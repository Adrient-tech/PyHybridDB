"""
File Manager for .phdb file format
Handles low-level file I/O operations
"""

import os
import struct
import json
from typing import Dict, Any, Optional
from pathlib import Path


class FileManager:
    """Manages .phdb file operations"""
    
    MAGIC_NUMBER = b'PHDB'
    VERSION = 1
    HEADER_SIZE = 64
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.file_handle = None
        self._ensure_extension()
        
    def _ensure_extension(self):
        """Ensure file has .phdb extension"""
        if self.filepath.suffix != '.phdb':
            self.filepath = self.filepath.with_suffix('.phdb')
    
    def create(self, metadata: Optional[Dict[str, Any]] = None):
        """Create a new .phdb file with header"""
        if self.filepath.exists():
            raise FileExistsError(f"Database file already exists: {self.filepath}")
        
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.filepath, 'wb') as f:
            # Write header
            header = self._create_header(metadata or {})
            f.write(header)
            
    def _create_header(self, metadata: Dict[str, Any]) -> bytes:
        """Create file header with metadata"""
        header = bytearray(self.HEADER_SIZE)
        
        # Magic number (4 bytes)
        header[0:4] = self.MAGIC_NUMBER
        
        # Version (4 bytes)
        struct.pack_into('I', header, 4, self.VERSION)
        
        # Metadata length (4 bytes) - reserved for future use
        metadata_json = json.dumps(metadata).encode('utf-8')
        struct.pack_into('I', header, 8, len(metadata_json))
        
        # Reserved space (52 bytes)
        
        return bytes(header)
    
    def open(self, mode='rb'):
        """Open the database file"""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Database file not found: {self.filepath}")
        
        self.file_handle = open(self.filepath, mode)
        self._validate_header()
        return self.file_handle
    
    def _validate_header(self):
        """Validate file header"""
        if self.file_handle is None:
            return
        
        self.file_handle.seek(0)
        magic = self.file_handle.read(4)
        
        if magic != self.MAGIC_NUMBER:
            raise ValueError("Invalid database file format")
        
        version = struct.unpack('I', self.file_handle.read(4))[0]
        if version != self.VERSION:
            raise ValueError(f"Unsupported database version: {version}")
    
    def close(self):
        """Close the file handle"""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
    
    def write_block(self, offset: int, data: bytes):
        """Write a data block at specified offset"""
        if self.file_handle is None:
            self.open('r+b')
        
        self.file_handle.seek(offset)
        self.file_handle.write(data)
        self.file_handle.flush()
    
    def read_block(self, offset: int, size: int) -> bytes:
        """Read a data block from specified offset"""
        if self.file_handle is None:
            self.open('rb')
        
        self.file_handle.seek(offset)
        return self.file_handle.read(size)
    
    def append_block(self, data: bytes) -> int:
        """Append data block and return offset"""
        if self.file_handle is None:
            self.open('r+b')
        
        self.file_handle.seek(0, os.SEEK_END)
        offset = self.file_handle.tell()
        self.file_handle.write(data)
        self.file_handle.flush()
        return offset
    
    def get_file_size(self) -> int:
        """Get current file size"""
        return self.filepath.stat().st_size if self.filepath.exists() else 0
    
    def __enter__(self):
        self.open('r+b')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
