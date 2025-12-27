"""
Distributed Cluster Client
Routes requests to nodes based on Consistent Hashing
"""

import requests
from typing import List, Dict, Any, Optional
from pyhybriddb.distributed.hashing import ConsistentHashRing

class DistributedCluster:
    """Client for a distributed cluster of PyHybridDB nodes"""

    def __init__(self, nodes: List[str]):
        """
        nodes: List of URLs e.g. ["http://localhost:8001", "http://localhost:8002"]
        """
        self.ring = ConsistentHashRing(nodes)

    def write(self, collection: str, data: Dict[str, Any], key_field: str = "_id"):
        """Write data to the cluster"""
        # Determine key for sharding
        if key_field in data:
            key = str(data[key_field])
        else:
            import uuid
            key = str(uuid.uuid4())
            data[key_field] = key

        # Get target node
        node_url = self.ring.get_node(key)
        if not node_url:
            raise RuntimeError("No nodes available")

        # Send request
        try:
            resp = requests.post(f"{node_url}/write", json={
                "collection": collection,
                "data": data
            })
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            # Basic fault tolerance: try next node?
            # For now just fail.
            raise RuntimeError(f"Failed to write to {node_url}: {e}")

    def read(self, collection: str, query: Dict[str, Any], key_field: str = "_id"):
        """Read data from the cluster"""
        # If query has the sharding key, we can route directly
        if key_field in query:
            key = str(query[key_field])
            node_url = self.ring.get_node(key)
            return self._read_from_node(node_url, collection, query)
        else:
            # Scatter-Gather: Query ALL nodes (expensive)
            # For MVP: query all and merge? Or just first match?
            # Let's just query all and return first non-null
            for node_url in self.ring.sorted_keys: # This iterates hashes, not unique nodes
                # Get unique nodes
                pass

            # Simplified: Iterate unique nodes
            unique_nodes = set(self.ring.ring.values())
            for node_url in unique_nodes:
                res = self._read_from_node(node_url, collection, query)
                if res:
                    return res
            return None

    def _read_from_node(self, node_url: str, collection: str, query: Dict[str, Any]):
        try:
            resp = requests.post(f"{node_url}/read", json={
                "collection": collection,
                "query": query
            })
            if resp.status_code == 200:
                data = resp.json()
                return data.get("result")
        except:
            pass
        return None
