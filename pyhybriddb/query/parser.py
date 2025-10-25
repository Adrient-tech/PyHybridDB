"""
Query Parser - Unified parser for SQL and NoSQL queries
"""

from typing import Any, Dict, List, Optional
from pyhybriddb.core.database import Database
from pyhybriddb.query.sql_parser import SQLParser
from pyhybriddb.query.nosql_parser import NoSQLParser


class QueryParser:
    """Main query parser that routes to SQL or NoSQL parser"""
    
    def __init__(self, database: Database):
        self.database = database
        self.sql_parser = SQLParser(database)
        self.nosql_parser = NoSQLParser(database)
    
    def parse_and_execute(self, query: str) -> Any:
        """Parse and execute a query"""
        query = query.strip()
        
        # Detect query type
        if self._is_sql_query(query):
            return self.sql_parser.parse_and_execute(query)
        else:
            return self.nosql_parser.parse_and_execute(query)
    
    def _is_sql_query(self, query: str) -> bool:
        """Detect if query is SQL"""
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        query_upper = query.upper()
        
        for keyword in sql_keywords:
            if query_upper.startswith(keyword):
                return True
        
        return False
