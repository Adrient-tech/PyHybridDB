"""
NoSQL Parser - Parse and execute MongoDB-style queries
"""

import json
import re
from typing import Any, Dict, List
from pyhybriddb.core.database import Database


class NoSQLParser:
    """NoSQL (MongoDB-style) query parser and executor"""
    
    def __init__(self, database: Database):
        self.database = database
    
    def parse_and_execute(self, query: str) -> Any:
        """Parse and execute NoSQL query"""
        # Expected format: db.collection.method(args)
        match = re.match(
            r'db\.(\w+)\.(\w+)\((.*)\)',
            query.strip(),
            re.DOTALL
        )
        
        if not match:
            raise ValueError("Invalid NoSQL query format. Expected: db.collection.method(args)")
        
        collection_name = match.group(1)
        method = match.group(2)
        args_str = match.group(3).strip()
        
        # Get collection
        collection = self.database.get_collection(collection_name)
        if not collection:
            raise ValueError(f"Collection '{collection_name}' not found")
        
        # Parse arguments
        args = self._parse_args(args_str) if args_str else []
        
        # Execute method
        return self._execute_method(collection, method, args)
    
    def _parse_args(self, args_str: str) -> List[Any]:
        """Parse method arguments"""
        # Try to parse as JSON
        try:
            # Handle single argument
            if not args_str.startswith('['):
                args_str = f'[{args_str}]'
            
            return json.loads(args_str)
        except json.JSONDecodeError:
            # Fallback to simple parsing
            return [args_str]
    
    def _execute_method(self, collection, method: str, args: List[Any]) -> Any:
        """Execute collection method"""
        if method == 'insertOne':
            if not args or not isinstance(args[0], dict):
                raise ValueError("insertOne requires a document argument")
            return collection.insert_one(args[0])
        
        elif method == 'insertMany':
            if not args or not isinstance(args[0], list):
                raise ValueError("insertMany requires an array of documents")
            return collection.insert_many(args[0])
        
        elif method == 'find':
            query = args[0] if args and isinstance(args[0], dict) else {}
            return collection.find(query)
        
        elif method == 'findOne':
            if not args or not isinstance(args[0], dict):
                raise ValueError("findOne requires a query argument")
            return collection.find_one(args[0])
        
        elif method == 'updateOne':
            if len(args) < 2:
                raise ValueError("updateOne requires query and update arguments")
            return collection.update_one(args[0], args[1])
        
        elif method == 'updateMany':
            if len(args) < 2:
                raise ValueError("updateMany requires query and update arguments")
            return collection.update_many(args[0], args[1])
        
        elif method == 'deleteOne':
            if not args or not isinstance(args[0], dict):
                raise ValueError("deleteOne requires a query argument")
            return collection.delete_one(args[0])
        
        elif method == 'deleteMany':
            if not args or not isinstance(args[0], dict):
                raise ValueError("deleteMany requires a query argument")
            return collection.delete_many(args[0])
        
        elif method == 'countDocuments':
            query = args[0] if args and isinstance(args[0], dict) else None
            return collection.count_documents(query)
        
        elif method == 'aggregate':
            if not args or not isinstance(args[0], list):
                raise ValueError("aggregate requires a pipeline array")
            return collection.aggregate(args[0])
        
        else:
            raise ValueError(f"Unsupported method: {method}")
