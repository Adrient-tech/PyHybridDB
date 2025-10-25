"""
JOIN operations for SQL queries
Implements INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class JoinType(Enum):
    """Types of SQL joins"""
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL"


class JoinExecutor:
    """Execute JOIN operations on tables"""
    
    @staticmethod
    def inner_join(left_table: List[Dict], right_table: List[Dict], 
                   left_key: str, right_key: str) -> List[Dict]:
        """
        INNER JOIN - Returns records that have matching values in both tables
        """
        result = []
        
        for left_row in left_table:
            for right_row in right_table:
                if left_row.get(left_key) == right_row.get(right_key):
                    # Merge rows
                    merged = {**left_row}
                    for key, value in right_row.items():
                        # Avoid key conflicts
                        if key in merged and key != right_key:
                            merged[f"right_{key}"] = value
                        else:
                            merged[key] = value
                    result.append(merged)
        
        return result
    
    @staticmethod
    def left_join(left_table: List[Dict], right_table: List[Dict],
                  left_key: str, right_key: str) -> List[Dict]:
        """
        LEFT JOIN - Returns all records from left table, and matched records from right table
        """
        result = []
        
        for left_row in left_table:
            matched = False
            
            for right_row in right_table:
                if left_row.get(left_key) == right_row.get(right_key):
                    # Merge rows
                    merged = {**left_row}
                    for key, value in right_row.items():
                        if key in merged and key != right_key:
                            merged[f"right_{key}"] = value
                        else:
                            merged[key] = value
                    result.append(merged)
                    matched = True
            
            # If no match, include left row with NULL values for right table
            if not matched:
                merged = {**left_row}
                # Add NULL values for right table columns
                if right_table:
                    for key in right_table[0].keys():
                        if key not in merged:
                            merged[key] = None
                result.append(merged)
        
        return result
    
    @staticmethod
    def right_join(left_table: List[Dict], right_table: List[Dict],
                   left_key: str, right_key: str) -> List[Dict]:
        """
        RIGHT JOIN - Returns all records from right table, and matched records from left table
        """
        # Right join is the same as left join with tables swapped
        return JoinExecutor.left_join(right_table, left_table, right_key, left_key)
    
    @staticmethod
    def full_outer_join(left_table: List[Dict], right_table: List[Dict],
                       left_key: str, right_key: str) -> List[Dict]:
        """
        FULL OUTER JOIN - Returns all records when there is a match in either table
        """
        result = []
        matched_right_indices = set()
        
        # First, do a left join
        for left_row in left_table:
            matched = False
            
            for right_idx, right_row in enumerate(right_table):
                if left_row.get(left_key) == right_row.get(right_key):
                    # Merge rows
                    merged = {**left_row}
                    for key, value in right_row.items():
                        if key in merged and key != right_key:
                            merged[f"right_{key}"] = value
                        else:
                            merged[key] = value
                    result.append(merged)
                    matched = True
                    matched_right_indices.add(right_idx)
            
            # If no match, include left row with NULL values
            if not matched:
                merged = {**left_row}
                if right_table:
                    for key in right_table[0].keys():
                        if key not in merged:
                            merged[key] = None
                result.append(merged)
        
        # Add unmatched rows from right table
        for right_idx, right_row in enumerate(right_table):
            if right_idx not in matched_right_indices:
                merged = {**right_row}
                # Add NULL values for left table columns
                if left_table:
                    for key in left_table[0].keys():
                        if key not in merged:
                            merged[key] = None
                result.append(merged)
        
        return result
    
    @staticmethod
    def execute_join(left_table: List[Dict], right_table: List[Dict],
                    left_key: str, right_key: str, 
                    join_type: JoinType = JoinType.INNER) -> List[Dict]:
        """
        Execute a JOIN operation based on join type
        """
        if join_type == JoinType.INNER:
            return JoinExecutor.inner_join(left_table, right_table, left_key, right_key)
        elif join_type == JoinType.LEFT:
            return JoinExecutor.left_join(left_table, right_table, left_key, right_key)
        elif join_type == JoinType.RIGHT:
            return JoinExecutor.right_join(left_table, right_table, left_key, right_key)
        elif join_type == JoinType.FULL:
            return JoinExecutor.full_outer_join(left_table, right_table, left_key, right_key)
        else:
            raise ValueError(f"Unsupported join type: {join_type}")
    
    @staticmethod
    def parse_join_query(query: str) -> Optional[Dict[str, Any]]:
        """
        Parse a SQL JOIN query
        Example: SELECT * FROM users INNER JOIN orders ON users.id = orders.user_id
        """
        import re
        
        # Simple JOIN query pattern
        pattern = r'SELECT\s+(.+?)\s+FROM\s+(\w+)\s+(INNER|LEFT|RIGHT|FULL\s+OUTER)\s+JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        
        match = re.match(pattern, query, re.IGNORECASE)
        
        if not match:
            return None
        
        columns = match.group(1).strip()
        left_table = match.group(2)
        join_type_str = match.group(3).upper().replace(' ', '_')
        right_table = match.group(4)
        left_table_alias = match.group(5)
        left_key = match.group(6)
        right_table_alias = match.group(7)
        right_key = match.group(8)
        
        # Map join type string to enum
        join_type_map = {
            'INNER': JoinType.INNER,
            'LEFT': JoinType.LEFT,
            'RIGHT': JoinType.RIGHT,
            'FULL_OUTER': JoinType.FULL
        }
        
        return {
            'columns': columns,
            'left_table': left_table,
            'right_table': right_table,
            'left_key': left_key,
            'right_key': right_key,
            'join_type': join_type_map.get(join_type_str, JoinType.INNER)
        }
