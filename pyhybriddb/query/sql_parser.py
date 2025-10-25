"""
SQL Parser - Parse and execute SQL queries
"""

import re
import sqlparse
from typing import Any, Dict, List, Optional
from pyhybriddb.core.database import Database


class SQLParser:
    """SQL query parser and executor"""
    
    def __init__(self, database: Database):
        self.database = database
    
    def parse_and_execute(self, query: str) -> Any:
        """Parse and execute SQL query"""
        # Parse SQL using sqlparse
        parsed = sqlparse.parse(query)[0]
        statement_type = parsed.get_type()
        
        if statement_type == 'SELECT':
            return self._execute_select(query)
        elif statement_type == 'INSERT':
            return self._execute_insert(query)
        elif statement_type == 'UPDATE':
            return self._execute_update(query)
        elif statement_type == 'DELETE':
            return self._execute_delete(query)
        elif statement_type == 'CREATE':
            return self._execute_create(query)
        elif statement_type == 'DROP':
            return self._execute_drop(query)
        else:
            raise ValueError(f"Unsupported SQL statement: {statement_type}")
    
    def _execute_select(self, query: str) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        # Simple regex-based parsing for basic SELECT
        match = re.match(
            r'SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?',
            query,
            re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        columns = match.group(1).strip()
        table_name = match.group(2).strip()
        where_clause = match.group(3)
        
        # Get table
        table = self.database.get_table(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")
        
        # Parse WHERE clause
        where_dict = self._parse_where_clause(where_clause) if where_clause else None
        
        # Execute select
        results = table.select(where_dict)
        
        # Apply column projection
        if columns != '*':
            col_list = [c.strip() for c in columns.split(',')]
            results = [{col: row.get(col) for col in col_list} for row in results]
        
        return results
    
    def _execute_insert(self, query: str) -> int:
        """Execute INSERT query"""
        # Parse INSERT INTO table (columns) VALUES (values)
        match = re.match(
            r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)',
            query,
            re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1).strip()
        columns = [c.strip() for c in match.group(2).split(',')]
        values = [self._parse_value(v.strip()) for v in match.group(3).split(',')]
        
        # Get table
        table = self.database.get_table(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")
        
        # Create record
        record = dict(zip(columns, values))
        
        return table.insert(record)
    
    def _execute_update(self, query: str) -> int:
        """Execute UPDATE query"""
        # Parse UPDATE table SET col=val WHERE condition
        match = re.match(
            r'UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?',
            query,
            re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1).strip()
        set_clause = match.group(2).strip()
        where_clause = match.group(3)
        
        # Get table
        table = self.database.get_table(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")
        
        # Parse SET clause
        updates = self._parse_set_clause(set_clause)
        
        # Parse WHERE clause
        where_dict = self._parse_where_clause(where_clause) if where_clause else {}
        
        return table.update(where_dict, updates)
    
    def _execute_delete(self, query: str) -> int:
        """Execute DELETE query"""
        # Parse DELETE FROM table WHERE condition
        match = re.match(
            r'DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?',
            query,
            re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1).strip()
        where_clause = match.group(2)
        
        # Get table
        table = self.database.get_table(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")
        
        # Parse WHERE clause
        where_dict = self._parse_where_clause(where_clause) if where_clause else {}
        
        return table.delete(where_dict)
    
    def _execute_create(self, query: str) -> str:
        """Execute CREATE TABLE query"""
        # Parse CREATE TABLE table (col type, ...)
        match = re.match(
            r'CREATE\s+TABLE\s+(\w+)\s*\(([^)]+)\)',
            query,
            re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1).strip()
        columns_def = match.group(2).strip()
        
        # Parse column definitions
        schema = {}
        for col_def in columns_def.split(','):
            parts = col_def.strip().split()
            if len(parts) >= 2:
                col_name = parts[0]
                col_type = parts[1]
                schema[col_name] = col_type
        
        self.database.create_table(table_name, schema)
        return f"Table '{table_name}' created"
    
    def _execute_drop(self, query: str) -> str:
        """Execute DROP TABLE query"""
        match = re.match(
            r'DROP\s+TABLE\s+(\w+)',
            query,
            re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Invalid DROP TABLE syntax")
        
        table_name = match.group(1).strip()
        self.database.drop_table(table_name)
        return f"Table '{table_name}' dropped"
    
    def _parse_where_clause(self, where: str) -> Dict[str, Any]:
        """Parse WHERE clause into dictionary"""
        conditions = {}
        
        # Simple parsing for col=val AND col=val
        parts = re.split(r'\s+AND\s+', where, flags=re.IGNORECASE)
        
        for part in parts:
            match = re.match(r'(\w+)\s*=\s*(.+)', part.strip())
            if match:
                col = match.group(1)
                val = self._parse_value(match.group(2))
                conditions[col] = val
        
        return conditions
    
    def _parse_set_clause(self, set_clause: str) -> Dict[str, Any]:
        """Parse SET clause into dictionary"""
        updates = {}
        
        parts = set_clause.split(',')
        for part in parts:
            match = re.match(r'(\w+)\s*=\s*(.+)', part.strip())
            if match:
                col = match.group(1)
                val = self._parse_value(match.group(2))
                updates[col] = val
        
        return updates
    
    def _parse_value(self, value: str) -> Any:
        """Parse a value string into appropriate Python type"""
        value = value.strip()
        
        # String (quoted)
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            return value[1:-1]
        
        # Number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # Boolean
        if value.upper() == 'TRUE':
            return True
        if value.upper() == 'FALSE':
            return False
        
        # NULL
        if value.upper() == 'NULL':
            return None
        
        return value
