# Columnar Tier (Analytics & OLAP)

The **Columnar Tier** stores data column-by-column rather than row-by-row. This is ideal for analytical queries (OLAP) where you often aggregate specific columns over millions of rows.

---

## 🔧 Architecture

*   **Storage**: Each column is stored as a contiguous NumPy array (`.npy` file) on disk.
*   **Vectorization**: Operations use SIMD (Single Instruction, Multiple Data) via NumPy for massive speedups.
*   **Compression**: (Future) Arrays can be compressed with LZ4/ZSTD.

---

## 📖 Usage Guide

### Creating a Table

You must define a schema. Supported types: `int`, `float`, `str`.

```python
# Initialize DB
db = Database("analytics_db")
db.create()

# Create Table
metrics = db.create_analytics_table("server_metrics", {
    "timestamp": "int",
    "cpu_load": "float",
    "region": "str"
})
```

### Batch Insertion

Columnar stores prefer batch inserts. Single-row inserts are slower.

```python
data = []
for i in range(1000):
    data.append({
        "timestamp": 1600000000 + i,
        "cpu_load": 0.45,
        "region": "us-east-1"
    })

metrics.insert_many(data)
```

### Aggregations

Aggregations run on the entire column (or filtered subset) instantly.

```python
# Sum
total_load = metrics.aggregate("cpu_load", "sum")

# Average
avg_load = metrics.aggregate("cpu_load", "avg")

# Max/Min
peak_load = metrics.aggregate("cpu_load", "max")
```

### Selecting Data

Retrieve specific columns to minimize I/O.

```python
# Get only CPU load for first 10 rows
rows = metrics.select(columns=["cpu_load"], limit=10)
```
