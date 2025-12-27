# PyHybridDB: The Versatile Local Database (v2.0)

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
... (Same as before)

### Tier 4: Distributed Cluster (Beta)

For TB-scale data, run multiple PyHybridDB nodes and connect them via the Distributed Client.

**1. Start Nodes**
```bash
# Terminal 1
pyhybriddb node --name node1 --path ./data/n1 --port 8001

# Terminal 2
pyhybriddb node --name node2 --path ./data/n2 --port 8002
```

**2. Connect & Shard Data**
```python
from pyhybriddb.distributed import DistributedCluster

# Initialize Cluster
cluster = DistributedCluster(["http://localhost:8001", "http://localhost:8002"])

# Write Data (Automatically Sharded)
# Key 'user_123' determines which node stores this record.
cluster.write("users", {"name": "Alice", "role": "admin"}, key_field="id")

# Read Data (Automatically Routed)
user = cluster.read("users", {"id": "user_123"}, key_field="id")
print(user)
```

---

## ❓ FAQ

### **Q: Can I use it for massive scale (Terabytes)?**
A: **Yes**, by using the **Distributed Mode**. You can shard data across multiple nodes (processes or servers) using Consistent Hashing. This allows horizontal scaling beyond a single machine's limits.

### **Q: Is it suitable for production?**
A: Yes. The local tiered engine is production-ready for small-medium apps. The Distributed Mode is currently in Beta but functional for scaling requirements.

---

## 📄 License

MIT License
