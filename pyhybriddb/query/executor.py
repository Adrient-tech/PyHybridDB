"""
Query Executor - Execute parsed queries with optimization
"""

from typing import Any, Dict, List
from pyhybriddb.core.database import Database


class QueryExecutor:
    """Execute queries with optimization"""
    
    def __init__(self, database: Database):
        self.database = database
        self.query_cache: Dict[str, Any] = {}
        self.cache_enabled = True
    
    def execute(self, query: str, use_cache: bool = True) -> Any:
        """Execute a query with optional caching"""
        if use_cache and self.cache_enabled:
            if query in self.query_cache:
                return self.query_cache[query]
        
        # Parse and execute
        from pyhybriddb.query.parser import QueryParser
        parser = QueryParser(self.database)
        result = parser.parse_and_execute(query)
        
        # Cache result
        if use_cache and self.cache_enabled:
            self.query_cache[query] = result
        
        return result
    
    def clear_cache(self):
        """Clear query cache"""
        self.query_cache.clear()
    
    def enable_cache(self):
        """Enable query caching"""
        self.cache_enabled = True
    
    def disable_cache(self):
        """Disable query caching"""
        self.cache_enabled = False
    
    def explain(self, query: str) -> Dict[str, Any]:
        """Explain query execution plan"""
        # Simplified explain - would include index usage, scan type, etc.
        return {
            'query': query,
            'type': 'full_scan',  # or 'index_scan'
            'estimated_rows': 0,
            'cached': query in self.query_cache
        }
