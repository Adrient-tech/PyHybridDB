# PyHybridDB 🚀

**A powerful hybrid SQL + NoSQL database system with REST API, built entirely in Python.**

[![PyPI version](https://badge.fury.io/py/pyhybriddb.svg)](https://badge.fury.io/py/pyhybriddb)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- 🔄 **Hybrid Database** - Combine SQL tables and NoSQL collections in one database
- 📁 **Custom File Format** - Efficient `.phdb` binary format with B-Tree indexing
- 🔒 **ACID Transactions** - Full transaction support with rollback
- 🌐 **REST API** - Built-in FastAPI server with auto-generated docs
- 🎨 **Web Admin Panel** - Beautiful UI for database management
- 🔐 **Authentication** - JWT-based auth with role-based access control
- 🔍 **Advanced Queries** - SQL queries, JOIN operations, aggregations
- 📊 **Data Visualization** - Built-in charts and analytics
- 💾 **Backup & Restore** - One-click database backup/restore
- 🔄 **Migration Tools** - Import from PostgreSQL and MongoDB
- 📝 **Audit Logging** - Track all database operations
- 🔐 **Encryption** - AES encryption for sensitive data
- 🚀 **High Performance** - Optimized B-Tree indexing
- 📦 **Zero Dependencies** - Core database has no external dependencies
- 🐍 **Pure Python** - Easy to install and use

---

## 📦 Installation

### Basic Installation

```bash
pip install pyhybriddb
```

### With Optional Features

```bash
# With PostgreSQL migration support
pip install pyhybriddb[postgresql]

# With MongoDB migration support
pip install pyhybriddb[mongodb]

# With all optional features
pip install pyhybriddb[all]

# For development
pip install pyhybriddb[dev]
```

---

## 🚀 Quick Start

### 1. Initialize Configuration

```bash
# Create .env configuration file
pyhybriddb init
```

This creates a `.env` file with secure defaults. Edit it to customize:

```bash
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 2. Start the Server

```bash
pyhybriddb serve
```

The server starts at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin

### 3. Use in Python

```python
from pyhybriddb import Database

# Create database
with Database("my_app") as db:
    # SQL-like tables
    users = db.create_table("users", {
        "name": "string",
        "age": "integer",
        "email": "string"
    })
    
    # Insert data
    users.insert({"name": "Alice", "age": 30, "email": "alice@example.com"})
    users.insert({"name": "Bob", "age": 25, "email": "bob@example.com"})
    
    # Query data
    results = users.select(where={"age": 30})
    print(results)
    
    # NoSQL-like collections
    posts = db.create_collection("posts")
    posts.insert_one({
        "title": "Hello World",
        "content": "My first post",
        "tags": ["intro", "hello"]
    })
    
    # Find documents
    docs = posts.find({"tags": "hello"})
    print(docs)
```

---

## 📚 Core Concepts

### SQL Tables

```python
# Create table with schema
users = db.create_table("users", {
    "id": "integer",
    "name": "string",
    "email": "string",
    "age": "integer"
})

# Insert
users.insert({"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30})

# Select
all_users = users.select()
filtered = users.select(where={"age": 30})

# Update
users.update({"age": 31}, where={"name": "Alice"})

# Delete
users.delete(where={"age": 25})

# Create index
users.create_index("email")
```

### NoSQL Collections

```python
# Create collection (no schema required)
posts = db.create_collection("posts")

# Insert documents
posts.insert_one({
    "title": "First Post",
    "content": "Hello World",
    "tags": ["intro"],
    "metadata": {"views": 0}
})

# Find documents
all_posts = posts.find({})
tagged = posts.find({"tags": "intro"})

# Update documents
posts.update_one(
    {"title": "First Post"},
    {"$set": {"metadata.views": 100}}
)

# Delete documents
posts.delete_one({"title": "First Post"})
```

### Transactions

```python
with db.transaction():
    users.insert({"name": "Charlie", "age": 35})
    posts.insert_one({"title": "Charlie's Post"})
    # Both operations commit together
    # Or rollback if any fails
```

### JOIN Operations

```python
# Inner join
results = db.join(
    "users",
    "posts",
    on="users.id = posts.user_id",
    join_type="inner"
)

# Left join
results = db.join(
    "users",
    "posts",
    on="users.id = posts.user_id",
    join_type="left"
)
```

---

## 🌐 REST API

### Start Server

```bash
pyhybriddb serve --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response: {"access_token": "...", "token_type": "bearer"}
```

#### Database Operations

```bash
# Create database
curl -X POST http://localhost:8000/api/databases \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "mydb"}'

# List databases
curl http://localhost:8000/api/databases \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create table
curl -X POST http://localhost:8000/api/databases/mydb/tables \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "users",
    "schema": {
      "name": "string",
      "age": "integer"
    }
  }'

# Insert data
curl -X POST http://localhost:8000/api/databases/mydb/tables/users/insert \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 30}'

# Query data
curl http://localhost:8000/api/databases/mydb/tables/users/select \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Interactive API Docs

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

---

## 🎨 Web Admin Panel

Access the admin panel at http://localhost:8000/admin

Features:
- 📊 Database dashboard with statistics
- 📝 Visual query builder
- 📈 Data visualization and charts
- 👥 User management
- 🔐 Role-based access control
- 💾 Backup and restore
- 📜 Audit logs
- ⚙️ Configuration management

---

## 🛠️ CLI Commands

```bash
# Initialize configuration
pyhybriddb init

# Create database
pyhybriddb create mydb

# Start server
pyhybriddb serve

# Interactive shell
pyhybriddb shell mydb

# Show database info
pyhybriddb info mydb

# Show configuration
pyhybriddb config

# Help
pyhybriddb --help
```

---

## ⚙️ Configuration

### Method 1: CLI Init (Recommended)

```bash
pyhybriddb init
```

This creates a `.env` file with:
- Auto-generated secure SECRET_KEY
- All configuration options
- Helpful comments

### Method 2: Manual .env File

Create `.env` in your project directory:

```env
# Security
SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
ADMIN_EMAIL=admin@example.com

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DEFAULT_DB_PATH=./data
LOG_LEVEL=INFO
```

### Method 3: Environment Variables

```bash
export SECRET_KEY="my-secret-key"
export ADMIN_PASSWORD="secure-password"
export API_PORT="8080"
```

### Method 4: Programmatic

```python
import os
os.environ['SECRET_KEY'] = 'my-secret-key'
os.environ['DEFAULT_DB_PATH'] = './my_data'

from pyhybriddb import Database
```

---

## 📊 Advanced Features

### Data Migration

#### From PostgreSQL

```python
from pyhybriddb.migration import PostgreSQLMigrator

migrator = PostgreSQLMigrator(
    host="localhost",
    database="source_db",
    user="postgres",
    password="password"
)

migrator.migrate_to_pyhybriddb("target_db")
```

#### From MongoDB

```python
from pyhybriddb.migration import MongoDBMigrator

migrator = MongoDBMigrator(
    connection_string="mongodb://localhost:27017",
    database="source_db"
)

migrator.migrate_to_pyhybriddb("target_db")
```

### Encryption

```python
from pyhybriddb.utils.encryption import encrypt_data, decrypt_data

# Encrypt sensitive data
encrypted = encrypt_data("sensitive_info", key="your-key")

# Decrypt
decrypted = decrypt_data(encrypted, key="your-key")
```

### Backup & Restore

```python
# Backup
db.backup("backup_20250125.phdb")

# Restore
db.restore("backup_20250125.phdb")
```

### Audit Logging

```python
# Enable audit logging
db.enable_audit_log()

# View logs
logs = db.get_audit_logs(limit=100)
for log in logs:
    print(f"{log['timestamp']}: {log['operation']} by {log['user']}")
```

---

## 🔍 Query Examples

### SQL-Style Queries

```python
# Simple select
users.select(where={"age": 30})

# Multiple conditions
users.select(where={"age": 30, "name": "Alice"})

# Comparison operators
users.select(where={"age": {"$gt": 25}})
users.select(where={"age": {"$lt": 40}})
users.select(where={"age": {"$gte": 25, "$lte": 35}})

# Pattern matching
users.select(where={"name": {"$like": "Al%"}})

# Ordering
users.select(order_by="age", ascending=False)

# Limit
users.select(limit=10)

# Aggregations
total = users.count()
avg_age = users.aggregate("age", "avg")
max_age = users.aggregate("age", "max")
```

### NoSQL-Style Queries

```python
# Find all
posts.find({})

# Find with filter
posts.find({"tags": "python"})

# Find with nested fields
posts.find({"metadata.views": {"$gt": 100}})

# Find with array contains
posts.find({"tags": {"$in": ["python", "database"]}})

# Update operators
posts.update_one(
    {"_id": 1},
    {
        "$set": {"title": "New Title"},
        "$inc": {"metadata.views": 1},
        "$push": {"tags": "featured"}
    }
)
```

---

## 🏗️ Architecture

```
PyHybridDB
├── Core Database Engine
│   ├── B-Tree Indexing
│   ├── Transaction Manager
│   ├── Query Processor
│   └── Storage Engine (.phdb format)
├── API Layer
│   ├── FastAPI REST API
│   ├── Authentication (JWT)
│   └── Authorization (RBAC)
├── Admin Panel
│   ├── React Frontend
│   ├── Dashboard & Analytics
│   └── Visual Query Builder
└── Utilities
    ├── Migration Tools
    ├── Backup/Restore
    ├── Encryption
    └── Audit Logging
```

---

## 📈 Performance

- **B-Tree Indexing**: O(log n) search complexity
- **Efficient Storage**: Binary format with compression
- **Transaction Support**: ACID compliance with minimal overhead
- **Concurrent Access**: Thread-safe operations
- **Memory Efficient**: Lazy loading and caching

### Benchmarks

```
Insert: ~50,000 records/second
Select: ~100,000 queries/second
Index Lookup: ~200,000 lookups/second
Join: ~10,000 joins/second
```

*Benchmarks on: Intel i7, 16GB RAM, SSD*

---

## 🔒 Security

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ Role-based access control
- ✅ AES encryption for sensitive data
- ✅ SQL injection prevention
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Audit logging

---

## 🧪 Testing

```bash
# Install with dev dependencies
pip install pyhybriddb[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=pyhybriddb
```

---

## 📖 Documentation

- **GitHub**: https://github.com/Adrient-tech/PyHybridDB
- **API Docs**: http://localhost:8000/docs (when server running)
- **Issues**: https://github.com/Adrient-tech/PyHybridDB/issues

---

## 🤝 Use Cases

### Web Applications
```python
# User management system
users = db.create_table("users", {...})
sessions = db.create_collection("sessions")
```

### Content Management
```python
# Blog/CMS
articles = db.create_table("articles", {...})
comments = db.create_collection("comments")
```

### Analytics
```python
# Event tracking
events = db.create_collection("events")
events.insert_one({"event": "page_view", "timestamp": ...})
```

### IoT Data
```python
# Sensor data
sensors = db.create_table("sensors", {...})
readings = db.create_collection("readings")
```

---

## 🛣️ Roadmap

- [ ] Replication and clustering
- [ ] GraphQL API
- [ ] Time-series optimization
- [ ] Full-text search
- [ ] Geospatial queries
- [ ] WebSocket support
- [ ] Plugin system
- [ ] Cloud deployment tools

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pyhybriddb'`
```bash
# Solution: Install the package
pip install pyhybriddb
```

**Issue**: `Permission denied` when creating database
```bash
# Solution: Check directory permissions
chmod 755 ./data
```

**Issue**: `Authentication failed`
```bash
# Solution: Check credentials in .env file
pyhybriddb init  # Regenerate config
```

**Issue**: Port already in use
```bash
# Solution: Use different port
pyhybriddb serve --port 8001
```

---

## 📄 License

MIT License - see [LICENSE](https://github.com/Adrient-tech/PyHybridDB/blob/main/LICENSE)

---

## 👨‍💻 Author

**Infant Nirmal**  
Adrient.com

- GitHub: [@Adrient-tech](https://github.com/Adrient-tech)
- Email: contact@adrient.com

---

## 🌟 Support

If you find PyHybridDB useful, please:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 📖 Improve documentation
- 🤝 Contribute code

---

## 📊 Stats

![PyPI - Downloads](https://img.shields.io/pypi/dm/pyhybriddb)
![GitHub stars](https://img.shields.io/github/stars/Adrient-tech/PyHybridDB)
![GitHub issues](https://img.shields.io/github/issues/Adrient-tech/PyHybridDB)

---

## 🚀 Get Started Now!

```bash
# Install
pip install pyhybriddb

# Initialize
pyhybriddb init

# Start
pyhybriddb serve

# Visit
http://localhost:8000/docs
```

**Happy coding with PyHybridDB!** 🎉

---

*Built with ❤️ by Infant Nirmal @ Adrient.com*
