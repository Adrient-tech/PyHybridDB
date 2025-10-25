"""
FastAPI Server - Main API server for admin panel
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from pathlib import Path

from pyhybriddb.core.database import Database
from pyhybriddb.api.models import (
    DatabaseCreate,
    TableCreate,
    CollectionCreate,
    QueryRequest,
    RecordInsert,
    DocumentInsert,
    UserLogin,
    Token
)
from pyhybriddb.api.auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from pyhybriddb.utils.logger import setup_logger
from pyhybriddb.utils.backup import BackupManager
from pyhybriddb.utils.audit import get_audit_logger, AuditAction
from pyhybriddb.utils.visualization import DataVisualizer
from pyhybriddb.config import Config
from datetime import timedelta

# Setup logger
logger = setup_logger("pyhybriddb.api")

# Create FastAPI app
app = FastAPI(
    title="PyHybridDB API",
    description="Hybrid Database System API",
    version="0.1.0"
)

# CORS middleware - configured from environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.get_cors_origins(),
    allow_credentials=Config.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database registry
databases: Dict[str, Database] = {}

# Global instances
backup_manager = BackupManager()
audit_logger = get_audit_logger()


# Authentication endpoints
@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """Login endpoint - returns JWT token"""
    user = authenticate_user(user_login.username, user_login.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


@app.get("/api/auth/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }


# Database management endpoints
@app.post("/api/databases")
async def create_database(db_create: DatabaseCreate, current_user = Depends(get_current_user)):
    """Create a new database"""
    try:
        if db_create.name in databases:
            raise HTTPException(status_code=400, detail="Database already exists")
        
        db = Database(name=db_create.name, path=db_create.path)
        db.create()
        databases[db_create.name] = db
        
        logger.info(f"Created database: {db_create.name}")
        
        return {"message": f"Database '{db_create.name}' created", "name": db_create.name}
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/databases")
async def list_databases():
    """List all databases"""
    return {
        "databases": [
            {
                "name": name,
                "stats": db.get_stats()
            }
            for name, db in databases.items()
        ]
    }


@app.get("/api/databases/{db_name}")
async def get_database(db_name: str):
    """Get database details"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    return {
        "name": db_name,
        "tables": db.list_tables(),
        "collections": db.list_collections(),
        "stats": db.get_stats()
    }


@app.delete("/api/databases/{db_name}")
async def delete_database(db_name: str):
    """Delete a database"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    db.close()
    
    # Delete file
    if db.db_file.exists():
        db.db_file.unlink()
    
    del databases[db_name]
    
    logger.info(f"Deleted database: {db_name}")
    
    return {"message": f"Database '{db_name}' deleted"}


# Table endpoints
@app.post("/api/databases/{db_name}/tables")
async def create_table(db_name: str, table_create: TableCreate):
    """Create a new table"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    try:
        db = databases[db_name]
        table = db.create_table(table_create.name, table_create.schema)
        
        logger.info(f"Created table: {db_name}.{table_create.name}")
        
        return {"message": f"Table '{table_create.name}' created", "table": table.describe()}
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/databases/{db_name}/tables")
async def list_tables(db_name: str):
    """List all tables in database"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    return {
        "tables": [
            db.get_table(name).describe()
            for name in db.list_tables()
        ]
    }


@app.get("/api/databases/{db_name}/tables/{table_name}")
async def get_table(db_name: str, table_name: str):
    """Get table details"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    table = db.get_table(table_name)
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    return table.describe()


@app.post("/api/databases/{db_name}/tables/{table_name}/records")
async def insert_record(db_name: str, table_name: str, record: RecordInsert):
    """Insert a record into table"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    table = db.get_table(table_name)
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    try:
        record_id = table.insert(record.data)
        db.commit()
        
        return {"message": "Record inserted", "id": record_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/databases/{db_name}/tables/{table_name}/records")
async def get_records(db_name: str, table_name: str):
    """Get all records from table"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    table = db.get_table(table_name)
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    records = table.select()
    return {"records": records, "count": len(records)}


# Collection endpoints
@app.post("/api/databases/{db_name}/collections")
async def create_collection(db_name: str, collection_create: CollectionCreate):
    """Create a new collection"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    try:
        db = databases[db_name]
        collection = db.create_collection(collection_create.name)
        
        logger.info(f"Created collection: {db_name}.{collection_create.name}")
        
        return {"message": f"Collection '{collection_create.name}' created"}
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/databases/{db_name}/collections")
async def list_collections(db_name: str):
    """List all collections in database"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    return {"collections": db.list_collections()}


