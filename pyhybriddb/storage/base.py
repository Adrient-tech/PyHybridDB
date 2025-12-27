"""
Base Storage Engine - Abstract interface for storage backends
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseStorageEngine(ABC):
    """Abstract base class for storage engines"""

    def __init__(self):
        # Metadata cache - expected to be populated by the implementation
        self.metadata: Dict[str, Any] = {
            'tables': {},
            'collections': {},
            'indexes': {}
        }

    @abstractmethod
    def initialize(self):
        """Initialize a new database storage"""
        pass

    @abstractmethod
    def open(self):
        """Open existing database storage"""
        pass

    @abstractmethod
    def close(self):
        """Close database connection/file"""
        pass

    @abstractmethod
    def insert_record(self, container_name: str, record: Dict[str, Any]) -> Any:
        """Insert a record and return its ID"""
        pass

    @abstractmethod
    def read_record(self, container_name: str, record_id: Any) -> Dict[str, Any]:
        """Read a record by ID"""
        pass

    @abstractmethod
    def update_record(self, container_name: str, record_id: Any, record: Dict[str, Any]) -> Any:
        """Update a record"""
        pass

    @abstractmethod
    def delete_record(self, container_name: str, record_id: Any):
        """Delete a record"""
        pass

    @abstractmethod
    def create_index(self, container_name: str, order: int = 4):
        """Create an index for a container"""
        pass

    @abstractmethod
    def scan_table(self, container_name: str) -> List[Dict[str, Any]]:
        """Scan all records in a container"""
        pass

    @abstractmethod
    def commit(self):
        """Commit pending transactions"""
        pass

    @abstractmethod
    def rollback(self):
        """Rollback pending transactions"""
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
