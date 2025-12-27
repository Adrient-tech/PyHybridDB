
import unittest
import shutil
import tempfile
import numpy as np
from pathlib import Path
from pyhybriddb import Database

class TestTieredStorage(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = Database("test_tiered_db", path=self.test_dir, engine="lsm")
        self.db.create()

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.test_dir)

    def test_lsm_tier(self):
        """Test Tier 1: LSM Document Store"""
        coll = self.db.create_collection("docs")
        coll.insert_one({"name": "Test", "value": 123})

        doc = coll.find_one({"name": "Test"})
        self.assertIsNotNone(doc)
        self.assertEqual(doc['value'], 123)

    def test_analytics_tier(self):
        """Test Tier 2: Columnar Store"""
        table = self.db.create_analytics_table("sales", {
            "amount": "float",
            "qty": "int"
        })

        # Batch insert
        table.insert_many([
            {"amount": 10.5, "qty": 2},
            {"amount": 20.0, "qty": 1},
            {"amount": 5.5,  "qty": 4}
        ])

        # Aggregation
        total_amount = table.aggregate("amount", "sum")
        total_qty = table.aggregate("qty", "sum")
        avg_amount = table.aggregate("amount", "avg")

        self.assertAlmostEqual(total_amount, 36.0)
        self.assertEqual(total_qty, 7)
        self.assertAlmostEqual(avg_amount, 12.0)

        # Select
        rows = table.select(columns=["qty"], limit=2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['qty'], 2)

    def test_vector_tier(self):
        """Test Tier 3: Vector Store"""
        dim = 4
        idx = self.db.create_vector_index("embeddings", dimension=dim)

        # Vectors: [1,0,0,0], [0,1,0,0], [0,0,1,0]
        v1 = [1.0, 0.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0, 0.0]
        v3 = [0.0, 0.0, 1.0, 0.0]

        idx.add(v1, "v1")
        idx.add(v2, "v2")
        idx.add(v3, "v3")

        # Search close to v1
        q = [0.9, 0.1, 0.0, 0.0]
        results = idx.search(q, k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "v1")
        self.assertTrue(results[0][1] > 0.8) # High similarity

if __name__ == '__main__':
    unittest.main()
