"""
Collection - Unstructured document storage (MongoDB-like)
"""

from typing import Dict, Any, List, Optional
from pyhybriddb.storage.base import BaseStorageEngine
from pyhybriddb.query.processor import QueryProcessor
import uuid


class Collection:
    """Represents a schema-less document collection"""
    
    def __init__(self, name: str, storage_engine: BaseStorageEngine):
        self.name = name
        self.storage_engine = storage_engine
        self.query_processor = QueryProcessor(storage_engine)

        # Ensure 'id' index exists (or '_id')
        self.storage_engine.create_index(name, '_id')
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert a single document"""
        # Add _id if not present
        if '_id' not in document:
            document['_id'] = str(uuid.uuid4())
        
        # Store document
        offset = self.storage_engine.insert_record(self.name, document)
        
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
        if query is None:
            return self.storage_engine.scan_table(self.name)

        return self.query_processor.execute(self.name, query)
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        results = self.find(query)
        return results[0] if results else None
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document"""
        coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
        offsets = coll_info.get('offsets', [])
        
        for i, offset in enumerate(offsets):
            try:
                document = self.storage_engine.read_record(self.name, offset)
                if self.query_processor._matches_query(document, query):
                    self._apply_update(document, update)
                    new_offset = self.storage_engine.update_record(self.name, document['_id'], document)
                    offsets[i] = new_offset
                    return True
            except:
                continue
        return False
    
    def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update multiple documents"""
        count = 0
        coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
        offsets = coll_info.get('offsets', [])
        
        for i, offset in enumerate(offsets):
            try:
                document = self.storage_engine.read_record(self.name, offset)
                if self.query_processor._matches_query(document, query):
                    self._apply_update(document, update)
                    new_offset = self.storage_engine.update_record(self.name, document['_id'], document)
                    offsets[i] = new_offset
                    count += 1
            except:
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
        offsets = list(coll_info.get('offsets', [])) # Copy to iterate safely
        
        for offset in offsets:
            try:
                document = self.storage_engine.read_record(self.name, offset)
                if self.query_processor._matches_query(document, query):
                    self.storage_engine.delete_record(self.name, document['_id'])
                    # If FileEngine, we need to remove from list manually or it persists in metadata?
                    # The previous logic popped i.
                    # But LSM engine removes it inside delete_record.
                    # FileEngine does NOT remove it inside delete_record (it just logs delete transaction).

                    # We should rely on storage engine specific behavior or standardize.
                    # Ideally, higher level shouldn't manage offsets list directly if engine does.

                    # Hack for now: Check if it was removed by engine, if not remove it.
                    current_offsets = coll_info.get('offsets', [])
                    if offset in current_offsets:
                        current_offsets.remove(offset)

                    return True
            except:
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
                document = self.storage_engine.read_record(self.name, offset)
                if self.query_processor._matches_query(document, query):
                    self.storage_engine.delete_record(self.name, document['_id'])
                    count += 1
                else:
                    new_offsets.append(offset)
            except:
                new_offsets.append(offset)

        coll_info['offsets'] = new_offsets
        return count
    
    def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching query"""
        if query is None:
            # Optimized count
            coll_info = self.storage_engine.metadata['collections'].get(self.name, {})
            return len(coll_info.get('offsets', []))
        
        return len(self.find(query))
    
    def create_index(self, field: str):
        """Create an index on a field"""
        self.storage_engine.create_index(self.name, field)

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation pipeline (simplified)"""
        # Initial input is full collection
        results = self.find()
        
        for stage in pipeline:
            if '$match' in stage:
                # Use query processor logic for match if possible?
                # For now reuse matches_query logic from processor
                q = stage['$match']
                results = [doc for doc in results if self.query_processor._matches_query(doc, q)]
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
