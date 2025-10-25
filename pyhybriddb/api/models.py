"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class DatabaseCreate(BaseModel):
    """Database creation request"""
    name: str = Field(..., description="Database name")
    path: Optional[str] = Field(None, description="Database file path")


class TableCreate(BaseModel):
    """Table creation request"""
    name: str = Field(..., description="Table name")
    schema: Dict[str, str] = Field(..., description="Table schema (column: type)")


class CollectionCreate(BaseModel):
    """Collection creation request"""
    name: str = Field(..., description="Collection name")


class RecordInsert(BaseModel):
    """Record insertion request"""
    data: Dict[str, Any] = Field(..., description="Record data")


class DocumentInsert(BaseModel):
    """Document insertion request"""
    data: Dict[str, Any] = Field(..., description="Document data")


class QueryRequest(BaseModel):
    """Query execution request"""
    query: str = Field(..., description="SQL or NoSQL query")


class UserCreate(BaseModel):
    """User creation request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None
    role: str = Field(default="user", description="User role: admin, user, readonly")


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None
