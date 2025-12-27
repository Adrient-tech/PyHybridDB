"""
File Storage Engine - Native storage backend with Caching and Indexing
"""

import json
import struct
from typing import Dict, Any, List, Optional
from pathlib import Path

from pyhybriddb.storage.file_manager import FileManager
from pyhybriddb.storage.index import BTreeIndex
from pyhybriddb.storage.base import BaseStorageEngine
from pyhybriddb.storage.cache import CacheManager


class FileStorageEngine(BaseStorageEngine):
    """Native storage engine for PyHybridDB with Caching"""

    BLOCK_HEADER_SIZE = 16  # Type (4) + Size (4) + Checksum (4) + Reserved (4)

    def __init__(self, db_path: str, cache_size: int = 5000):
        super().__init__()
        self.db_path = Path(db_path)
        self.file_manager = FileManager(db_path)
        self.indexes: Dict[str, Dict[str, BTreeIndex]] = {} # {container: {field: index}}
        self._transaction_log: List[Dict] = []
        self.cache = CacheManager(capacity=cache_size)

    def initialize(self):
        """Initialize a new database"""
        self.file_manager.create(metadata=self.metadata)
        self._write_metadata()

    def open(self):
        """Open existing database"""
        self.file_manager.open('r+b')
        self._load_metadata()
        self._rebuild_indexes()

    def close(self):
        """Close database and flush changes"""
        self._write_metadata()
        self.file_manager.close()

    def _write_metadata(self):
        """Write metadata to file"""
        metadata_json = json.dumps(self.metadata).encode('utf-8')
        block = self._create_block('META', metadata_json)

        # Write metadata at fixed offset after header
        self.file_manager.write_block(FileManager.HEADER_SIZE, block)

    def _load_metadata(self):
        """Load metadata from file"""
        try:
            block = self.file_manager.read_block(
                FileManager.HEADER_SIZE,
                1024 * 50  # Increased to 50KB for metadata
            )

            block_type, data = self._parse_block(block)
            if block_type == 'META':
                self.metadata = json.loads(data.decode('utf-8'))
        except Exception as e:
            # Initialize empty metadata if load fails
            self.metadata = {
                'tables': {},
                'collections': {},
                'indexes': {}
            }

    def _create_block(self, block_type: str, data: bytes) -> bytes:
        """Create a data block with header"""
        header = bytearray(self.BLOCK_HEADER_SIZE)

        # Block type (4 bytes)
        type_bytes = block_type.encode('utf-8')[:4].ljust(4, b'\x00')
        header[0:4] = type_bytes

        # Data size (4 bytes)
        struct.pack_into('I', header, 4, len(data))

        # Checksum (4 bytes) - simplified
        checksum = sum(data) % (2**32)
        struct.pack_into('I', header, 8, checksum)

        return bytes(header) + data

    def _parse_block(self, block: bytes) -> tuple:
        """Parse a data block"""
        if len(block) < self.BLOCK_HEADER_SIZE:
            raise ValueError("Invalid block size")

        block_type = block[0:4].decode('utf-8').strip('\x00')
        data_size = struct.unpack('I', block[4:8])[0]
        checksum = struct.unpack('I', block[8:12])[0]

        data = block[self.BLOCK_HEADER_SIZE:self.BLOCK_HEADER_SIZE + data_size]

        # Verify checksum
        calculated_checksum = sum(data) % (2**32)
        if calculated_checksum != checksum:
            raise ValueError("Block checksum mismatch")

        return block_type, data

    def insert_record(self, container_name: str, record: Dict[str, Any]) -> int:
        """Insert a record and return its ID"""
        record_json = json.dumps(record).encode('utf-8')
        block = self._create_block('DATA', record_json)

        offset = self.file_manager.append_block(block)

        # Update cache
        self.cache.put(str(offset), record)

        # Update indexes
        self._update_indexes(container_name, record, offset)

        # Update metadata offsets
        # TODO: This metadata update is O(N) over time for loading. Should be optimized.
        if container_name in self.metadata.get('tables', {}):
             if 'offsets' not in self.metadata['tables'][container_name]:
                 self.metadata['tables'][container_name]['offsets'] = []
             self.metadata['tables'][container_name]['offsets'].append(offset)
        elif container_name in self.metadata.get('collections', {}):
             if 'offsets' not in self.metadata['collections'][container_name]:
                 self.metadata['collections'][container_name]['offsets'] = []
             self.metadata['collections'][container_name]['offsets'].append(offset)

        # Log transaction
        self._log_transaction('INSERT', container_name, record)

        return offset

    def _update_indexes(self, container_name: str, record: Dict[str, Any], offset: int):
        """Update all indexes for a container"""
        if container_name not in self.indexes:
            return

        for field, index in self.indexes[container_name].items():
            value = record.get(field)
            if value is not None:
                # BTree requires comparable keys
                try:
                    index.insert(value, offset)
                except TypeError:
                    # Skip un-indexable types
                    pass

    def read_record(self, container_name: str, record_id: Any) -> Dict[str, Any]:
        """Read a record from offset"""
        offset = int(record_id)

        # Check cache first
        cached_record = self.cache.get(str(offset))
        if cached_record:
            return cached_record

        # Read block header first
        header = self.file_manager.read_block(offset, self.BLOCK_HEADER_SIZE)
        data_size = struct.unpack('I', header[4:8])[0]

        # Read full block
        block = self.file_manager.read_block(offset, self.BLOCK_HEADER_SIZE + data_size)
        block_type, data = self._parse_block(block)

        if block_type != 'DATA':
            raise ValueError(f"Expected DATA block, got {block_type}")

        record = json.loads(data.decode('utf-8'))

        # Populate cache
        self.cache.put(str(offset), record)

        return record

    def update_record(self, container_name: str, record_id: Any, record: Dict[str, Any]) -> int:
        """Update a record (creates new version)"""
        # Resolve record_id to offset if it's not one
        old_offset = self._resolve_id_to_offset(container_name, record_id)

        if old_offset is None:
            # Maybe record_id is already the offset?
            try:
                old_offset = int(record_id)
            except ValueError:
                # If we still can't find it, we can't update.
                # But to proceed with 'insert new version', we assume the old one is effectively gone or this is a weird case.
                pass

        # For simplicity, we append a new version (Append-Only)
        new_offset = self.insert_record(container_name, record) # This updates indexes too

        # Invalidate old cache
        if old_offset is not None:
            self.cache.invalidate(str(old_offset))

        # We need to remove old index entries?
        # A proper implementation would handle updates in BTree.
        # Here we rely on the container to manage 'offsets' list replacement.
        # But for indexes, we might have stale entries if we don't remove them.
        # TODO: Implement delete_from_index logic

        self._log_transaction('UPDATE', old_offset, record)

        return new_offset

    def delete_record(self, container_name: str, record_id: Any):
        """Delete a record (logical deletion)"""
        # In this simplistic append-only engine, 'delete' usually means
        # removing it from the metadata 'offsets' list (handled by Table/Collection class)
        # and invalidating cache.

        offset = self._resolve_id_to_offset(container_name, record_id)
        if offset is None:
             if isinstance(record_id, int):
                 offset = record_id

        if offset is not None:
            self.cache.invalidate(str(offset))

        # TODO: Remove from indexes

        self._log_transaction('DELETE', container_name, {'id': record_id})

    def _resolve_id_to_offset(self, container_name: str, record_id: Any) -> Optional[int]:
        """Resolve a record ID (uuid/int) to file offset using indexes"""
        # Try ID index first
        if container_name in self.indexes:
            if 'id' in self.indexes[container_name]:
                return self.indexes[container_name]['id'].search(record_id)
            if '_id' in self.indexes[container_name]:
                return self.indexes[container_name]['_id'].search(record_id)

        return None

    def create_index(self, container_name: str, field: str = 'id', order: int = 4):
        """Create an index for a specific field in a container"""
        if container_name not in self.indexes:
            self.indexes[container_name] = {}

        if field not in self.indexes[container_name]:
            self.indexes[container_name][field] = BTreeIndex(order)

            # Store index metadata
            if 'indexes' not in self.metadata:
                self.metadata['indexes'] = {}
            if container_name not in self.metadata['indexes']:
                self.metadata['indexes'][container_name] = {}

            self.metadata['indexes'][container_name][field] = {'order': order}

            # Populate index if data exists
            self._populate_index(container_name, field)

    def _populate_index(self, container_name: str, field: str):
        """Populate a newly created index"""
        offsets = []
        if container_name in self.metadata.get('tables', {}):
            offsets = self.metadata['tables'][container_name].get('offsets', [])
        elif container_name in self.metadata.get('collections', {}):
            offsets = self.metadata['collections'][container_name].get('offsets', [])

        index = self.indexes[container_name][field]

        for offset in offsets:
            try:
                record = self.read_record(container_name, offset)
                value = record.get(field)
                if value is not None:
                    try:
                        index.insert(value, offset)
                    except TypeError:
                        pass
            except Exception:
                continue

    def _rebuild_indexes(self):
        """Rebuild indexes from metadata"""
        for container, fields in self.metadata.get('indexes', {}).items():
            if container not in self.indexes:
                self.indexes[container] = {}

            for field, info in fields.items():
                order = info.get('order', 4)
                self.indexes[container][field] = BTreeIndex(order)
                # Note: We need to repopulate them!
                # This is slow on startup but necessary since we don't persist index to disk yet
                self._populate_index(container, field)

    def _log_transaction(self, operation: str, target: Any, data: Any):
        """Log transaction for ACID compliance"""
        self._transaction_log.append({
            'operation': operation,
            'target': target,
            'data': data
        })

    def commit(self):
        """Commit pending transactions"""
        # Write transaction log to file
        if self._transaction_log:
            log_data = json.dumps(self._transaction_log).encode('utf-8')
            block = self._create_block('TLOG', log_data)
            self.file_manager.append_block(block)
            self._transaction_log.clear()

    def rollback(self):
        """Rollback pending transactions"""
        self._transaction_log.clear()

    def scan_table(self, container_name: str) -> List[Dict[str, Any]]:
        """Scan all records in a table (full table scan)"""
        records = []

        offsets = []
        if container_name in self.metadata.get('tables', {}):
            offsets = self.metadata['tables'][container_name].get('offsets', [])
        elif container_name in self.metadata.get('collections', {}):
            offsets = self.metadata['collections'][container_name].get('offsets', [])

        for offset in offsets:
            try:
                record = self.read_record(container_name, offset)
                records.append(record)
            except Exception:
                continue

        return records

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            'file_size': self.file_manager.get_file_size(),
            'tables': len(self.metadata.get('tables', {})),
            'collections': len(self.metadata.get('collections', {})),
            'indexes': sum(len(fields) for fields in self.indexes.values()),
            'pending_transactions': len(self._transaction_log),
            'cache': self.cache.get_stats()
        }
