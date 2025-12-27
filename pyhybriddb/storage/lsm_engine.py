"""
LSM Storage Engine
Coordinates MemTable and SSTables.
"""

import os
import glob
from typing import Any, Dict, List, Optional
from pathlib import Path

from pyhybriddb.storage.base import BaseStorageEngine
from pyhybriddb.storage.lsm.memtable import MemTable
from pyhybriddb.storage.lsm.sstable import SSTable

class LSMStorageEngine(BaseStorageEngine):
    """Log-Structured Merge Tree Storage Engine"""

    def __init__(self, db_path: str, memtable_size: int = 1000):
        super().__init__()
        self.db_path = Path(db_path)
        self.wal_path = self.db_path / "wal.log"
        self.memtable_capacity = memtable_size
        # Create dummy memtable or delay?
        # Creating MemTable opens WAL immediately, which requires directory.
        # So we defer creation to open/initialize
        self.memtable = None
        self.sstables: List[SSTable] = []
        # QueryProcessor expects indexes dict
        self.indexes: Dict[str, Dict[str, Any]] = {}
        # Table/Collection expects metadata
        self.metadata = {
            'tables': {},
            'collections': {},
            'indexes': {}
        }

    def initialize(self):
        """Initialize"""
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.memtable = MemTable(str(self.wal_path), capacity=self.memtable_capacity)
        self._load_sstables()

    def open(self):
        """Open"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"DB not found: {self.db_path}")
        self.memtable = MemTable(str(self.wal_path), capacity=self.memtable_capacity)
        self._load_sstables()
        self.memtable.recover()

    def close(self):
        """Close"""
        # Flush memtable on close? (Optional, WAL handles recovery)
        # self._flush_memtable()
        self.memtable.wal.close()

    def _load_sstables(self):
        """Load existing SSTables"""
        files = sorted(glob.glob(str(self.db_path / "*.sst")), reverse=True) # Newest first
        self.sstables = [SSTable(f) for f in files]

    def _flush_memtable(self):
        """Flush MemTable to SSTable"""
        if self.memtable.size == 0:
            return

        filename = f"{len(self.sstables):06d}.sst"
        path = str(self.db_path / filename)

        items = self.memtable.flush()

        # Try using optimized Cython writer
        try:
            from pyhybriddb.storage.lsm.optimized import write_sstable_fast
            import msgpack
            # Cython needs (key, packed_value)
            packed_items = [(k, msgpack.packb(v)) for k, v in items]
            write_sstable_fast(path, packed_items)
            new_sstable = SSTable(path)
        except ImportError:
            new_sstable = SSTable.write(path, items)

        # Add to list (Newest first for search)
        self.sstables.insert(0, new_sstable)

    def insert_record(self, container_name: str, record: Dict[str, Any]) -> Any:
        """Insert a record"""
        # LSM is Key-Value. We need to define a Key.
        # Container is prefix?
        # e.g. "users:123"

        if 'id' in record:
            rec_id = record['id']
            key = f"{container_name}:{rec_id}"
        elif '_id' in record:
            rec_id = record['_id']
            key = f"{container_name}:{rec_id}"
        else:
            # Generate ID? For now assume ID provided or use auto-inc handled by Table class
            # But Table class expects an int ID returned.
            # Here we just return the key we used?
            # Or we let the Table class handle ID generation and we just store it.
             raise ValueError("Record must have 'id' or '_id'")

        self.memtable.put(key, record)

        # Track offsets for Table/Collection count (simulated)
        # LSM doesn't use file offsets the same way, but higher levels rely on 'offsets' list length for count
        if container_name in self.metadata['tables']:
            if rec_id not in self.metadata['tables'][container_name]['offsets']:
                self.metadata['tables'][container_name]['offsets'].append(rec_id)
        elif container_name in self.metadata['collections']:
            if rec_id not in self.metadata['collections'][container_name]['offsets']:
                self.metadata['collections'][container_name]['offsets'].append(rec_id)

        if self.memtable.is_full():
            self._flush_memtable()

        return rec_id

    def read_record(self, container_name: str, record_id: Any) -> Dict[str, Any]:
        """Read a record"""
        key = f"{container_name}:{record_id}"

        # 1. Check MemTable
        val = self.memtable.get(key)
        if val is not None:
             if val is None: # Tombstone
                 raise KeyError("Record deleted")
             return val

        # 2. Check SSTables (Newest to Oldest)
        for sst in self.sstables:
            val = sst.get(key)
            if val is not None:
                if val is None: # Tombstone (Wait, we stored None in Msgpack?)
                    # Msgpack handles None.
                    raise KeyError("Record deleted")
                return val

        raise KeyError(f"Record {record_id} not found")

    def update_record(self, container_name: str, record_id: Any, record: Dict[str, Any]) -> Any:
        """Update"""
        return self.insert_record(container_name, record)

    def delete_record(self, container_name: str, record_id: Any):
        """Delete"""
        key = f"{container_name}:{record_id}"
        self.memtable.delete(key)

        # Remove from simulated metadata
        if container_name in self.metadata['tables']:
            if record_id in self.metadata['tables'][container_name]['offsets']:
                self.metadata['tables'][container_name]['offsets'].remove(record_id)
        elif container_name in self.metadata['collections']:
             if record_id in self.metadata['collections'][container_name]['offsets']:
                self.metadata['collections'][container_name]['offsets'].remove(record_id)

        if self.memtable.is_full():
            self._flush_memtable()

    # Stub implementations for BaseStorageEngine abstract methods
    def create_index(self, container_name: str, order: int = 4):
        pass # LSM is primary key index only for now

    def scan_table(self, container_name: str) -> List[Dict[str, Any]]:
        """Scan table"""
        # Merge sort iterator over MemTable and all SSTables
        # This is complex. For MVP, we just iterate everything and filter by prefix.
        results = {}
        prefix = f"{container_name}:"

        # Process oldest SSTables first, then MemTable (to overwrite)
        for sst in reversed(self.sstables):
            for key, offset in sst.index:
                if key.startswith(prefix):
                    val = sst._read_at(offset)
                    if val is not None:
                        results[key] = val
                    else:
                        results.pop(key, None)

        # MemTable
        for key, val in self.memtable.data.items():
             if key.startswith(prefix):
                 if val is not None:
                     results[key] = val
                 else:
                     results.pop(key, None)

        return list(results.values())

    def commit(self):
        pass # WAL handles it

    def rollback(self):
        pass # Not supported yet

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "memtable_size": self.memtable.size,
            "sstables": len(self.sstables)
        }
