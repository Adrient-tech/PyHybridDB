"""
PyHybridDB - A Python-based hybrid database system
Combines SQL and NoSQL paradigms with a modern admin panel
"""

__version__ = "0.1.0"
__author__ = "PyHybridDB Team"

from pyhybriddb.core.database import Database
from pyhybriddb.core.connection import Connection

__all__ = ["Database", "Connection", "__version__"]
