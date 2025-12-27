"""
Query Processor - Handles complex queries and optimization
"""

from typing import List, Dict, Any, Optional
from pyhybriddb.storage.base import BaseStorageEngine

class QueryProcessor:
    """Processes queries using available indexes"""

    def __init__(self, storage_engine: BaseStorageEngine):
        self.storage_engine = storage_engine

    def execute(self, container_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute a query against a container.

        Supported query operators:
        - Exact match: {'field': 'value'}
        - Comparison: {'field': {'$gt': 10}} ($gt, $lt, $gte, $lte)
        - Logic: {'$and': [...], '$or': [...]} (To be implemented)
        """

        # 1. Query Optimization / Index Selection
        # Check if we can use an index for any part of the query
        best_index_field = None

        # Ensure indexes attribute exists (for LSM engine compatibility)
        indexes = getattr(self.storage_engine, 'indexes', {})

        if container_name in indexes:
            container_indexes = indexes[container_name]
            for field in query:
                if field in container_indexes and not field.startswith('$'):
                    best_index_field = field
                    break

        results = []

        if best_index_field:
            # Use Index Scan
            index = self.storage_engine.indexes[container_name][best_index_field]
            search_value = query[best_index_field]

            # TODO: Support range queries in index ($gt, etc)
            # Currently only supporting exact match on index
            if isinstance(search_value, dict):
                # Fallback to full scan if query on indexed field is complex (e.g. $gt)
                # Unless we implement range_search in processor
                results = self._full_scan(container_name)
            else:
                offset = index.search(search_value)
                if offset is not None:
                    try:
                        record = self.storage_engine.read_record(container_name, offset)
                        results.append(record)
                    except:
                        pass
        else:
            # Full Table Scan
            results = self._full_scan(container_name)

        # 2. Filtering (Refinement)
        # Apply all query conditions to the candidate results
        filtered_results = []
        for doc in results:
            if self._matches_query(doc, query):
                filtered_results.append(doc)

        return filtered_results

    def _full_scan(self, container_name: str) -> List[Dict[str, Any]]:
        """Perform a full scan of the container"""
        return self.storage_engine.scan_table(container_name)

    def _matches_query(self, document: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if document matches query"""
        for key, value in query.items():
            if key.startswith('$'):
                continue

            if key not in document:
                return False

            doc_val = document[key]

            if isinstance(value, dict):
                for op, op_val in value.items():
                    if op == '$gt':
                        if not (doc_val > op_val): return False
                    elif op == '$lt':
                        if not (doc_val < op_val): return False
                    elif op == '$gte':
                        if not (doc_val >= op_val): return False
                    elif op == '$lte':
                        if not (doc_val <= op_val): return False
                    elif op == '$ne':
                        if not (doc_val != op_val): return False
            else:
                if doc_val != value:
                    return False

        return True
