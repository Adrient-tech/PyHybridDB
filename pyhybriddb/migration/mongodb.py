"""
MongoDB to PyHybridDB migration tool
"""

from typing import Dict, List, Any, Optional
import json


class MongoDBMigration:
    """Migrate data from MongoDB to PyHybridDB"""
    
    def __init__(self, mongo_config: Dict[str, Any]):
        """
        Initialize MongoDB connection
        
        Args:
            mongo_config: {
                'host': 'localhost',
                'port': 27017,
                'database': 'mydb',
                'username': 'user',  # optional
                'password': 'pass'   # optional
            }
        """
        self.mongo_config = mongo_config
        self.client = None
        self.db = None
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            from pymongo import MongoClient
            
            host = self.mongo_config.get('host', 'localhost')
            port = self.mongo_config.get('port', 27017)
            username = self.mongo_config.get('username')
            password = self.mongo_config.get('password')
            database = self.mongo_config['database']
            
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            else:
                connection_string = f"mongodb://{host}:{port}/{database}"
            
            self.client = MongoClient(connection_string)
            self.db = self.client[database]
            
            # Test connection
            self.client.server_info()
            
            return True
        except ImportError:
            raise ImportError("pymongo not installed. Install with: pip install pymongo")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    
    def get_collections(self) -> List[str]:
        """Get list of collections in MongoDB database"""
        if not self.db:
            self.connect()
        
        return self.db.list_collection_names()
    
    def get_collection_sample(self, collection_name: str, limit: int = 10) -> List[Dict]:
        """Get sample documents from collection"""
        if not self.db:
            self.connect()
        
        collection = self.db[collection_name]
        documents = list(collection.find().limit(limit))
        
        # Convert ObjectId to string
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        return documents
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get document count in collection"""
        if not self.db:
            self.connect()
        
        collection = self.db[collection_name]
        return collection.count_documents({})
    
    def get_collection_data(self, collection_name: str, 
                           query: Optional[Dict] = None,
                           limit: Optional[int] = None) -> List[Dict]:
        """Get all data from a collection"""
        if not self.db:
            self.connect()
        
        collection = self.db[collection_name]
        
        if query is None:
            query = {}
        
        cursor = collection.find(query)
        
        if limit:
            cursor = cursor.limit(limit)
        
        documents = list(cursor)
        
        # Convert ObjectId and other special types to strings
        for doc in documents:
            self._convert_document(doc)
        
        return documents
    
    def _convert_document(self, doc: Dict):
        """Convert MongoDB special types to JSON-serializable types"""
        from bson import ObjectId
        from datetime import datetime
        
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, datetime):
                doc[key] = value.isoformat()
            elif isinstance(value, dict):
                self._convert_document(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._convert_document(item)
                    elif isinstance(item, ObjectId):
                        value[i] = str(item)
    
    def migrate_collection(self, collection_name: str, target_db, 
                          progress_callback=None) -> int:
        """
        Migrate a single collection to PyHybridDB
        
        Args:
            collection_name: MongoDB collection name
            target_db: PyHybridDB Database instance
            progress_callback: Optional callback function(current, total)
        
        Returns:
            Number of documents migrated
        """
        # Create collection in PyHybridDB
        target_collection = target_db.create_collection(collection_name)
        
        # Get data
        documents = self.get_collection_data(collection_name)
        
        # Insert documents
        total = len(documents)
        for i, doc in enumerate(documents):
            target_collection.insert_one(doc)
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return total
    
    def migrate_database(self, target_db, collections: Optional[List[str]] = None,
                        progress_callback=None) -> Dict[str, int]:
        """
        Migrate entire database or specific collections
        
        Args:
            target_db: PyHybridDB Database instance
            collections: List of collection names to migrate (None = all)
            progress_callback: Optional callback function(collection, current, total)
        
        Returns:
            Dictionary of collection_name: document_count
        """
        if collections is None:
            collections = self.get_collections()
        
        results = {}
        
        for collection_name in collections:
            def collection_progress(current, total):
                if progress_callback:
                    progress_callback(collection_name, current, total)
            
            count = self.migrate_collection(collection_name, target_db, collection_progress)
            results[collection_name] = count
        
        return results
    
    def export_to_json(self, collection_name: str, output_file: str):
        """Export collection to JSON file"""
        documents = self.get_collection_data(collection_name)
        
        with open(output_file, 'w') as f:
            json.dump(documents, f, indent=2)
        
        return len(documents)
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
