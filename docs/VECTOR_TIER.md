# Vector Tier (AI & Embeddings)

The **Vector Tier** enables PyHybridDB to function as a Vector Database. It stores high-dimensional vectors and provides similarity search capabilities.

---

## 🔧 Architecture

*   **Storage**: Vectors are stored in a dense matrix (NumPy array).
*   **Indexing**: Current implementation uses a Flat Index (Brute Force) for exact recall. Future versions will support HNSW.
*   **Metric**: Cosine Similarity is used for ranking.

---

## 📖 Usage Guide

### Creating an Index

```python
# Initialize DB
db = Database("ai_db")
db.create()

# Create Index
# Dimension must match your embedding model (e.g. 1536 for OpenAI ada-002)
vectors = db.create_vector_index("embeddings", dimension=1536)
```

### Adding Vectors

```python
vector = [0.12, 0.05, -0.01, ...] # 1536 floats

# Link to an external ID (e.g., from your document store)
vectors.add(vector, record_id="doc_555")
```

### Similarity Search

Find the `k` nearest neighbors to a query vector.

```python
query_vec = [0.10, 0.04, ...]

# Search top 5
results = vectors.search(query_vec, k=5)

for record_id, score in results:
    print(f"ID: {record_id}, Similarity: {score:.4f}")
```

### Integration Example

Common pattern: Store metadata in LSM Tier, and embeddings in Vector Tier.

1.  Insert document into `users` collection. Get `_id`.
2.  Generate embedding for user bio.
3.  Insert embedding into `vectors` index using `_id`.
4.  Search vectors -> Get `_id` -> Fetch full document.
