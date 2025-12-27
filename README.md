# PyHybridDB: The Versatile Local Database

**PyHybridDB** is a high-performance, tiered storage database engine designed for modern Python applications. It unifies the best of SQL (structured), NoSQL (unstructured), and Vector (AI) worlds into a single, lightweight package.

It features a **Hybrid Tiered Storage Architecture**:

1.  **LSM-Tree Tier (Hot Data)**: Log-Structured Merge Tree for high-speed writes and Key-Value access (Cython optimized).
2.  **Columnar Tier (Analytics)**: NumPy-backed columnar storage for OLAP aggregation.
3.  **Vector Tier (AI)**: Vector storage and similarity search for Embeddings.

---

## 🚀 Key Features

*   **LSM-Tree Engine**: High throughput writes using MemTables and SSTables.
*   **Vector Search**: Built-in similarity search for AI applications.
*   **Analytics**: Columnar storage for fast SUM/AVG/COUNT queries.
*   **Hybrid Storage**: Support for Tables, Collections, and Vectors.
*   **Zero Dependencies**: (Mostly) Pure Python + NumPy + Optional optimizations.

---

## 📦 Installation

```bash
pip install pyhybriddb numpy
```

---

## ⚡ Tiered Usage Guide

### Tier 1: Document/Key-Value Store (MongoDB-like)

Ideal for flexible data structures, user profiles, or logs.

```python
from pyhybriddb import Database

# 1. Initialize DB
db = Database("my_app_db", engine="lsm")
db.create()

# 2. Create Collection
users = db.create_collection("users")

# 3. CRUD Operations
# Insert
uid = users.insert_one({"name": "Alice", "role": "admin", "meta": {"login": "today"}})

# Find
admin = users.find_one({"role": "admin"})

# Update
users.update_one({"name": "Alice"}, {"$set": {"active": True}})

# Delete
users.delete_one({"name": "Alice"})
```

### Tier 2: SQL/Analytics Store (ClickHouse-like)

Ideal for large datasets needing aggregation (logs, financial data, sensor readings).

```python
# 1. Create Analytics Table
# Schema defines types: 'int', 'float', 'str'
logs = db.create_analytics_table("server_logs", {
    "timestamp": "int",
    "cpu_usage": "float",
    "requests": "int"
})

# 2. Insert Data (Batch is recommended)
import time
batch = []
for i in range(1000):
    batch.append({
        "timestamp": int(time.time()),
        "cpu_usage": 0.45,
        "requests": 10
    })
logs.insert_many(batch)

# 3. Aggregation (Fast Vectorized Operations)
total_requests = logs.aggregate("requests", "sum")
avg_cpu = logs.aggregate("cpu_usage", "avg")

# 4. Select
recent_logs = logs.select(columns=["cpu_usage"], limit=5)
```

### Tier 3: Vector Store (Milvus-like)

Ideal for AI embeddings, image search, or semantic text search.

```python
# 1. Create Vector Index
# Define dimension (e.g., 128 for small models, 1536 for OpenAI)
vectors = db.create_vector_index("image_embeddings", dimension=128)

# 2. Add Vectors
# You can link the vector to a record ID from your document store
vector_data = [0.1, 0.5, ...] # list of 128 floats
vectors.add(vector_data, record_id="image_123")

# 3. Similarity Search
# Find top 5 similar items
query_vec = [0.1, 0.4, ...]
results = vectors.search(query_vec, k=5)

# Returns: [('image_123', 0.98), ('image_456', 0.85)]
for vid, score in results:
    print(f"Found {vid} with score {score}")
```

---

## 🔧 Architecture

*   **LSM Engine**: MemTable (RAM) -> WAL (Disk) -> SSTable (Disk).
*   **Columnar Engine**: Data stored as contiguous NumPy arrays (`.npy`) per column.
*   **Vector Engine**: Flat Index using NumPy for vectorized Cosine Similarity.

---

## 📄 License

MIT License
