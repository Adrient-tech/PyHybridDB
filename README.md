# PyHybridDB: The Versatile Local Database

**PyHybridDB** is a high-performance, tiered storage database engine designed for modern Python applications. It unifies the best of SQL (structured) and NoSQL (unstructured) worlds into a single, lightweight package.

It now features a **Hybrid Tiered Storage Architecture**:

1.  **LSM-Tree Tier (Hot Data)**: Log-Structured Merge Tree for high-speed writes and Key-Value access (Cython optimized).
2.  **Columnar Tier (Analytics)**: (Coming Soon) Columnar storage for OLAP.
3.  **Vector Tier (AI)**: (Coming Soon) Vector search for embeddings.

---

## 🚀 Key Features

*   **LSM-Tree Engine**: High throughput writes using MemTables and SSTables.
*   **Cython Optimized**: Critical paths compiled to C for performance.
*   **Hybrid Storage**: Support for Tables and Collections.
*   **Zero Dependencies**: (Mostly) Pure Python + Optional optimizations.
*   **ACID Compliant**: Write-Ahead Log (WAL) ensures durability.

---

## 📦 Installation

```bash
pip install pyhybriddb
```

---

## ⚡ Quick Start

### 1. Key-Value / Document Store (LSM Engine)

The default engine uses an LSM-Tree for fast writes.

```python
from pyhybriddb import Database

# Initialize (uses LSM Engine by default)
db = Database("my_fast_db", engine="lsm")
db.create()

# Create a collection
users = db.create_collection("users")

# Insert documents (Written to WAL + MemTable -> Flushed to SSTable)
users.insert_one({"name": "Alice", "age": 30, "skills": ["python", "db"]})

# Query
results = users.find({"name": "Alice"})
print(results)

db.close()
```

---

## 🔧 Architecture

### Phase 1: The "Speed" Foundation
*   **MemTable**: In-memory sorted buffer.
*   **WAL**: Append-only log for crash recovery.
*   **SSTable**: Immutable sorted files on disk, read via `mmap`.
*   **Compaction**: Background merging of SSTables (Basic implementation).

---

## 📚 Documentation

For detailed configuration, see [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md).

---

## 📄 License

MIT License
