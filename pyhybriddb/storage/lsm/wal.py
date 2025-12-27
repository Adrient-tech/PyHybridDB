"""
Write-Ahead Log (WAL) implementation
Ensures durability by appending operations to disk before applying to MemTable.
"""

import os
import struct
import msgpack
from typing import Any, Tuple, Optional

class WAL:
    """Write-Ahead Log"""

    def __init__(self, path: str):
        self.path = path
        self.file = open(path, "ab")
        self.offset = 0

    def append(self, key: str, value: Any) -> int:
        """Append a key-value pair to the log"""
        # Format: KeyLen(4) + ValLen(4) + Key + Value
        key_bytes = key.encode('utf-8')
        val_bytes = msgpack.packb(value)

        entry = struct.pack('II', len(key_bytes), len(val_bytes)) + key_bytes + val_bytes
        self.file.write(entry)
        self.file.flush() # Ensure it hits disk

        written_len = len(entry)
        current_offset = self.offset
        self.offset += written_len
        return current_offset

    def close(self):
        """Close the WAL"""
        self.file.close()

    def clear(self):
        """Clear the WAL (after flush)"""
        self.file.close()
        self.file = open(self.path, "wb")
        self.file.close()
        self.file = open(self.path, "ab")
        self.offset = 0

    @classmethod
    def recover(cls, path: str) -> list[Tuple[str, Any]]:
        """Recover entries from WAL"""
        entries = []
        if not os.path.exists(path):
            return entries

        with open(path, "rb") as f:
            while True:
                header = f.read(8)
                if not header or len(header) < 8:
                    break

                k_len, v_len = struct.unpack('II', header)
                key = f.read(k_len).decode('utf-8')
                val_bytes = f.read(v_len)
                value = msgpack.unpackb(val_bytes)

                entries.append((key, value))
        return entries
