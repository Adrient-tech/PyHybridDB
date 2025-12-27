
import os
import shutil
import time
import random
from pyhybriddb import Database

DB_NAME = "benchmark_lsm"
DB_PATH = "./benchmark_data"

def setup():
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
    os.makedirs(DB_PATH)

def cleanup():
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

def run_benchmark():
    setup()
    print("--- Starting Benchmark (LSM Engine) ---")

    # Use LSM Engine
    db = Database(DB_NAME, path=DB_PATH, engine='lsm')
    db.create()

    coll = db.create_collection("users")

    # 1. Insert Performance
    count = 10000
    print(f"Inserting {count} records...")
    start_time = time.time()

    batch = []
    for i in range(count):
        # Insert one by one to test Write throughput of LSM
        coll.insert_one({
            "name": f"User_{i}",
            "age": random.randint(18, 90),
            "active": random.choice([True, False]),
            "score": random.randint(0, 1000)
        })

    duration = time.time() - start_time
    print(f"Insert Time: {duration:.4f}s ({count/duration:.2f} ops/s)")

    # 2. Read Performance (Point Lookup)
    print("\nReading random records...")
    start_time = time.time()
    found = 0
    reads = 1000
    for _ in range(reads):
        # We need to query by ID usually, but here let's scan or find by property
        # LSM is KV, so finding by property requires scan unless indexed.
        # But we haven't implemented secondary indexes for LSM yet in this MVP phase.
        # So we test scan speed.
        pass

    # Test Scan
    print("Scanning all records...")
    start_time = time.time()
    results = coll.find()
    duration = time.time() - start_time
    print(f"Scan Time: {duration:.4f}s (Found {len(results)} records)")

    db.close()
    cleanup()

if __name__ == "__main__":
    run_benchmark()