@app.post("/api/databases/{db_name}/collections/{collection_name}/documents")
async def insert_document(db_name: str, collection_name: str, document: DocumentInsert):
    """Insert a document into collection"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    collection = db.get_collection(collection_name)
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    try:
        doc_id = collection.insert_one(document.data)
        db.commit()
        
        return {"message": "Document inserted", "_id": doc_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/databases/{db_name}/collections/{collection_name}/documents")
async def get_documents(db_name: str, collection_name: str):
    """Get all documents from collection"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    collection = db.get_collection(collection_name)
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    documents = collection.find()
    return {"documents": documents, "count": len(documents)}


# Query endpoint
@app.post("/api/databases/{db_name}/query")
async def execute_query(db_name: str, query_req: QueryRequest):
    """Execute a query (SQL or NoSQL)"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    
    try:
        from pyhybriddb.query.parser import QueryParser
        parser = QueryParser(db)
        result = parser.parse_and_execute(query_req.query)
        
        db.commit()
        
        return {"result": result, "query": query_req.query}
    except Exception as e:
        db.rollback()
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "databases": len(databases)
    }


# Backup & Restore endpoints
@app.post("/api/databases/{db_name}/backup")
async def backup_database(db_name: str, compress: bool = True, current_user = Depends(get_current_user)):
    """Create a backup of the database"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    try:
        db = databases[db_name]
        backup_file = backup_manager.create_backup(str(db.db_file), compress=compress)
        
        # Log audit
        audit_logger.log(
            action=AuditAction.BACKUP,
            user=current_user.username,
            database_name=db_name,
            details={"backup_file": backup_file},
            success=True
        )
        
        return {"message": "Backup created successfully", "file": backup_file}
    except Exception as e:
        audit_logger.log(
            action=AuditAction.BACKUP,
            user=current_user.username,
            database_name=db_name,
            success=False,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/databases/{db_name}/backups")
async def list_backups(db_name: str, current_user = Depends(get_current_user)):
    """List all backups for a database"""
    backups = backup_manager.list_backups(db_name)
    return {"backups": backups}


@app.post("/api/databases/{db_name}/restore")
async def restore_database(db_name: str, backup_file: str, current_user = Depends(get_current_user)):
    """Restore database from backup"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        restored_path = backup_manager.restore_backup(backup_file)
        
        # Reload database
        if db_name in databases:
            databases[db_name].close()
        
        db = Database(name=db_name)
        db.open()
        databases[db_name] = db
        
        # Log audit
        audit_logger.log(
            action=AuditAction.RESTORE,
            user=current_user.username,
            database_name=db_name,
            details={"backup_file": backup_file},
            success=True
        )
        
        return {"message": "Database restored successfully", "path": restored_path}
    except Exception as e:
        audit_logger.log(
            action=AuditAction.RESTORE,
            user=current_user.username,
            database_name=db_name,
            success=False,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


# Audit Log endpoints
@app.get("/api/audit/logs")
async def get_audit_logs(
    limit: int = 100,
    action: Optional[str] = None,
    user: Optional[str] = None,
    database_name: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get audit logs (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logs = audit_logger.get_logs(
        action=action,
        user=user,
        database_name=database_name,
        limit=limit
    )
    return {"logs": logs, "count": len(logs)}


@app.get("/api/audit/statistics")
async def get_audit_statistics(current_user = Depends(get_current_user)):
    """Get audit statistics (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = audit_logger.get_statistics()
    return stats


# Data Visualization endpoints
@app.get("/api/databases/{db_name}/tables/{table_name}/visualize")
async def visualize_table_data(
    db_name: str,
    table_name: str,
    chart_type: str = "bar",
    x_field: Optional[str] = None,
    y_field: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Generate visualization data for table"""
    if db_name not in databases:
        raise HTTPException(status_code=404, detail="Database not found")
    
    db = databases[db_name]
    
    try:
        table = db.get_table(table_name)
        data = table.select()
        
        if chart_type == "bar" and x_field and y_field:
            chart_data = DataVisualizer.generate_bar_chart(data, x_field, y_field)
        elif chart_type == "line" and x_field and y_field:
            chart_data = DataVisualizer.generate_line_chart(data, x_field, y_field)
        elif chart_type == "pie" and x_field and y_field:
            chart_data = DataVisualizer.generate_pie_chart(data, x_field, y_field)
        elif chart_type == "statistics":
            numeric_fields = [f for f in data[0].keys() if isinstance(data[0][f], (int, float))] if data else []
            chart_data = DataVisualizer.generate_statistics(data, numeric_fields)
        else:
            chart_data = DataVisualizer.generate_table_summary(data)
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include user management router
from pyhybriddb.api.users import router as users_router
app.include_router(users_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PyHybridDB API",
        "version": "0.1.0",
        "docs": "/docs",
        "github": "https://github.com/Adrient-tech/PyHybridDB.git"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
