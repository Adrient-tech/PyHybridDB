"""
Storage Engine - Main interface for data persistence
Manages both structured and unstructured data storage
"""

import json
import struct
from typing import Dict, Any, List, Optional
from pathlib import Path

from pyhybriddb.storage.file_manager import FileManager
from pyhybriddb.storage.index import BTreeIndex


class StorageEngine:
    """Main storage engine for PyHybridDB"""
    
    BLOCK_HEADER_SIZE = 16  # Type (4) + Size (4) + Checksum (4) + Reserved (4)
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.file_manager = FileManager(db_path)
        self.indexes: Dict[str, BTreeIndex] = {}
        self.metadata: Dict[str, Any] = {
            'tables': {},
            'collections': {},
            'indexes': {}
        }
        self._transaction_log: List[Dict] = []
        
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
                1024 * 10  # Read up to 10KB for metadata
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
    
    def insert_record(self, table_name: str, record: Dict[str, Any]) -> int:
        """Insert a record and return its ID"""
        record_json = json.dumps(record).encode('utf-8')
        block = self._create_block('DATA', record_json)
        
        offset = self.file_manager.append_block(block)
        
        # Update index if exists
        if table_name in self.indexes:
            record_id = record.get('id', offset)
            self.indexes[table_name].insert(record_id, offset)
        
        # Log transaction
        self._log_transaction('INSERT', table_name, record)
        
        return offset
    
    def read_record(self, offset: int) -> Dict[str, Any]:
        """Read a record from offset"""
        # Read block header first
        header = self.file_manager.read_block(offset, self.BLOCK_HEADER_SIZE)
        data_size = struct.unpack('I', header[4:8])[0]
        
        # Read full block
        block = self.file_manager.read_block(offset, self.BLOCK_HEADER_SIZE + data_size)
        block_type, data = self._parse_block(block)
        
        if block_type != 'DATA':
            raise ValueError(f"Expected DATA block, got {block_type}")
        
        return json.loads(data.decode('utf-8'))
    
    def update_record(self, offset: int, record: Dict[str, Any]) -> int:
        """Update a record (creates new version)"""
        # For simplicity, we append a new version
        new_offset = self.insert_record('_updates', record)
        
        # Mark old record as deleted (in production, would use tombstone)
        self._log_transaction('UPDATE', offset, record)
        
        return new_offset
    
    def delete_record(self, table_name: str, record_id: Any):
        """Delete a record (logical deletion)"""
        if table_name in self.indexes:
            offset = self.indexes[table_name].search(record_id)
            if offset:
                self._log_transaction('DELETE', table_name, {'id': record_id})
                self.indexes[table_name].delete(record_id)
    
    def create_index(self, table_name: str, order: int = 4):
        """Create an index for a table"""
        if table_name not in self.indexes:
            self.indexes[table_name] = BTreeIndex(order)
            self.metadata['indexes'][table_name] = {'order': order}
    
    def _rebuild_indexes(self):
        """Rebuild indexes from metadata"""
        for table_name, index_info in self.metadata.get('indexes', {}).items():
            order = index_info.get('order', 4)
            self.indexes[table_name] = BTreeIndex(order)
    
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
    
    def scan_table(self, table_name: str) -> List[Dict[str, Any]]:
        """Scan all records in a table (full table scan)"""
        records = []
        
        # This is a simplified implementation
        # In production, would maintain table metadata with record offsets
        if table_name in self.metadata.get('tables', {}):
            table_info = self.metadata['tables'][table_name]
            for offset in table_info.get('offsets', []):
                try:
                    record = self.read_record(offset)
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
            'indexes': len(self.indexes),
            'pending_transactions': len(self._transaction_log)
        }
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
