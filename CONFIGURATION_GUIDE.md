# 🔧 PyHybridDB Configuration Guide

Complete guide for configuring and optimizing PyHybridDB.

---

## 📋 Overview

PyHybridDB is a native Python database engine. It does not require installing MongoDB, PostgreSQL, or MySQL servers. It runs embedded in your application, similar to SQLite but with more features.

---

## ⚡ Performance Optimization

### **1. Indexing**

Indexes are the single most important factor for performance on large datasets. Without an index, the database performs a "Full Table Scan", reading every record from disk.

**Supported Index Types:**
- **B-Tree**: Good for range queries ($gt, $lt) and equality checks. Default for all fields.

**How to Index:**

```python
# For Collections
users = db.create_collection("users")
users.create_index("email")  # Fast lookups by email
users.create_index("age")    # Fast range queries on age

# For Tables
orders = db.create_table("orders", {"amount": "int"})
orders.create_index("amount")
```

### **2. Caching**

PyHybridDB includes an internal LRU (Least Recently Used) cache.

**Configuration:**
Currently, the cache size is fixed to 5000 records per instance. Future versions will allow configuration via environment variables.

### **3. Batch Operations**

When inserting massive amounts of data, use `insert_many` to reduce overhead.

```python
# Good
collection.insert_many(large_list_of_dicts)

# Bad
for doc in large_list_of_dicts:
    collection.insert_one(doc)
```

---

## 🔍 Query Capabilities

PyHybridDB supports a rich query syntax inspired by MongoDB.

| Operator | Description | Example |
| :--- | :--- | :--- |
| **Equality** | Exact match | `{"name": "Alice"}` |
| **$gt** | Greater than | `{"age": {"$gt": 18}}` |
| **$lt** | Less than | `{"price": {"$lt": 100}}` |
| **$gte** | Greater than or equal | `{"score": {"$gte": 50}}` |
| **$lte** | Less than or equal | `{"rating": {"$lte": 5}}` |
| **$ne** | Not equal | `{"status": {"$ne": "deleted"}}` |

**Complex Queries:**

```python
# Find active users older than 25
users.find({
    "active": True,
    "age": {"$gt": 25}
})
```

---

## 🛠️ Configuration Methods

PyHybridDB uses **environment variables** for global settings.

### **Method 1: CLI Init Command**

```bash
pyhybriddb init
```

Creates a `.env` file with defaults.

### **Method 2: Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_DB_PATH` | ./data | Default storage location |
| `LOG_LEVEL` | INFO | Logging verbosity |

---

## ❓ FAQ

### **Q: Is this faster than SQLite?**
A: For simple relational queries, SQLite is highly optimized C code and is faster. PyHybridDB shines when you need **flexibility** (JSON documents) mixed with structured data, or Python-native extensibility.

### **Q: Can I use it for production?**
A: It is suitable for small to medium-scale production apps (e.g., embedded devices, desktop apps, microservices). For massive scale (terabytes of data), distributed databases are recommended.

### **Q: How does it store data?**
A: Data is stored in a custom binary-safe block format in `.phdb` files. Metadata and indexes are managed separately.

---

*Last Updated: October 2025*
