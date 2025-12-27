"""
PyHybridDB v2.0 - Comprehensive Demo
Covers: Bulk Import, Filtering, Deletion, Cloning, Tables, Documents, Vectors.
"""

import os
import shutil
import time
import random
from pyhybriddb import Database

DB_PATH = "./demo_data"

def setup_clean():
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
    os.makedirs(DB_PATH)

def main():
    setup_clean()
    print("=== PyHybridDB v2.0 Feature Demo ===")

    # Initialize Database (LSM Engine by default for fast writes)
    db = Database("demo_db", path=DB_PATH, engine="lsm")
    db.create()

    print("\n[1] Bulk User Import (LSM Tier)")
    # Scenario: Import 1000 users from a "CSV/JSON source"
    users = db.create_collection("users")

    user_data = []
    for i in range(1000):
        user_data.append({
            "emp_id": f"EMP_{i:04d}",
            "name": f"Employee_{i}",
            "dept": random.choice(["HR", "Engineering", "Sales", "Marketing"]),
            "salary": random.randint(50000, 150000),
            "active": True
        })

    start_time = time.time()
    # Batch insert is usually preferred, but LSM engine handles high-throughput single inserts well too.
    # Our Collection class uses insert_many which calls insert_one loop in current impl,
    # but the underlying LSM MemTable handles it efficiently.
    ids = users.insert_many(user_data)
    print(f"Imported {len(ids)} users in {time.time() - start_time:.4f}s")

    print("\n[2] Filter User by Employee ID")
    # Scenario: Find EMP_0042
    target_id = "EMP_0042"
    # Note: For optimal performance, we should index 'emp_id'.
    # Current MVP LSM engine indexes primary key (generated ID) effectively.
    # Secondary index support is simulated or requires scan in current MVP.
    start_time = time.time()
    emp = users.find_one({"emp_id": target_id})
    print(f"Found: {emp['name']} ({emp['dept']}) in {time.time() - start_time:.4f}s")

    print("\n[3] Delete Particular User")
    # Scenario: Fire EMP_0042
    if emp:
        print(f"Deleting {emp['name']}...")
        users.delete_one({"emp_id": target_id})

        # Verify
        check = users.find_one({"emp_id": target_id})
        if not check:
            print("User successfully deleted.")
        else:
            print("Error: User still exists.")

    print("\n[4] Clone Multiple User Profiles")
    # Scenario: Clone 'Engineering' dept users to a new 'R&D' dept project list
    engineers = users.find({"dept": "Engineering"})
    print(f"Found {len(engineers)} Engineers. Cloning to 'R&D' candidates...")

    rd_candidates = db.create_collection("rd_candidates")
    clones = []
    for eng in engineers:
        # Clone dict
        new_profile = eng.copy()
        # Remove old internal ID to generate new one
        new_profile.pop('_id', None)
        new_profile.pop('id', None)

        # Modify
        new_profile['original_dept'] = "Engineering"
        new_profile['dept'] = "R&D"
        new_profile['candidate_status'] = "Review"
        clones.append(new_profile)

    rd_candidates.insert_many(clones)
    print(f"Cloned {len(clones)} profiles into 'rd_candidates'.")

    print("\n[5] Show All User Tables/Collections")
    tables = db.list_tables()
    colls = db.list_collections()
    print("Tables:", tables)
    print("Collections:", colls)

    print("\n[6] Analytics Tier (Columnar)")
    # Scenario: Store salary data in Columnar tier for aggregation
    salaries = db.create_analytics_table("salary_stats", {
        "amount": "int",
        "bonus": "float"
    })

    # Extract salaries from users
    all_users = users.find()
    salary_data = [{"amount": u["salary"], "bonus": u["salary"] * 0.1} for u in all_users]

    salaries.insert_many(salary_data)
    print(f"Moved {len(salary_data)} salary records to Columnar Tier.")

    # Analytics
    total_payroll = salaries.aggregate("amount", "sum")
    avg_bonus = salaries.aggregate("bonus", "avg")
    print(f"Total Payroll: ${total_payroll:,.2f}")
    print(f"Average Bonus: ${avg_bonus:,.2f}")

    print("\n[7] Vector Tier (AI/Embeddings)")
    # Scenario: Store face embeddings for biometric login
    face_db = db.create_vector_index("face_biometrics", dimension=128)

    # Generate dummy embeddings for 100 users
    print("Indexing biometric data...")
    for i in range(100):
        # random vector normalized
        vec = [random.random() for _ in range(128)]
        face_db.add(vec, record_id=f"user_{i}")

    # Search
    print("Simulating Face Scan...")
    scan_vec = [random.random() for _ in range(128)]
    matches = face_db.search(scan_vec, k=3)
    print("Top 3 Matches:", matches)

    db.close()
    # Cleanup
    shutil.rmtree(DB_PATH)
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
