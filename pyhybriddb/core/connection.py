"""
Connection - Database connection manager
"""

from typing import Optional
from pyhybriddb.core.database import Database


class Connection:
    """Database connection"""
    
    def __init__(self, database: Database):
        self.database = database
        self._in_transaction = False
    
    def begin_transaction(self):
        """Begin a transaction"""
        self._in_transaction = True
    
    def commit(self):
        """Commit the current transaction"""
        if self._in_transaction:
            self.database.commit()
            self._in_transaction = False
    
    def rollback(self):
        """Rollback the current transaction"""
        if self._in_transaction:
            self.database.rollback()
            self._in_transaction = False
    
    def execute(self, query: str):
        """Execute a query (SQL or NoSQL)"""
        # This will be implemented with the query parser
        from pyhybriddb.query.parser import QueryParser
        
        parser = QueryParser(self.database)
        return parser.parse_and_execute(query)
    
    def close(self):
        """Close the connection"""
        if self._in_transaction:
            self.rollback()
        self.database.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and self._in_transaction:
            self.commit()
        elif self._in_transaction:
            self.rollback()
        self.close()
