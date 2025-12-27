"""
Table - Structured data with schema (SQL-like)
"""

from typing import Dict, Any, List, Optional
from pyhybriddb.storage.base import BaseStorageEngine
from pyhybriddb.query.processor import QueryProcessor

class Table:
    """Represents a structured table with schema"""
    
    def __init__(self, name: str, schema: Dict[str, str], storage_engine: BaseStorageEngine):
        self.name = name
        self.schema = schema  # {column_name: data_type}
        self.storage_engine = storage_engine
        self.query_processor = QueryProcessor(storage_engine)
        self._auto_increment_id = 0

        # Always index ID
        self.storage_engine.create_index(name, 'id')
    
    def insert(self, record: Dict[str, Any]) -> int:
        """Insert a record into the table"""
        # Validate against schema
        self._validate_record(record)
        
        # Add auto-increment ID if not present
        if 'id' not in record:
            self._auto_increment_id += 1
            record['id'] = self._auto_increment_id
        else:
            # Update auto increment if user provided id is higher
            if isinstance(record['id'], int) and record['id'] > self._auto_increment_id:
                self._auto_increment_id = record['id']
        
        # Store record
        self.storage_engine.insert_record(self.name, record)
        
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
        if where is None:
            return self.storage_engine.scan_table(self.name)

        return self.query_processor.execute(self.name, where)
    
    def update(self, where: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """Update records matching where clause"""
        # We need offsets to update properly in metadata list
        # select() returns copies of records.
        # We need to access storage engine scan to find offsets or use index lookup + verification

        # Simpler approach: Iterate all offsets, check condition, update if match
        count = 0
        table_info = self.storage_engine.metadata['tables'].get(self.name, {})
        offsets = table_info.get('offsets', [])
        
        for i, offset in enumerate(offsets):
            try:
                record = self.storage_engine.read_record(self.name, offset)
                # Check if matches 'where'
                # Use query processor logic or simple check
                if self.query_processor._matches_query(record, where):
                     record.update(updates)
                     self._validate_record(record)
                     new_offset = self.storage_engine.update_record(self.name, record['id'], record)
                     offsets[i] = new_offset
                     count += 1
            except:
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
                record = self.storage_engine.read_record(self.name, offset)
                if self.query_processor._matches_query(record, where):
                     self.storage_engine.delete_record(self.name, record['id'])
                     count += 1
                else:
                    new_offsets.append(offset)
            except:
                new_offsets.append(offset)
        
        table_info['offsets'] = new_offsets
        return count
    
    def create_index(self, column: str):
        """Create an index on a column"""
        if column in self.schema or column == 'id':
            self.storage_engine.create_index(self.name, column)
        else:
            raise ValueError(f"Column {column} not in schema")

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
