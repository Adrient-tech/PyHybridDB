"""
Table - Structured data with schema (SQL-like)
"""

from typing import Dict, Any, List, Optional
from pyhybriddb.storage.engine import StorageEngine


class Table:
    """Represents a structured table with schema"""
    
    def __init__(self, name: str, schema: Dict[str, str], storage_engine: StorageEngine):
        self.name = name
        self.schema = schema  # {column_name: data_type}
        self.storage_engine = storage_engine
        self._auto_increment_id = 0
    
    def insert(self, record: Dict[str, Any]) -> int:
        """Insert a record into the table"""
        # Validate against schema
        self._validate_record(record)
        
        # Add auto-increment ID if not present
        if 'id' not in record:
            self._auto_increment_id += 1
            record['id'] = self._auto_increment_id
        
        # Store record
        offset = self.storage_engine.insert_record(self.name, record)
        
        # Update table metadata
        if self.name in self.storage_engine.metadata['tables']:
            self.storage_engine.metadata['tables'][self.name]['offsets'].append(offset)
        
        return record['id']
    
    def _validate_record(self, record: Dict[str, Any]):
        """Validate record against schema"""
        for column, value in record.items():
            if column not in self.schema and column != 'id':
                raise ValueError(f"Column '{column}' not in schema")
            
            # Basic type checking
            expected_type = self.schema.get(column)
            if expected_type and not self._check_type(value, expected_type):
                raise TypeError(f"Column '{column}' expected {expected_type}, got {type(value).__name__}")
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_map = {
            'int': int,
            'integer': int,
            'str': str,
            'string': str,
            'float': float,
            'bool': bool,
            'boolean': bool,
        }
        
        python_type = type_map.get(expected_type.lower())
        if python_type:
            return isinstance(value, python_type)
        
        return True  # Unknown types pass validation
    
    def select(self, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Select records from table"""
        results = []
        
        # Get all offsets for this table
        table_info = self.storage_engine.metadata['tables'].get(self.name, {})
        offsets = table_info.get('offsets', [])
        
        for offset in offsets:
            try:
                record = self.storage_engine.read_record(offset)
                
                # Apply where clause
                if where is None or self._matches_where(record, where):
                    results.append(record)
            except Exception:
                continue
        
        return results
    
    def _matches_where(self, record: Dict[str, Any], where: Dict[str, Any]) -> bool:
        """Check if record matches where clause"""
        for key, value in where.items():
            if key not in record or record[key] != value:
                return False
        return True
    
    def update(self, where: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """Update records matching where clause"""
        count = 0
        table_info = self.storage_engine.metadata['tables'].get(self.name, {})
        offsets = table_info.get('offsets', [])
        
        for i, offset in enumerate(offsets):
            try:
                record = self.storage_engine.read_record(offset)
                
                if self._matches_where(record, where):
                    # Apply updates
                    record.update(updates)
                    self._validate_record(record)
                    
                    # Write updated record
                    new_offset = self.storage_engine.update_record(offset, record)
                    offsets[i] = new_offset
                    count += 1
            except Exception:
                continue
        
        return count
    
    def delete(self, where: Dict[str, Any]) -> int:
        """Delete records matching where clause"""
        count = 0
        table_info = self.storage_engine.metadata['tables'].get(self.name, {})
        offsets = table_info.get('offsets', [])
        new_offsets = []
        
        for offset in offsets:
            try:
                record = self.storage_engine.read_record(offset)
                
                if self._matches_where(record, where):
                    # Mark for deletion
                    self.storage_engine.delete_record(self.name, record.get('id'))
                    count += 1
                else:
                    new_offsets.append(offset)
            except Exception:
                new_offsets.append(offset)
        
        # Update offsets
        table_info['offsets'] = new_offsets
        
        return count
    
    def count(self) -> int:
        """Count records in table"""
        table_info = self.storage_engine.metadata['tables'].get(self.name, {})
        return len(table_info.get('offsets', []))
    
    def describe(self) -> Dict[str, Any]:
        """Describe table schema"""
        return {
            'name': self.name,
            'schema': self.schema,
            'record_count': self.count()
        }
    
    def __repr__(self):
        return f"Table(name='{self.name}', columns={list(self.schema.keys())})"
