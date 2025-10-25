"""
Serializer - Data serialization utilities
"""

import json
import pickle
from typing import Any, Dict


class Serializer:
    """Serialize and deserialize data"""
    
    @staticmethod
    def to_json(data: Any) -> str:
        """Serialize to JSON"""
        return json.dumps(data, default=str)
    
    @staticmethod
    def from_json(json_str: str) -> Any:
        """Deserialize from JSON"""
        return json.loads(json_str)
    
    @staticmethod
    def to_bytes(data: Any) -> bytes:
        """Serialize to bytes using pickle"""
        return pickle.dumps(data)
    
    @staticmethod
    def from_bytes(data: bytes) -> Any:
        """Deserialize from bytes"""
        return pickle.loads(data)
