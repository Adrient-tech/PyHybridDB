"""
Unit tests for PyHybridDB
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from pyhybriddb import Database


class TestDatabase(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.test_dir = tempfile.mkdtemp()
        self.db = Database(name="test_db", path=self.test_dir)
        self.db.create()
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_create_database(self):
        """Test database creation"""
        self.assertTrue(self.db.db_file.exists())
        self.assertTrue(self.db._is_open)
    
    def test_create_table(self):
        """Test table creation"""
        schema = {"name": "string", "age": "integer"}
        table = self.db.create_table("users", schema)
        
        self.assertIsNotNone(table)
        self.assertEqual(table.name, "users")
        self.assertEqual(table.schema, schema)
        self.assertIn("users", self.db.list_tables())
    
    def test_create_collection(self):
        """Test collection creation"""
        collection = self.db.create_collection("posts")
        
        self.assertIsNotNone(collection)
        self.assertEqual(collection.name, "posts")
        self.assertIn("posts", self.db.list_collections())
    
    def test_table_insert(self):
        """Test table insert"""
        table = self.db.create_table("users", {"name": "string", "age": "integer"})
        
        record_id = table.insert({"name": "Alice", "age": 30})
        self.assertIsNotNone(record_id)
        self.assertEqual(table.count(), 1)
    
    def test_table_select(self):
        """Test table select"""
        table = self.db.create_table("users", {"name": "string", "age": "integer"})
        
        table.insert({"name": "Alice", "age": 30})
        table.insert({"name": "Bob", "age": 25})
        
        all_users = table.select()
        self.assertEqual(len(all_users), 2)
        
        alice = table.select(where={"name": "Alice"})
        self.assertEqual(len(alice), 1)
        self.assertEqual(alice[0]["name"], "Alice")
    
    def test_table_update(self):
        """Test table update"""
        table = self.db.create_table("users", {"name": "string", "age": "integer"})
        
        table.insert({"name": "Alice", "age": 30})
        updated = table.update(where={"name": "Alice"}, updates={"age": 31})
        
        self.assertEqual(updated, 1)
        alice = table.select(where={"name": "Alice"})
        self.assertEqual(alice[0]["age"], 31)
    
    def test_table_delete(self):
        """Test table delete"""
        table = self.db.create_table("users", {"name": "string", "age": "integer"})
        
        table.insert({"name": "Alice", "age": 30})
        table.insert({"name": "Bob", "age": 25})
        
        deleted = table.delete(where={"name": "Bob"})
        self.assertEqual(deleted, 1)
        self.assertEqual(table.count(), 1)
    
    def test_collection_insert(self):
        """Test collection insert"""
        collection = self.db.create_collection("posts")
        
        doc_id = collection.insert_one({"title": "Test", "content": "Hello"})
        self.assertIsNotNone(doc_id)
        self.assertEqual(collection.count_documents(), 1)
    
    def test_collection_find(self):
        """Test collection find"""
        collection = self.db.create_collection("posts")
        
        collection.insert_one({"title": "Post 1", "author": "Alice"})
        collection.insert_one({"title": "Post 2", "author": "Bob"})
        
        all_posts = collection.find()
        self.assertEqual(len(all_posts), 2)
        
        alice_posts = collection.find({"author": "Alice"})
        self.assertEqual(len(alice_posts), 1)
        self.assertEqual(alice_posts[0]["author"], "Alice")
    
    def test_collection_update(self):
        """Test collection update"""
        collection = self.db.create_collection("posts")
        
        collection.insert_one({"title": "Test", "views": 0})
        updated = collection.update_one(
            {"title": "Test"},
            {"$set": {"views": 100}}
        )
        
        self.assertTrue(updated)
        post = collection.find_one({"title": "Test"})
        self.assertEqual(post["views"], 100)
    
    def test_collection_delete(self):
        """Test collection delete"""
        collection = self.db.create_collection("posts")
        
        collection.insert_one({"title": "Post 1"})
        collection.insert_one({"title": "Post 2"})
        
        deleted = collection.delete_one({"title": "Post 1"})
        self.assertTrue(deleted)
        self.assertEqual(collection.count_documents(), 1)


class TestStorage(unittest.TestCase):
    """Test storage engine"""
    
    def setUp(self):
        """Set up test storage"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test.phdb"
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_file_creation(self):
        """Test file creation"""
        from pyhybriddb.storage.file_manager import FileManager
        
        fm = FileManager(str(self.test_file))
        fm.create()
        
        self.assertTrue(self.test_file.exists())
        fm.close()
    
    def test_file_header(self):
        """Test file header validation"""
        from pyhybriddb.storage.file_manager import FileManager
        
        fm = FileManager(str(self.test_file))
        fm.create()
        fm.close()
        
        # Reopen and validate
        fm.open('rb')
        # Should not raise exception
        fm.close()


class TestIndex(unittest.TestCase):
    """Test B-Tree index"""
    
    def test_index_insert(self):
        """Test index insertion"""
        from pyhybriddb.storage.index import BTreeIndex
        
        index = BTreeIndex()
        index.insert(1, 100)
        index.insert(2, 200)
        
        self.assertEqual(index.size(), 2)
    
    def test_index_search(self):
        """Test index search"""
        from pyhybriddb.storage.index import BTreeIndex
        
        index = BTreeIndex()
        index.insert(1, 100)
        index.insert(2, 200)
        
        self.assertEqual(index.search(1), 100)
        self.assertEqual(index.search(2), 200)
        self.assertIsNone(index.search(3))


if __name__ == '__main__':
    unittest.main()
