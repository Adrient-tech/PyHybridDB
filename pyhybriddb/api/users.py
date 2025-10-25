"""
User Management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
import sqlite3
from pathlib import Path

from pyhybriddb.api.auth import get_current_user, User
from pyhybriddb.utils.audit import get_audit_logger, AuditAction

router = APIRouter(prefix="/api/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    """User creation request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    role: str = Field(default="user", pattern="^(admin|user|readonly)$")


class UserUpdate(BaseModel):
    """User update request"""
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|user|readonly)$")
    disabled: Optional[bool] = None


class UserResponse(BaseModel):
    """User response model"""
    username: str
    email: Optional[str]
    role: str
    disabled: bool


class UserDatabase:
    """User database manager"""
    
    def __init__(self, db_path: str = "./users.db"):
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                hashed_password TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL DEFAULT 'user',
                disabled BOOLEAN NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password: str, email: Optional[str], role: str) -> bool:
        """Create a new user"""
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            hashed_password = pwd_context.hash(password)
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO users (username, hashed_password, email, role, disabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, 0, ?, ?)
            ''', (username, hashed_password, email, role, now, now))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def list_users(self) -> List[dict]:
        """List all users"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT username, email, role, disabled, created_at FROM users')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_user(self, username: str, email: Optional[str], role: Optional[str], disabled: Optional[bool]) -> bool:
        """Update user"""
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        
        if disabled is not None:
            updates.append("disabled = ?")
            params.append(1 if disabled else 0)
        
        if not updates:
            conn.close()
            return False
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(username)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_user(self, username: str) -> bool:
        """Delete user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password"""
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        hashed_password = pwd_context.hash(new_password)
        
        cursor.execute('''
            UPDATE users 
            SET hashed_password = ?, updated_at = ?
            WHERE username = ?
        ''', (hashed_password, datetime.now().isoformat(), username))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success


# Global user database instance
user_db = UserDatabase()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, current_user: User = Depends(get_current_user)):
    """Create a new user (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = user_db.create_user(
        username=user_create.username,
        password=user_create.password,
        email=user_create.email,
        role=user_create.role
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Log audit
    audit_logger = get_audit_logger()
    audit_logger.log(
        action=AuditAction.LOGIN,
        user=current_user.username,
        details={"created_user": user_create.username}
    )
    
    return UserResponse(
        username=user_create.username,
        email=user_create.email,
        role=user_create.role,
        disabled=False
    )


@router.get("", response_model=List[UserResponse])
async def list_users(current_user: User = Depends(get_current_user)):
    """List all users (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = user_db.list_users()
    
    return [
        UserResponse(
            username=u['username'],
            email=u.get('email'),
            role=u['role'],
            disabled=bool(u['disabled'])
        )
        for u in users
    ]


@router.get("/{username}", response_model=UserResponse)
async def get_user(username: str, current_user: User = Depends(get_current_user)):
    """Get user details"""
    
    # Users can only view their own details unless admin
    if current_user.role != "admin" and current_user.username != username:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = user_db.get_user(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        username=user['username'],
        email=user.get('email'),
        role=user['role'],
        disabled=bool(user['disabled'])
    )


@router.put("/{username}", response_model=UserResponse)
async def update_user(username: str, user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    """Update user (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = user_db.update_user(
        username=username,
        email=user_update.email,
        role=user_update.role,
        disabled=user_update.disabled
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log audit
    audit_logger = get_audit_logger()
    audit_logger.log(
        action=AuditAction.LOGIN,
        user=current_user.username,
        details={"updated_user": username, "changes": user_update.dict(exclude_none=True)}
    )
    
    user = user_db.get_user(username)
    
    return UserResponse(
        username=user['username'],
        email=user.get('email'),
        role=user['role'],
        disabled=bool(user['disabled'])
    )


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(username: str, current_user: User = Depends(get_current_user)):
    """Delete user (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    success = user_db.delete_user(username)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log audit
    audit_logger = get_audit_logger()
    audit_logger.log(
        action=AuditAction.LOGIN,
        user=current_user.username,
        details={"deleted_user": username}
    )
