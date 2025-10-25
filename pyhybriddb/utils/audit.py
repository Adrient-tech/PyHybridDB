"""
Audit logging system for PyHybridDB
Tracks all database operations for security and compliance
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum


class AuditAction(Enum):
    """Audit action types"""
    CREATE_DATABASE = "create_database"
    DELETE_DATABASE = "delete_database"
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    CREATE_COLLECTION = "create_collection"
    DROP_COLLECTION = "drop_collection"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SELECT = "select"
    QUERY = "query"
    LOGIN = "login"
    LOGOUT = "logout"
    BACKUP = "backup"
    RESTORE = "restore"
    IMPORT = "import"
    EXPORT = "export"


class AuditLogger:
    """Audit logging system"""
    
    def __init__(self, audit_db_path: str = "./audit.db"):
        self.audit_db_path = Path(audit_db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize audit database"""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                user TEXT,
                database_name TEXT,
                table_name TEXT,
                details TEXT,
                ip_address TEXT,
                success BOOLEAN,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_action ON audit_log(action)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user ON audit_log(user)
        ''')
        
        conn.commit()
        conn.close()
    
    def log(self, 
            action: AuditAction,
            user: Optional[str] = None,
            database_name: Optional[str] = None,
            table_name: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None,
            ip_address: Optional[str] = None,
            success: bool = True,
            error_message: Optional[str] = None):
        """Log an audit event"""
        
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_log 
            (timestamp, action, user, database_name, table_name, details, ip_address, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            action.value if isinstance(action, AuditAction) else action,
            user,
            database_name,
            table_name,
            json.dumps(details) if details else None,
            ip_address,
            success,
            error_message
        ))
        
        conn.commit()
        conn.close()
    
    def get_logs(self,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 action: Optional[AuditAction] = None,
                 user: Optional[str] = None,
                 database_name: Optional[str] = None,
                 limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filters"""
        
        conn = sqlite3.connect(self.audit_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        if action:
            query += " AND action = ?"
            params.append(action.value if isinstance(action, AuditAction) else action)
        
        if user:
            query += " AND user = ?"
            params.append(user)
        
        if database_name:
            query += " AND database_name = ?"
            params.append(database_name)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            log = dict(row)
            if log['details']:
                log['details'] = json.loads(log['details'])
            logs.append(log)
        
        conn.close()
        return logs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit statistics"""
        
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        total_events = cursor.fetchone()[0]
        
        # Events by action
        cursor.execute('''
            SELECT action, COUNT(*) as count 
            FROM audit_log 
            GROUP BY action 
            ORDER BY count DESC
        ''')
        events_by_action = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Events by user
        cursor.execute('''
            SELECT user, COUNT(*) as count 
            FROM audit_log 
            WHERE user IS NOT NULL
            GROUP BY user 
            ORDER BY count DESC
            LIMIT 10
        ''')
        events_by_user = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Failed operations
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE success = 0")
        failed_operations = cursor.fetchone()[0]
        
        # Recent activity (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) FROM audit_log 
            WHERE timestamp >= datetime('now', '-1 day')
        ''')
        recent_activity = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_events": total_events,
            "events_by_action": events_by_action,
            "events_by_user": events_by_user,
            "failed_operations": failed_operations,
            "recent_activity_24h": recent_activity
        }
    
    def clear_old_logs(self, days: int = 90):
        """Clear audit logs older than specified days"""
        
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM audit_log 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count


# Global audit logger instance
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
