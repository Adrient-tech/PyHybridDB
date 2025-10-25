"""
PostgreSQL to PyHybridDB migration tool
"""

from typing import Dict, List, Any, Optional
import json


class PostgreSQLMigration:
    """Migrate data from PostgreSQL to PyHybridDB"""
    
    def __init__(self, pg_config: Dict[str, str]):
        """
        Initialize PostgreSQL connection
        
        Args:
            pg_config: {
                'host': 'localhost',
                'port': 5432,
                'database': 'mydb',
                'user': 'postgres',
                'password': 'password'
            }
        """
        self.pg_config = pg_config
        self.connection = None
    
    def connect(self):
        """Connect to PostgreSQL"""
        try:
            import psycopg2
            self.connection = psycopg2.connect(**self.pg_config)
            return True
        except ImportError:
            raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")
    
    def get_tables(self) -> List[str]:
        """Get list of tables in PostgreSQL database"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        return tables
    
    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """Get table schema"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table_name,))
        
        schema = {}
        type_mapping = {
            'integer': 'integer',
            'bigint': 'integer',
            'smallint': 'integer',
            'numeric': 'float',
            'real': 'float',
            'double precision': 'float',
            'character varying': 'string',
            'character': 'string',
            'text': 'string',
            'boolean': 'boolean',
            'date': 'string',
            'timestamp': 'string',
            'json': 'string',
            'jsonb': 'string'
        }
        
        for column_name, data_type in cursor.fetchall():
            phdb_type = type_mapping.get(data_type.lower(), 'string')
            schema[column_name] = phdb_type
        
        cursor.close()
        return schema
    
    def get_table_data(self, table_name: str, limit: Optional[int] = None) -> List[Dict]:
        """Get all data from a table"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        data = []
        for row in rows:
            record = {}
            for i, value in enumerate(row):
                # Convert special types
                if value is not None:
                    if isinstance(value, (list, dict)):
                        record[columns[i]] = json.dumps(value)
                    else:
                        record[columns[i]] = value
                else:
                    record[columns[i]] = None
            data.append(record)
        
        cursor.close()
        return data
    
    def migrate_table(self, table_name: str, target_db, progress_callback=None) -> int:
        """
        Migrate a single table to PyHybridDB
        
        Args:
            table_name: PostgreSQL table name
            target_db: PyHybridDB Database instance
            progress_callback: Optional callback function(current, total)
        
        Returns:
            Number of records migrated
        """
        # Get schema
        schema = self.get_table_schema(table_name)
        
        # Create table in PyHybridDB
        target_table = target_db.create_table(table_name, schema)
        
        # Get data
        data = self.get_table_data(table_name)
        
        # Insert data
        total = len(data)
        for i, record in enumerate(data):
            target_table.insert(record)
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return total
    
    def migrate_database(self, target_db, tables: Optional[List[str]] = None, 
                        progress_callback=None) -> Dict[str, int]:
        """
        Migrate entire database or specific tables
        
        Args:
            target_db: PyHybridDB Database instance
            tables: List of table names to migrate (None = all tables)
            progress_callback: Optional callback function(table, current, total)
        
        Returns:
            Dictionary of table_name: record_count
        """
        if tables is None:
            tables = self.get_tables()
        
        results = {}
        
        for table_name in tables:
            def table_progress(current, total):
                if progress_callback:
                    progress_callback(table_name, current, total)
            
            count = self.migrate_table(table_name, target_db, table_progress)
            results[table_name] = count
        
        return results
    
    def close(self):
        """Close PostgreSQL connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
