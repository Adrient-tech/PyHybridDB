"""
Database - Main database interface
Manages tables and collections
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from pyhybriddb.storage.engine import StorageEngine
from pyhybriddb.core.table import Table
from pyhybriddb.core.collection import Collection


class Database:
    """Main database class"""
    
    def __init__(self, name: str, path: Optional[str] = None):
        self.name = name
        self.path = Path(path) if path else Path.cwd() / 'data'
        self.db_file = self.path / f"{name}.phdb"
        
        self.storage_engine: Optional[StorageEngine] = None
        self.tables: Dict[str, Table] = {}
        self.collections: Dict[str, Collection] = {}
        self._is_open = False
    
    def create(self):
        """Create a new database"""
        self.path.mkdir(parents=True, exist_ok=True)
        
        self.storage_engine = StorageEngine(str(self.db_file))
        self.storage_engine.initialize()
        self._is_open = True
        
        return self
    
    def open(self):
        """Open an existing database"""
        if not self.db_file.exists():
            raise FileNotFoundError(f"Database not found: {self.db_file}")
        
        self.storage_engine = StorageEngine(str(self.db_file))
        self.storage_engine.open()
        self._is_open = True
        
        # Load existing tables and collections
        self._load_schema()
        
        return self
    
    def close(self):
        """Close the database"""
        if self.storage_engine and self._is_open:
            self.storage_engine.close()
            self._is_open = False
    
    def _load_schema(self):
        """Load tables and collections from metadata"""
        if not self.storage_engine:
            return
        
        metadata = self.storage_engine.metadata
        
        # Load tables
        for table_name, table_info in metadata.get('tables', {}).items():
            self.tables[table_name] = Table(
                name=table_name,
                schema=table_info.get('schema', {}),
                storage_engine=self.storage_engine
            )
        
        # Load collections
        for coll_name, coll_info in metadata.get('collections', {}).items():
            self.collections[coll_name] = Collection(
                name=coll_name,
                storage_engine=self.storage_engine
            )
    
    def create_table(self, name: str, schema: Dict[str, str]) -> Table:
        """Create a new table with schema"""
        if not self._is_open:
            raise RuntimeError("Database is not open")
        
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        
        table = Table(name=name, schema=schema, storage_engine=self.storage_engine)
        self.tables[name] = table
        
        # Update metadata
        self.storage_engine.metadata['tables'][name] = {
            'schema': schema,
            'offsets': []
        }
        self.storage_engine.create_index(name)
        
        return table
    
    def create_collection(self, name: str) -> Collection:
        """Create a new collection (schema-less)"""
        if not self._is_open:
            raise RuntimeError("Database is not open")
        
        if name in self.collections:
            raise ValueError(f"Collection '{name}' already exists")
        
        collection = Collection(name=name, storage_engine=self.storage_engine)
        self.collections[name] = collection
        
        # Update metadata
        self.storage_engine.metadata['collections'][name] = {
            'offsets': []
        }
        self.storage_engine.create_index(name)
        
        return collection
    
    def get_table(self, name: str) -> Optional[Table]:
        """Get a table by name"""
        return self.tables.get(name)
    
    def get_collection(self, name: str) -> Optional[Collection]:
        """Get a collection by name"""
        return self.collections.get(name)
    
    def drop_table(self, name: str):
        """Drop a table"""
        if name in self.tables:
            del self.tables[name]
            if name in self.storage_engine.metadata['tables']:
                del self.storage_engine.metadata['tables'][name]
    
    def drop_collection(self, name: str):
        """Drop a collection"""
        if name in self.collections:
            del self.collections[name]
            if name in self.storage_engine.metadata['collections']:
                del self.storage_engine.metadata['collections'][name]
    
    def list_tables(self) -> List[str]:
        """List all table names"""
        return list(self.tables.keys())
    
    def list_collections(self) -> List[str]:
        """List all collection names"""
        return list(self.collections.keys())
    
    def commit(self):
        """Commit pending changes"""
        if self.storage_engine:
            self.storage_engine.commit()
    
    def rollback(self):
        """Rollback pending changes"""
        if self.storage_engine:
            self.storage_engine.rollback()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.storage_engine:
            return {}
        
        stats = self.storage_engine.get_statistics()
        stats.update({
            'name': self.name,
            'path': str(self.db_file),
            'is_open': self._is_open,
            'table_count': len(self.tables),
            'collection_count': len(self.collections)
        })
        
        return stats
    
    def __enter__(self):
        if not self._is_open:
            if self.db_file.exists():
                self.open()
            else:
                self.create()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __repr__(self):
        return f"Database(name='{self.name}', tables={len(self.tables)}, collections={len(self.collections)})"
