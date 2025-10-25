"""
Basic usage examples for PyHybridDB
"""

from pyhybriddb import Database

# Example 1: Create a database and table (SQL-like)
def example_sql_operations():
    print("=== SQL Operations Example ===\n")
    
    # Create and open database
    with Database(name="example_db", path="./data") as db:
        
        # Create a table with schema
        users_table = db.create_table("users", {
            "name": "string",
            "age": "integer",
            "email": "string"
        })
        
        print(f"Created table: {users_table}")
        
        # Insert records
        user1_id = users_table.insert({
            "name": "Alice",
            "age": 30,
            "email": "alice@example.com"
        })
        
        user2_id = users_table.insert({
            "name": "Bob",
            "age": 25,
            "email": "bob@example.com"
        })
        
        print(f"Inserted users with IDs: {user1_id}, {user2_id}")
        
        # Select all records
        all_users = users_table.select()
        print(f"\nAll users: {all_users}")
        
        # Select with WHERE clause
        young_users = users_table.select(where={"age": 25})
        print(f"\nUsers aged 25: {young_users}")
        
        # Update records
        updated = users_table.update(
            where={"name": "Alice"},
            updates={"age": 31}
        )
        print(f"\nUpdated {updated} record(s)")
        
        # Verify update
        alice = users_table.select(where={"name": "Alice"})
        print(f"Alice after update: {alice}")
        
        # Delete records
        deleted = users_table.delete(where={"name": "Bob"})
        print(f"\nDeleted {deleted} record(s)")
        
        # Final count
        print(f"Total users: {users_table.count()}")


# Example 2: NoSQL operations with collections
def example_nosql_operations():
    print("\n\n=== NoSQL Operations Example ===\n")
    
    with Database(name="blog_db", path="./data") as db:
        
        # Create a collection (schema-less)
        posts = db.create_collection("posts")
        
        print(f"Created collection: {posts}")
        
        # Insert documents
        post1_id = posts.insert_one({
            "title": "Getting Started with PyHybridDB",
            "content": "PyHybridDB is a hybrid database...",
            "author": "Alice",
            "tags": ["database", "python", "tutorial"],
            "views": 100
        })
        
        post2_id = posts.insert_one({
            "title": "Advanced Query Techniques",
            "content": "Learn how to write complex queries...",
            "author": "Bob",
            "tags": ["database", "advanced"],
            "views": 50
        })
        
        print(f"Inserted posts with IDs: {post1_id}, {post2_id}")
        
        # Find all documents
        all_posts = posts.find()
        print(f"\nAll posts: {len(all_posts)} found")
        for post in all_posts:
            print(f"  - {post['title']} by {post['author']}")
        
        # Find with query
        alice_posts = posts.find({"author": "Alice"})
        print(f"\nAlice's posts: {alice_posts}")
        
        # Update document
        posts.update_one(
            {"author": "Alice"},
            {"$set": {"views": 150}}
        )
        print("\nUpdated Alice's post views")
        
        # Increment views
        posts.update_one(
            {"author": "Bob"},
            {"$inc": {"views": 10}}
        )
        print("Incremented Bob's post views")
        
        # Aggregate
        popular_posts = posts.aggregate([
            {"$match": {"views": {"$gt": 0}}},
            {"$sort": {"views": -1}},
            {"$limit": 5}
        ])
        print(f"\nPopular posts: {popular_posts}")
        
        # Count documents
        total = posts.count_documents()
        print(f"\nTotal posts: {total}")


# Example 3: Hybrid operations (SQL + NoSQL)
def example_hybrid_operations():
    print("\n\n=== Hybrid Operations Example ===\n")
    
    with Database(name="hybrid_db", path="./data") as db:
        
        # Create both table and collection
        customers = db.create_table("customers", {
            "name": "string",
            "email": "string",
            "status": "string"
        })
        
        orders = db.create_collection("orders")
        
        # Insert structured data
        customer_id = customers.insert({
            "name": "Charlie",
            "email": "charlie@example.com",
            "status": "active"
        })
        
        # Insert unstructured data
        order_id = orders.insert_one({
            "customer_id": customer_id,
            "items": [
                {"product": "Laptop", "price": 999.99, "quantity": 1},
                {"product": "Mouse", "price": 29.99, "quantity": 2}
            ],
            "total": 1059.97,
            "status": "pending",
            "metadata": {
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0..."
            }
        })
        
        print(f"Created customer {customer_id} with order {order_id}")
        
        # Query both
        customer_data = customers.select(where={"id": customer_id})
        order_data = orders.find({"customer_id": customer_id})
        
        print(f"\nCustomer: {customer_data}")
        print(f"Orders: {order_data}")
        
        # Show database stats
        stats = db.get_stats()
        print(f"\nDatabase stats:")
        print(f"  Tables: {stats['table_count']}")
        print(f"  Collections: {stats['collection_count']}")
        print(f"  File size: {stats['file_size']} bytes")


# Example 4: Using queries
def example_queries():
    print("\n\n=== Query Examples ===\n")
    
    with Database(name="query_db", path="./data") as db:
        
        # Create table
        db.create_table("products", {
            "name": "string",
            "price": "float",
            "category": "string"
        })
        
        # Use Connection for queries
        from pyhybriddb.core.connection import Connection
        
        conn = Connection(db)
        
        # SQL queries
        print("Executing SQL queries:")
        
        # INSERT
        conn.execute("INSERT INTO products (name, price, category) VALUES ('Laptop', 999.99, 'Electronics')")
        conn.execute("INSERT INTO products (name, price, category) VALUES ('Book', 19.99, 'Books')")
        
        # SELECT
        result = conn.execute("SELECT * FROM products")
        print(f"All products: {result}")
        
        # SELECT with WHERE
        result = conn.execute("SELECT * FROM products WHERE category = 'Electronics'")
        print(f"Electronics: {result}")
        
        conn.commit()
        
        # Create collection for NoSQL queries
        db.create_collection("reviews")
        
        # NoSQL queries
        print("\nExecuting NoSQL queries:")
        
        conn.execute('db.reviews.insertOne({"product": "Laptop", "rating": 5, "comment": "Great!"})')
        conn.execute('db.reviews.insertOne({"product": "Book", "rating": 4, "comment": "Good read"})')
        
        result = conn.execute('db.reviews.find({})')
        print(f"All reviews: {result}")
        
        conn.commit()
        conn.close()


if __name__ == "__main__":
    print("PyHybridDB Examples\n")
    print("=" * 50)
    
    try:
        example_sql_operations()
        example_nosql_operations()
        example_hybrid_operations()
        example_queries()
        
        print("\n" + "=" * 50)
        print("\n✓ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
