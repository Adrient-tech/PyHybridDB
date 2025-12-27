"""
MemTable implementation
In-memory sorted storage (SkipList or RBTree ideally, using Dict + Sort for MVP)
"""

from typing import Any, Dict, List, Tuple
from pyhybriddb.storage.lsm.wal import WAL

class MemTable:
    """In-memory table"""

    def __init__(self, wal_path: str, capacity: int = 1000):
        self.capacity = capacity
        self.data: Dict[str, Any] = {}
        self.wal = WAL(wal_path)
        self.size = 0

    def put(self, key: str, value: Any):
        """Insert/Update key"""
        self.wal.append(key, value)
        self.data[key] = value
        self.size += 1

    def get(self, key: str) -> Any:
        """Get value by key"""
        return self.data.get(key)

    def delete(self, key: str):
        """Delete key (tombstone)"""
        # We store None as tombstone
        self.put(key, None)

    def is_full(self) -> bool:
        """Check if MemTable is full"""
        return len(self.data) >= self.capacity

    def flush(self) -> List[Tuple[str, Any]]:
        """Return sorted items and clear"""
        # Sort by key
        sorted_items = sorted(self.data.items())

        # Clear
        self.data.clear()
        self.wal.clear()
        self.size = 0

        return sorted_items

    def recover(self):
        """Recover from WAL"""
        entries = WAL.recover(self.wal.path)
        for k, v in entries:
            self.data[k] = v
