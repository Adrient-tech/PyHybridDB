"""
B-Tree Index implementation for efficient data retrieval
"""

from typing import Any, Optional, List, Tuple
from dataclasses import dataclass, field
import bisect


@dataclass
class BTreeNode:
    """Node in B-Tree structure"""
    order: int
    keys: List[Any] = field(default_factory=list)
    values: List[int] = field(default_factory=list)  # File offsets
    children: List['BTreeNode'] = field(default_factory=list)
    is_leaf: bool = True


class BTreeIndex:
    """B-Tree index for fast lookups"""
    
    def __init__(self, order: int = 4):
        self.order = order
        self.root = BTreeNode(order)
        self._size = 0
    
    def insert(self, key: Any, value: int):
        """Insert key-value pair into index"""
        root = self.root
        
        # Max keys is 2*order - 1
        if len(root.keys) >= (2 * self.order - 1):
            # Root is full, split it
            new_root = BTreeNode(self.order)
            new_root.is_leaf = False
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        
        self._insert_non_full(self.root, key, value)
        self._size += 1
    
    def _insert_non_full(self, node: BTreeNode, key: Any, value: int):
        """Insert into a non-full node"""
        i = len(node.keys) - 1
        
        if node.is_leaf:
            # Insert into leaf node
            node.keys.append(None)
            node.values.append(None)
            
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            # Find child to insert into
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if len(node.children[i].keys) >= (2 * self.order - 1):
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)
    
    def _split_child(self, parent: BTreeNode, index: int):
        """Split a full child node"""
        order = self.order
        full_child = parent.children[index]
        new_child = BTreeNode(order)
        new_child.is_leaf = full_child.is_leaf
        
        # mid index for 2*order - 1 keys is (order - 1)
        # e.g., order=4, max keys=7, mid index=3
        mid = order - 1
        
        # Move keys and values to new node
        # keys[mid+1:] goes to new_child
        new_child.keys = full_child.keys[mid + 1:]
        new_child.values = full_child.values[mid + 1:]

        # keys[:mid] stays in full_child
        # keys[mid] goes to parent
        median_key = full_child.keys[mid]
        median_value = full_child.values[mid]

        full_child.keys = full_child.keys[:mid]
        full_child.values = full_child.values[:mid]
        
        # If not leaf, children also need to be split
        # full_child children count is len(keys)+1
        # Original keys=2t-1, children=2t
        # New keys=t-1, children=t
        if not full_child.is_leaf:
            new_child.children = full_child.children[mid + 1:]
            full_child.children = full_child.children[:mid + 1]
        
        # Insert middle key into parent
        parent.children.insert(index + 1, new_child)
        parent.keys.insert(index, median_key)
        parent.values.insert(index, median_value)
    
    def search(self, key: Any) -> Optional[int]:
        """Search for a key and return its value (offset)"""
        return self._search_node(self.root, key)
    
    def _search_node(self, node: BTreeNode, key: Any) -> Optional[int]:
        """Search within a node"""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]
        
        if node.is_leaf:
            return None
        
        return self._search_node(node.children[i], key)
    
    def range_search(self, start_key: Any, end_key: Any) -> List[Tuple[Any, int]]:
        """Search for all keys in range [start_key, end_key]"""
        results = []
        self._range_search_node(self.root, start_key, end_key, results)
        return results
    
    def _range_search_node(self, node: BTreeNode, start: Any, end: Any, results: List):
        """Range search within a node"""
        i = 0
        
        while i < len(node.keys):
            if not node.is_leaf:
                if start <= node.keys[i]:
                    self._range_search_node(node.children[i], start, end, results)
            
            if start <= node.keys[i] <= end:
                results.append((node.keys[i], node.values[i]))
            
            i += 1
        
        # Check last child
        if not node.is_leaf:
             # Need to be careful here to only traverse if relevant
             # The loop handles children[0] to children[n-1]
             # This handles children[n] (rightmost child)
             if end >= node.keys[i-1]:
                self._range_search_node(node.children[i], start, end, results)
    
    def delete(self, key: Any) -> bool:
        """Delete a key from the index"""
        # Simplified deletion - full implementation would be more complex
        # Note: This simple implementation might unbalance the tree
        return self._delete_from_node(self.root, key)
    
    def _delete_from_node(self, node: BTreeNode, key: Any) -> bool:
        """Delete key from node (simplified)"""
        try:
            if key in node.keys:
                idx = node.keys.index(key)
                del node.keys[idx]
                del node.values[idx]
                self._size -= 1
                return True
            elif not node.is_leaf:
                # Find child
                i = 0
                while i < len(node.keys) and key > node.keys[i]:
                    i += 1
                return self._delete_from_node(node.children[i], key)
            return False
        except ValueError:
            return False
    
    def size(self) -> int:
        """Return number of entries in index"""
        return self._size
    
    def clear(self):
        """Clear all entries"""
        self.root = BTreeNode(self.order)
        self._size = 0
