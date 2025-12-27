"""
SSTable (Sorted String Table) implementation
Immutable on-disk file with index.
"""

import os
import struct
import mmap
import msgpack
from typing import Any, List, Tuple, Optional

class SSTable:
    """Sorted String Table"""

    def __init__(self, path: str):
        self.path = path
        self.index: List[Tuple[str, int]] = [] # Sparse index (Key, Offset)
        self.bloom_filter = set() # Simple set for now (Bloom Filter for Phase 2)

        if os.path.exists(path):
            self._load_index()

    def _load_index(self):
        """Load sparse index from file footer or separate file"""
        # For simplicity MVP: we verify the file exists and build index by scanning
        # In PROD: Read footer offset, read index block.
        # Here: We will build index on load (scan headers)

        with open(self.path, "rb") as f:
            offset = 0
            while True:
                # Seek to start (implicitly done by reads)
                try:
                    # Read KeyLen (4)
                    f.seek(offset)
                    header = f.read(4)
                    if not header: break

                    k_len = struct.unpack('I', header)[0]

                    # Read Key
                    key = f.read(k_len).decode('utf-8')
                    self.index.append((key, offset))
                    self.bloom_filter.add(key)

                    # Read ValLen (4)
                    v_len_bytes = f.read(4)
                    v_len = struct.unpack('I', v_len_bytes)[0]

                    # Skip value
                    offset += 4 + k_len + 4 + v_len
                except:
                    break

    @classmethod
    def write(cls, path: str, items: List[Tuple[str, Any]]):
        """Write sorted items to a new SSTable"""
        with open(path, "wb") as f:
            for key, value in items:
                k_bytes = key.encode('utf-8')
                v_bytes = msgpack.packb(value)

                # Format: KLen(4) + Key + VLen(4) + Value
                f.write(struct.pack('I', len(k_bytes)))
                f.write(k_bytes)
                f.write(struct.pack('I', len(v_bytes)))
                f.write(v_bytes)

        return cls(path)

    def get(self, key: str) -> Optional[Any]:
        """Search key in SSTable"""
        if key not in self.bloom_filter:
            return None

        # Binary search in sparse index (if we had blocks)
        # Here index has ALL keys (dense index in memory), so O(1)
        # Wait, having ALL keys in memory defeats the purpose of disk storage.
        # But for MVP it's fast.
        # For "Beat Python", we should use mmap + sparse index.
        # Let's fix _load_index to be sparse (every Nth key) and use block search?
        # Or simpler: For MVP, keep dense index but rely on mmap for value read.

        # Binary Search on index
        idx = self._binary_search_index(key)
        if idx is not None:
            offset = self.index[idx][1]
            return self._read_at(offset)
        return None

    def _binary_search_index(self, key: str) -> Optional[int]:
        """Binary search in in-memory index"""
        import bisect
        # self.index is list of (key, offset) sorted by key
        keys = [k for k, _ in self.index]
        i = bisect.bisect_left(keys, key)
        if i != len(keys) and keys[i] == key:
            return i
        return None

    def _read_at(self, offset: int) -> Any:
        """Read value at offset"""
        with open(self.path, "rb") as f:
            f.seek(offset)
            k_len = struct.unpack('I', f.read(4))[0]
            f.read(k_len) # Skip key
            v_len = struct.unpack('I', f.read(4))[0]
            v_bytes = f.read(v_len)
            return msgpack.unpackb(v_bytes)
