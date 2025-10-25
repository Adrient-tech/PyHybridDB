"""
Collection - Unstructured document storage (MongoDB-like)
"""

from typing import Dict, Any, List, Optional
from pyhybriddb.storage.engine import StorageEngine
import uuid


class Collection:
    """Represents a schema-less document collection"""
    
    def __init__(self, name: str, storage_engine: StorageEngine):
        self.name = name
        self.storage_engine = storage_engine
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert a single document"""
        # Add _id if not present
        if '_id' not in document:
            document['_id'] = str(uuid.uuid4())
        
        # Store document
        offset = self.storage_engine.insert_record(self.name, document)
        
        # Update collection metadata
        if self.name in self.storage_engine.metadata['collections']:
            self.storage_engine.metadata['collections'][self.name]['offsets'].append(offset)
        
        return document['_id']
    
    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents"""
        ids = []
        for doc in documents:
            doc_id = self.insert_one(doc)
            ids.append(doc_id)
        return ids
    
    def find(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find documents matching query"""
        results = []
        
        # Get all offsets for this collection
        coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
        offsets = coll_info.get('offsets', [])
        
        for offset in offsets:
            try:
                document = self.storage_engine.read_record(offset)
                
                # Apply query filter
                if query is None or self._matches_query(document, query):
                    results.append(document)
            except Exception:
                continue
        
        return results
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        results = self.find(query)
        return results[0] if results else None
    
    def _matches_query(self, document: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if document matches query"""
        for key, value in query.items():
            # Handle nested queries
            if key.startswith('$'):
                # Special operators like $gt, $lt, etc.
                continue
            
            # Simple equality check
            if key not in document:
                return False
            
            # Handle nested fields (dot notation)
            if '.' in key:
                if not self._get_nested_value(document, key) == value:
                    return False
            else:
                if document[key] != value:
                    return False
        
        return True
    
    def _get_nested_value(self, document: Dict, path: str) -> Any:
        """Get value from nested document using dot notation"""
        keys = path.split('.')
        value = document
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document"""
        coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
        offsets = coll_info.get('offsets', [])
        
        for i, offset in enumerate(offsets):
            try:
                document = self.storage_engine.read_record(offset)
                
                if self._matches_query(document, query):
                    # Apply update
                    self._apply_update(document, update)
                    
                    # Write updated document
                    new_offset = self.storage_engine.update_record(offset, document)
                    offsets[i] = new_offset
                    return True
            except Exception:
                continue
        
        return False
    
    def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update multiple documents"""
        count = 0
        coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
        offsets = coll_info.get('offsets', [])
        
        for i, offset in enumerate(offsets):
            try:
                document = self.storage_engine.read_record(offset)
                
                if self._matches_query(document, query):
                    # Apply update
                    self._apply_update(document, update)
                    
                    # Write updated document
                    new_offset = self.storage_engine.update_record(offset, document)
                    offsets[i] = new_offset
                    count += 1
            except Exception:
                continue
        
        return count
    
    def _apply_update(self, document: Dict[str, Any], update: Dict[str, Any]):
        """Apply update operators to document"""
        for operator, fields in update.items():
            if operator == '$set':
                document.update(fields)
            elif operator == '$unset':
                for field in fields:
                    document.pop(field, None)
            elif operator == '$inc':
                for field, value in fields.items():
                    document[field] = document.get(field, 0) + value
            else:
                # No operator, direct update
                document.update(update)
                break
    
    def delete_one(self, query: Dict[str, Any]) -> bool:
        """Delete a single document"""
        coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
        offsets = coll_info.get('offsets', [])
        
        for i, offset in enumerate(offsets):
            try:
                document = self.storage_engine.read_record(offset)
                
                if self._matches_query(document, query):
                    # Mark for deletion
                    self.storage_engine.delete_record(self.name, document.get('_id'))
                    offsets.pop(i)
                    return True
            except Exception:
                continue
        
        return False
    
    def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete multiple documents"""
        count = 0
        coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
        offsets = coll_info.get('offsets', [])
        new_offsets = []
        
        for offset in offsets:
            try:
                document = self.storage_engine.read_record(offset)
                
                if self._matches_query(document, query):
                    # Mark for deletion
                    self.storage_engine.delete_record(self.name, document.get('_id'))
                    count += 1
                else:
                    new_offsets.append(offset)
            except Exception:
                new_offsets.append(offset)
        
        # Update offsets
        coll_info['offsets'] = new_offsets
        
        return count
    
    def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching query"""
        if query is None:
            coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
            return len(coll_info.get('offsets', []))
        
        return len(self.find(query))
    
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation pipeline (simplified)"""
        results = self.find()
        
        for stage in pipeline:
            if '$match' in stage:
                results = [doc for doc in results if self._matches_query(doc, stage['$match'])]
            elif '$project' in stage:
                projection = stage['$project']
                results = [{k: doc.get(k) for k in projection} for doc in results]
            elif '$limit' in stage:
                results = results[:stage['$limit']]
            elif '$sort' in stage:
                # Simplified sort
                sort_key = list(stage['$sort'].keys())[0]
                reverse = stage['$sort'][sort_key] == -1
                results = sorted(results, key=lambda x: x.get(sort_key, ''), reverse=reverse)
        
        return results
    
    def __repr__(self):
        return f"Collection(name='{self.name}', documents={self.count_documents()})"
