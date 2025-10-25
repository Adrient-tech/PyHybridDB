"""
PyHybridDB Demo Script
Demonstrates all major features of the hybrid database system
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pyhybriddb import Database
from pyhybriddb.core.connection import Connection


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_database_creation():
    """Demo: Creating a database"""
    print_section("1. DATABASE CREATION")
    
    db = Database(name="demo_db", path="./demo_data")
    db.create()
    
    print("✓ Created database: demo_db")
    print(f"  Location: {db.db_file}")
    
    return db


def demo_sql_operations(db):
    """Demo: SQL-like table operations"""
    print_section("2. SQL OPERATIONS (Structured Data)")
    
    # Create table
    print("Creating 'employees' table...")
    employees = db.create_table("employees", {
        "name": "string",
        "department": "string",
        "salary": "float",
        "age": "integer"
    })
    print(f"✓ Table created: {employees}")
    
    # Insert records
    print("\nInserting employee records...")
    employees.insert({"name": "Alice Johnson", "department": "Engineering", "salary": 95000.0, "age": 32})
    employees.insert({"name": "Bob Smith", "department": "Marketing", "salary": 75000.0, "age": 28})
    employees.insert({"name": "Carol White", "department": "Engineering", "salary": 105000.0, "age": 35})
    employees.insert({"name": "David Brown", "department": "Sales", "salary": 80000.0, "age": 30})
    print(f"✓ Inserted {employees.count()} records")
    
    # Select all
    print("\nSELECT * FROM employees:")
    all_employees = employees.select()
    for emp in all_employees:
        print(f"  {emp['name']:20} | {emp['department']:15} | ${emp['salary']:,.2f}")
    
    # Select with WHERE
    print("\nSELECT * FROM employees WHERE department = 'Engineering':")
    engineers = employees.select(where={"department": "Engineering"})
    for emp in engineers:
        print(f"  {emp['name']:20} | ${emp['salary']:,.2f}")
    
    # Update
    print("\nUPDATE employees SET salary = 98000 WHERE name = 'Alice Johnson':")
    employees.update(where={"name": "Alice Johnson"}, updates={"salary": 98000.0})
    alice = employees.select(where={"name": "Alice Johnson"})[0]
    print(f"  ✓ Alice's new salary: ${alice['salary']:,.2f}")
    
    # Count
    print(f"\nTotal employees: {employees.count()}")


def demo_nosql_operations(db):
    """Demo: NoSQL-like collection operations"""
    print_section("3. NOSQL OPERATIONS (Unstructured Data)")
    
    # Create collection
    print("Creating 'blog_posts' collection...")
    posts = db.create_collection("blog_posts")
    print(f"✓ Collection created: {posts}")
    
    # Insert documents
    print("\nInserting blog posts...")
    posts.insert_one({
        "title": "Introduction to PyHybridDB",
        "author": "Alice Johnson",
        "content": "PyHybridDB combines the best of SQL and NoSQL...",
        "tags": ["database", "python", "tutorial"],
        "views": 1250,
        "published": True,
        "metadata": {
            "created_at": "2024-01-15",
            "last_modified": "2024-01-20"
        }
    })
    
    posts.insert_one({
        "title": "Advanced Query Techniques",
        "author": "Carol White",
        "content": "Learn how to write complex queries in PyHybridDB...",
        "tags": ["database", "advanced", "queries"],
        "views": 890,
        "published": True,
        "metadata": {
            "created_at": "2024-01-18",
            "last_modified": "2024-01-18"
        }
    })
    
    posts.insert_one({
        "title": "Database Performance Tips",
        "author": "Alice Johnson",
        "content": "Optimize your database performance with these tips...",
        "tags": ["performance", "optimization"],
        "views": 2100,
        "published": False,
        "metadata": {
            "created_at": "2024-01-22",
            "last_modified": "2024-01-23"
        }
    })
    
    print(f"✓ Inserted {posts.count_documents()} documents")
    
    # Find all
    print("\ndb.blog_posts.find():")
    all_posts = posts.find()
    for post in all_posts:
        print(f"  📝 {post['title']}")
        print(f"     Author: {post['author']} | Views: {post['views']} | Tags: {', '.join(post['tags'])}")
    
    # Find with query
    print("\ndb.blog_posts.find({author: 'Alice Johnson'}):")
    alice_posts = posts.find({"author": "Alice Johnson"})
    for post in alice_posts:
        print(f"  📝 {post['title']} ({post['views']} views)")
    
    # Update with $set
    print("\ndb.blog_posts.updateOne({title: '...'}, {$set: {published: true}}):")
    posts.update_one(
        {"title": "Database Performance Tips"},
        {"$set": {"published": True}}
    )
    print("  ✓ Updated post status")
    
    # Update with $inc
    print("\ndb.blog_posts.updateOne({title: '...'}, {$inc: {views: 100}}):")
    posts.update_one(
        {"title": "Introduction to PyHybridDB"},
        {"$inc": {"views": 100}}
    )
    updated_post = posts.find_one({"title": "Introduction to PyHybridDB"})
    print(f"  ✓ New view count: {updated_post['views']}")
    
    # Aggregate
    print("\ndb.blog_posts.aggregate([{$sort: {views: -1}}, {$limit: 2}]):")
    popular = posts.aggregate([
        {"$sort": {"views": -1}},
        {"$limit": 2}
    ])
    for post in popular:
        print(f"  🔥 {post['title']} - {post['views']} views")


def demo_hybrid_queries(db):
    """Demo: Hybrid SQL and NoSQL queries"""
    print_section("4. HYBRID QUERIES")
    
    conn = Connection(db)
    
    # SQL query
    print("SQL Query: SELECT * FROM employees WHERE department = 'Engineering'")
    result = conn.execute("SELECT * FROM employees WHERE department = 'Engineering'")
    print(f"  Results: {len(result)} records")
    for emp in result:
        print(f"    • {emp['name']}")
    
    # NoSQL query
    print("\nNoSQL Query: db.blog_posts.find({published: true})")
    result = conn.execute('db.blog_posts.find({"published": true})')
    print(f"  Results: {len(result)} documents")
    for post in result:
        print(f"    • {post['title']}")
    
    conn.commit()
    conn.close()


def demo_statistics(db):
    """Demo: Database statistics"""
    print_section("5. DATABASE STATISTICS")
    
    stats = db.get_stats()
    
    print(f"Database Name:     {stats['name']}")
    print(f"File Path:         {stats['path']}")
    print(f"File Size:         {stats['file_size']:,} bytes")
    print(f"Tables:            {stats['table_count']}")
    print(f"Collections:       {stats['collection_count']}")
    print(f"Indexes:           {stats['indexes']}")
    print(f"Status:            {'Open' if stats['is_open'] else 'Closed'}")
    
    print("\nTable Details:")
    for table_name in db.list_tables():
        table = db.get_table(table_name)
        print(f"  • {table_name}: {table.count()} records")
    
    print("\nCollection Details:")
    for coll_name in db.list_collections():
        collection = db.get_collection(coll_name)
        print(f"  • {coll_name}: {collection.count_documents()} documents")


def demo_transactions(db):
    """Demo: Transaction support"""
    print_section("6. TRANSACTION SUPPORT")
    
    # Reopen database for transaction demo
    db.open()
    
    print("Starting transaction...")
    employees = db.get_table("employees")
    
    # Make changes
    print("  • Updating employee salaries...")
    employees.update(where={"department": "Engineering"}, updates={"salary": 110000.0})
    
    print("  • Inserting new employee...")
    employees.insert({"name": "Eve Davis", "department": "HR", "salary": 70000.0, "age": 29})
    
    # Commit
    print("\nCommitting transaction...")
    db.commit()
    print("✓ Transaction committed successfully")
    
    print(f"\nTotal employees after transaction: {employees.count()}")


def main():
    """Run the demo"""
    print("\n" + "=" * 60)
    print("  🗄️  PyHybridDB - Hybrid Database System Demo")
    print("=" * 60)
    print("\n  Combining SQL and NoSQL in a single database!")
    print("  Features: Tables, Collections, Unified Queries, ACID")
    
    try:
        # Create database
        db = demo_database_creation()
        
        # SQL operations
        demo_sql_operations(db)
        
        # NoSQL operations
        demo_nosql_operations(db)
        
        # Hybrid queries
        demo_hybrid_queries(db)
        
        # Statistics
        demo_statistics(db)
        
        # Transactions
        demo_transactions(db)
        
        # Close database
        db.close()
        
        # Final message
        print_section("DEMO COMPLETE")
        print("✓ All features demonstrated successfully!")
        print("\nNext steps:")
        print("  1. Start the API server: python -m pyhybriddb.cli serve")
        print("  2. Open admin panel: admin/index.html")
        print("  3. Try the interactive shell: python -m pyhybriddb.cli shell demo_db")
        print("  4. Run examples: python examples/basic_usage.py")
        print("  5. Read documentation: docs/QUICKSTART.md")
        print("\n" + "=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
