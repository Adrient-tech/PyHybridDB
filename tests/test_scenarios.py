
import unittest
import shutil
import tempfile
import random
from pyhybriddb import Database

class TestScenarios(unittest.TestCase):
    """
    Test real-world usage scenarios requested for v2.0
    """

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = Database("scenario_db", path=self.test_dir, engine="lsm")
        self.db.create()

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.test_dir)

    def test_bulk_user_import_and_filter(self):
        """Test Scenario: Bulk Import users and Filter by ID"""
        users = self.db.create_collection("users")

        # 1. Bulk Import
        batch = []
        for i in range(500):
            batch.append({
                "emp_id": f"E{i}",
                "name": f"User {i}",
                "role": "Staff"
            })
        users.insert_many(batch)

        self.assertEqual(users.count_documents(), 500)

        # 2. Filter by ID (simulated query)
        target = users.find_one({"emp_id": "E100"})
        self.assertIsNotNone(target)
        self.assertEqual(target['name'], "User 100")

    def test_delete_particular_user(self):
        """Test Scenario: Delete particular user"""
        users = self.db.create_collection("users")
        users.insert_one({"emp_id": "E1", "name": "Alice"})
        users.insert_one({"emp_id": "E2", "name": "Bob"})

        # Delete Alice
        deleted = users.delete_one({"name": "Alice"})
        self.assertTrue(deleted)

        # Verify
        alice = users.find_one({"name": "Alice"})
        self.assertIsNone(alice)

        bob = users.find_one({"name": "Bob"})
        self.assertIsNotNone(bob)
        self.assertEqual(users.count_documents(), 1)

    def test_clone_profiles(self):
        """Test Scenario: Clone multiple profiles"""
        src = self.db.create_collection("source")
        src.insert_many([
            {"name": "A", "type": "original"},
            {"name": "B", "type": "original"}
        ])

        dest = self.db.create_collection("dest")
        originals = src.find()
        clones = []
        for item in originals:
            clone = item.copy()
            clone.pop('_id', None) # Remove ID
            clone['type'] = "clone"
            clones.append(clone)

        dest.insert_many(clones)

        self.assertEqual(dest.count_documents(), 2)
        sample = dest.find_one({"name": "A"})
        self.assertEqual(sample['type'], "clone")

    def test_show_tables(self):
        """Test Scenario: Show all tables"""
        self.db.create_collection("coll1")
        self.db.create_table("tab1", {"col": "int"})

        colls = self.db.list_collections()
        tables = self.db.list_tables()

        self.assertIn("coll1", colls)
        self.assertIn("tab1", tables)

    def test_multiple_documents(self):
        """Test Scenario: Storing multiple documents"""
        docs = self.db.create_collection("docs")
        ids = docs.insert_many([
            {"doc": 1},
            {"doc": 2},
            {"doc": 3}
        ])
        self.assertEqual(len(ids), 3)
        self.assertEqual(docs.count_documents(), 3)

if __name__ == '__main__':
    unittest.main()
