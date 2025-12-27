# Distributed Mode (Beta)

PyHybridDB supports **Distributed Mode** for scaling beyond a single machine. It allows you to create a cluster of nodes that share data using **Sharding** and **Replication**.

---

## 🔧 Architecture

*   **Consistent Hashing**: Keys are mapped to nodes using a consistent hash ring. This ensures minimal data movement when nodes are added/removed.
*   **Sharding**: Data is automatically partitioned across available nodes.
*   **Replication**: (Coming Soon) Configurable replication factor for fault tolerance.

---

## 🚀 Setup Guide

### 1. Start Nodes

You need to start multiple PyHybridDB instances (nodes) on different ports or servers.

```bash
# Node 1
pyhybriddb node --name n1 --path ./data/n1 --port 8001

# Node 2
pyhybriddb node --name n2 --path ./data/n2 --port 8002

# Node 3
pyhybriddb node --name n3 --path ./data/n3 --port 8003
```

### 2. Configure Client

In your application code, use the `DistributedCluster` client.

```python
from pyhybriddb.distributed import DistributedCluster

# List of node URLs
nodes = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003"
]

# Connect
cluster = DistributedCluster(nodes)
```

### 3. Usage

The client API abstracts away the complexity of sharding.

#### Write Data
```python
# The 'key_field' determines which node gets the data
cluster.write("users", {"id": "u100", "name": "Alice"}, key_field="id")
```

#### Read Data
```python
# The client hashes 'u100' -> Finds correct node -> Fetches data
user = cluster.read("users", {"id": "u100"}, key_field="id")
```

---

## ⚠️ Limitations (Beta)

*   **Rebalancing**: Automatic data migration when adding nodes is not yet fully automatic.
*   **Transactions**: Distributed transactions (Two-Phase Commit) are not yet supported. Operations are atomic per-node.
*   **Querying**: Scatter-gather queries (queries without shard key) broadcast to all nodes, which can be slower.
