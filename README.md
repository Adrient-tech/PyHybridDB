# PyHybridDB: The Versatile Local Database (v2.0)

**PyHybridDB** is a high-performance, tiered storage database engine designed for modern Python applications. It unifies the best of SQL (structured), NoSQL (unstructured), and Vector (AI) worlds into a single, lightweight package.

**New in v2.0:**
*   **Tiered Architecture**: Hot Data (LSM), Analytics (Columnar), and AI (Vector).
*   **LSM Engine**: High-speed write throughput.
*   **Vector Search**: Built-in similarity search for embeddings.
*   **Columnar Analytics**: Fast aggregations using NumPy.

---

## 🚀 Key Features

*   **Hybrid Storage**: Tables (SQL), Collections (NoSQL), Vectors (AI).
*   **High Performance**: Native Caching, B-Tree Indexing, Cython Optimizations.
*   **Zero Dependencies**: (Mostly) Pure Python + NumPy.
*   **ACID Compliant**: Write-Ahead Log (WAL) ensures durability.

---

## 📦 Installation

```bash
pip install pyhybriddb
```

---

## ⚡ Quick Start & Examples

See `examples/full_demo.py` for a comprehensive runnable demo.

### 1. Document/Key-Value Store (LSM Tier)

Ideal for user profiles, logs, and flexible data.

```python
from pyhybriddb import Database

# Initialize (LSM Engine default for v2.0)
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
print(alice)

# Delete
users.delete_one({"name": "Bob"})
```

### 2. Analytics Store (Columnar Tier)

Ideal for financial data, sensor logs, and aggregations.

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
    {"amount": 50.25, "qty": 5}
])

# Aggregation (Vectorized)
total_revenue = sales.aggregate("amount", "sum")
print(f"Total Revenue: {total_revenue}")
```

### 3. Vector Store (AI Tier)

Ideal for Image Search, Semantic Text Search.

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

---

## 🔧 Architecture

*   **LSM Tier**: MemTable (RAM) -> WAL (Disk) -> SSTable (Disk). Optimized for writes.
*   **Columnar Tier**: NumPy arrays on disk. Optimized for OLAP scans.
*   **Vector Tier**: Flat Index / Cosine Similarity. Optimized for AI.

---

## 📚 Documentation

For detailed configuration, see [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md).

---

## 📄 License

MIT License
