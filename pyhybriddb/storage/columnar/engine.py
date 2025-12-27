"""
Columnar Storage Engine - Optimized for OLAP/Analytics
Stores data column-by-column using NumPy for vectorized processing.
"""

import os
import numpy as np
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

class ColumnarTable:
    """A single table stored in columnar format"""

    def __init__(self, name: str, schema: Dict[str, str], path: Path):
        self.name = name
        self.schema = schema # {col: type} ('int', 'float', 'str')
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.columns: Dict[str, Any] = {}
        self.row_count = 0
        self._load_columns()

    def _load_columns(self):
        """Load columns from disk"""
        for col_name, col_type in self.schema.items():
            col_file = self.path / f"{col_name}.npy"
            if col_file.exists():
                try:
                    self.columns[col_name] = np.load(str(col_file), allow_pickle=True)
                except:
                    self._init_column(col_name, col_type)
            else:
                self._init_column(col_name, col_type)

        if self.columns:
            self.row_count = len(next(iter(self.columns.values())))

    def _init_column(self, col_name: str, col_type: str):
        """Initialize empty column"""
        if col_type in ['int', 'integer']:
            self.columns[col_name] = np.array([], dtype=np.int64)
        elif col_type in ['float', 'double']:
            self.columns[col_name] = np.array([], dtype=np.float64)
        else:
            self.columns[col_name] = np.array([], dtype=object) # Strings/Objects

    def insert(self, record: Dict[str, Any]):
        """Insert a record (Single row - Slow, use insert_many for batch)"""
        self.insert_many([record])

    def insert_many(self, records: List[Dict[str, Any]]):
        """Batch insert"""
        # Transpose list of dicts to dict of lists
        cols_data = {col: [] for col in self.schema}

        for record in records:
            for col in self.schema:
                cols_data[col].append(record.get(col, None))

        # Append to numpy arrays
        for col, data in cols_data.items():
            new_arr = np.array(data)
            if self.columns[col].size == 0:
                 # Re-init with correct type if inferred from data?
                 # Or just append. NumPy append returns new copy.
                 # For production column stores, we would use chunked files (Parquet-like).
                 # Here we simply extend the array (expensive for massive data, ok for MVP).
                 self.columns[col] = new_arr
            else:
                 self.columns[col] = np.concatenate([self.columns[col], new_arr])

        self.row_count += len(records)
        self._save()

    def _save(self):
        """Save columns to disk"""
        for col_name, data in self.columns.items():
            np.save(str(self.path / f"{col_name}.npy"), data)

    def select(self, columns: Optional[List[str]] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Select rows"""
        if not columns:
            columns = list(self.schema.keys())

        result = []
        # Vectorized slice
        count = min(self.row_count, limit)

        for i in range(count):
            row = {}
            for col in columns:
                if col in self.columns:
                    row[col] = self.columns[col][i]
            result.append(row)

        return result

    def aggregate(self, column: str, func: str) -> Union[float, int, None]:
        """Perform fast aggregation"""
        if column not in self.columns:
            raise ValueError(f"Column {column} not found")

        data = self.columns[column]
        if len(data) == 0:
            return 0

        if func == 'sum':
            return np.sum(data)
        elif func == 'avg' or func == 'mean':
            return np.mean(data)
        elif func == 'max':
            return np.max(data)
        elif func == 'min':
            return np.min(data)
        elif func == 'count':
            return len(data)
        else:
            raise ValueError(f"Unknown aggregation: {func}")


class ColumnarStorageEngine:
    """Engine managing multiple columnar tables"""

    def __init__(self, db_path: str):
        self.base_path = Path(db_path) / "analytics"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.tables: Dict[str, ColumnarTable] = {}

    def create_table(self, name: str, schema: Dict[str, str]) -> ColumnarTable:
        """Create or load a columnar table"""
        table_path = self.base_path / name
        table = ColumnarTable(name, schema, table_path)
        self.tables[name] = table
        return table

    def get_table(self, name: str) -> Optional[ColumnarTable]:
        if name in self.tables:
            return self.tables[name]
        # Try loading
        table_path = self.base_path / name
        if table_path.exists():
            # We need schema to load.
            # For now, we assume schema is passed during creation or stored in a metadata file.
            # To fix: Save schema.json in table dir.
            import json
            schema_file = table_path / "schema.json"
            if schema_file.exists():
                with open(schema_file, 'r') as f:
                    schema = json.load(f)
                return self.create_table(name, schema)
        return None

    def save_schema(self, name: str, schema: Dict[str, str]):
        table_path = self.base_path / name
        table_path.mkdir(parents=True, exist_ok=True)
        import json
        with open(table_path / "schema.json", 'w') as f:
            json.dump(schema, f)
