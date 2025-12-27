# LSM Tier (Document & Key-Value Store)

The **LSM Tier** is the default storage engine in PyHybridDB v2.0. It is optimized for high-throughput write operations and fast key-value lookups.

---

## 🔧 Architecture

It uses a **Log-Structured Merge Tree (LSM-Tree)** architecture:

1.  **WAL (Write-Ahead Log)**: Every write is first appended to a log file on disk to ensure durability (ACID compliance).
2.  **MemTable**: Data is then stored in an in-memory sorted structure (SkipList logic).
3.  **SSTable (Sorted String Table)**: When the MemTable is full, it is flushed to disk as an immutable SSTable.
4.  **Compaction**: Background processes merge SSTables to reclaim space and optimize reads.

---

## ⚡ Performance

*   **Writes**: extremely fast (append-only).
*   **Reads**: fast (uses Bloom Filters and sparse indexes).
*   **Optimizations**: Critical paths are compiled with Cython.

---

## 📖 Usage Guide

### Initialization

```python
from pyhybriddb import Database

# Initialize with LSM Engine
db = Database("my_db", engine="lsm")
db.create()
```

### Collections (Document Store)

Collections are schema-less containers for JSON documents.

```python
users = db.create_collection("users")
```

### CRUD Operations

#### Insert
```python
# Single Insert
users.insert_one({"name": "Alice", "age": 30})

# Bulk Insert (Recommended for large imports)
users.insert_many([
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
])
```

#### Find / Query
```python
# Find One by ID
user = users.find_one({"_id": "unique-uuid"})

# Find Many with Filter
admins = users.find({"role": "admin"})

# Complex Query
seniors = users.find({"age": {"$gt": 50}})
```

#### Update
```python
# Update One
users.update_one({"name": "Alice"}, {"$set": {"age": 31}})

# Update Many
users.update_many({"role": "staff"}, {"$set": {"active": True}})
```

#### Delete
```python
# Delete One
users.delete_one({"name": "Bob"})

# Delete Many
users.delete_many({"active": False})
```

---

## 🛠️ Tuning

You can adjust the MemTable size via `lsm_memtable_size` in configuration to balance RAM usage vs I/O frequency.
