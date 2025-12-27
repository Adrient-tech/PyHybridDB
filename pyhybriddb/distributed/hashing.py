"""
Consistent Hashing implementation for Distributed Sharding
"""

import hashlib
import bisect
from typing import List, Dict, Any

class ConsistentHashRing:
    """Consistent Hash Ring for node distribution"""

    def __init__(self, nodes: List[str] = None, replicas: int = 3):
        self.replicas = replicas
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def add_node(self, node: str):
        """Add a node to the ring"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node: str):
        """Remove a node from the ring"""
        keys_to_remove = []
        for key, n in self.ring.items():
            if n == node:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key: str) -> str:
        """Get the node responsible for the key"""
        if not self.ring:
            return None

        hash_val = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_val)

        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def get_nodes_for_key(self, key: str, n: int = 1) -> List[str]:
        """Get N nodes responsible for key (for replication)"""
        if not self.ring:
            return []

        hash_val = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_val)

        nodes = []
        seen = set()

        for i in range(len(self.sorted_keys)):
            current_idx = (idx + i) % len(self.sorted_keys)
            node = self.ring[self.sorted_keys[current_idx]]

            if node not in seen:
                nodes.append(node)
                seen.add(node)

            if len(nodes) == n:
                break

        return nodes

    def _hash(self, key: str) -> int:
        """SHA256 hash"""
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)
