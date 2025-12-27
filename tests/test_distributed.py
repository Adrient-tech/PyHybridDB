
import unittest
from unittest.mock import patch, MagicMock
from pyhybriddb.distributed.hashing import ConsistentHashRing
from pyhybriddb.distributed.cluster import DistributedCluster

class TestDistributed(unittest.TestCase):

    def test_consistent_hashing(self):
        """Test ring distribution"""
        nodes = ["n1", "n2", "n3"]
        ring = ConsistentHashRing(nodes, replicas=10)

        # Check distribution
        counts = {n: 0 for n in nodes}
        for i in range(100):
            node = ring.get_node(f"key_{i}")
            counts[node] += 1

        # Ensure relatively even distribution (at least somewhat used)
        for n in nodes:
            self.assertTrue(counts[n] > 0)

        # Consistency check: Adding node shouldn't move ALL keys
        old_assignment = {}
        for i in range(100):
            old_assignment[i] = ring.get_node(f"key_{i}")

        ring.add_node("n4")

        changed = 0
        for i in range(100):
            new_node = ring.get_node(f"key_{i}")
            if new_node != old_assignment[i]:
                changed += 1

        # Ideally only ~1/4 keys move
        self.assertTrue(changed < 40)
        self.assertTrue(changed > 0)

    @patch('requests.post')
    def test_cluster_write(self, mock_post):
        """Test cluster write routing"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "123"}
        mock_post.return_value = mock_resp

        cluster = DistributedCluster(["http://n1", "http://n2"])

        # Write
        cluster.write("users", {"id": "u1", "val": 1}, key_field="id")

        # Verify request sent
        self.assertTrue(mock_post.called)
        args, kwargs = mock_post.call_args
        self.assertIn("/write", args[0])
        self.assertEqual(kwargs['json']['collection'], "users")

if __name__ == '__main__':
    unittest.main()
