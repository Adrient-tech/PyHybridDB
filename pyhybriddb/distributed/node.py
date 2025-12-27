"""
Node Server - REST API wrapper for a local DB instance
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from pyhybriddb import Database

app = FastAPI()

# Global DB instance for this node
db_instance: Optional[Database] = None

class WriteRequest(BaseModel):
    collection: str
    data: Dict[str, Any]

class QueryRequest(BaseModel):
    collection: str
    query: Dict[str, Any]

@app.on_event("startup")
async def startup():
    global db_instance
    path = os.environ.get("PHDB_NODE_PATH", "./data")
    name = os.environ.get("PHDB_NODE_NAME", "node")
    db_instance = Database(name, path=path, engine="lsm")
    db_instance.create()

@app.on_event("shutdown")
async def shutdown():
    if db_instance:
        db_instance.close()

@app.post("/write")
async def write_record(req: WriteRequest):
    if not db_instance:
        raise HTTPException(status_code=500, detail="DB not initialized")

    # We treat everything as collections for simplicity in distributed mode MVP
    coll = db_instance.create_collection(req.collection)
    doc_id = coll.insert_one(req.data)
    return {"id": doc_id}

@app.post("/read")
async def read_record(req: QueryRequest):
    if not db_instance:
        raise HTTPException(status_code=500, detail="DB not initialized")

    coll = db_instance.create_collection(req.collection)
    result = coll.find_one(req.query)
    return {"result": result}
