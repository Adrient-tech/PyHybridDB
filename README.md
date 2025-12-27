# PyHybridDB: The Versatile Local Database (v2.0)

[![PyPI version](https://badge.fury.io/py/pyhybriddb.svg)](https://badge.fury.io/py/pyhybriddb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyHybridDB** is a high-performance, tiered storage database engine designed for modern Python applications. It unifies the best of SQL (structured), NoSQL (unstructured), and Vector (AI) worlds into a single, lightweight package.

**New in v2.0:**
*   **Tiered Architecture**: Hot Data (LSM), Analytics (Columnar), and AI (Vector).
*   **Distributed Mode**: Sharding and replication across multiple nodes (Beta).
*   **LSM Engine**: High-speed write throughput.
*   **Vector Search**: Built-in similarity search for embeddings.
*   **Columnar Analytics**: Fast aggregations using NumPy.

---

## 🚀 Key Features

*   **Hybrid Storage**: Tables (SQL), Collections (NoSQL), Vectors (AI).
*   **High Performance**: Native Caching, B-Tree Indexing, Cython Optimizations.
*   **Distributed**: Consistent Hashing, Horizontal Scaling.
*   **Zero Dependencies**: (Mostly) Pure Python + NumPy.
*   **ACID Compliant**: Write-Ahead Log (WAL) ensures durability.

---

## 📦 Installation

```bash
pip install pyhybriddb
```

---

## ⚡ Tiered Usage Guide

### Tier 1: Document/Key-Value Store (LSM Tier)
*Best for: User profiles, logs, flexible data, high-throughput writes.*

[View Full Documentation](docs/LSM_TIER.md)

```python
from pyhybriddb import Database

# Initialize (LSM Engine default)
db = Database("my_app_db", engine="lsm")
db.create()

# Create Collection
users = db.create_collection("users")

# Bulk Import
users.insert_many([
    {"name": "Alice", "role": "admin", "dept": "Engineering"},
    {"name": "Bob", "role": "staff", "dept": "Sales"}
])

# Filter / Find
alice = users.find_one({"name": "Alice"})

# Update & Delete
users.update_one({"name": "Alice"}, {"$set": {"active": True}})
users.delete_one({"name": "Bob"})
```

### Tier 2: Analytics Store (Columnar Tier)
*Best for: Financial data, sensor logs, aggregations, OLAP.*

[View Full Documentation](docs/COLUMNAR_TIER.md)

```python
# Create Analytics Table
sales = db.create_analytics_table("sales_data", {
    "amount": "float",
    "qty": "int"
})

# Insert Data
sales.insert_many([
    {"amount": 100.50, "qty": 2},
    {"amount": 200.00, "qty": 1},
])

# Aggregation (Vectorized)
total_revenue = sales.aggregate("amount", "sum")
print(f"Total Revenue: {total_revenue}")
```

### Tier 3: Vector Store (AI Tier)
*Best for: Image Search, Semantic Text Search, Embeddings.*

[View Full Documentation](docs/VECTOR_TIER.md)

```python
# Create Vector Index (dimension=128)
face_db = db.create_vector_index("faces", dimension=128)

# Add Vectors
import random
vec = [random.random() for _ in range(128)]
face_db.add(vec, record_id="user_123")

# Similarity Search
matches = face_db.search(vec, k=1)
print(f"Top Match: {matches[0]}")
```

### Tier 4: Distributed Cluster (Beta)
*Best for: TB-scale data, Horizontal Scaling.*

[View Full Documentation](docs/DISTRIBUTED.md)

```python
from pyhybriddb.distributed import DistributedCluster

# Connect to Cluster
cluster = DistributedCluster(["http://node1:8001", "http://node2:8002"])

# Write Data (Automatically Sharded)
cluster.write("users", {"name": "Alice"}, key_field="id")
```

---

## 📚 Detailed Documentation

*   [**LSM Tier (Document/KV)**](docs/LSM_TIER.md): Deep dive into WAL, MemTables, and CRUD.
*   [**Columnar Tier (Analytics)**](docs/COLUMNAR_TIER.md): How to use aggregations and schema.
*   [**Vector Tier (AI)**](docs/VECTOR_TIER.md): Managing embeddings and similarity search.
*   [**Distributed Mode**](docs/DISTRIBUTED.md): Setting up a cluster and sharding.
*   [**Configuration Guide**](CONFIGURATION_GUIDE.md): Environment variables and tuning.

**Run the Demo:**
See `examples/full_demo.py` for a complete runnable script covering all features.

---

## 📄 License

MIT License
