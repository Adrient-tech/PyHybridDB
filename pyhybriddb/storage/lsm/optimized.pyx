# cython: language_level=3
"""
Cython optimized components for LSM Tree
"""

import struct
from libc.stdio cimport fopen, fclose, fwrite, fread, FILE, fseek, SEEK_SET
from libc.string cimport memcpy

def write_sstable_fast(str path, list items):
    """
    Fast write of SSTable using C file I/O
    items: list of (key: str, value_bytes: bytes)
    Note: value must be already packed bytes
    """
    cdef FILE* f
    cdef bytes b_path = path.encode('utf-8')
    cdef char* c_path = b_path

    cdef bytes k_bytes
    cdef bytes v_bytes
    cdef int k_len
    cdef int v_len

    f = fopen(c_path, "wb")
    if f == NULL:
        raise IOError("Could not open file")

    try:
        for key, val_bytes in items:
            k_bytes = key.encode('utf-8')
            k_len = len(k_bytes)
            v_len = len(val_bytes)

            # Write KLen (4 bytes)
            fwrite(&k_len, 4, 1, f)
            # Write Key
            fwrite(<char*>k_bytes, 1, k_len, f)
            # Write VLen (4 bytes)
            fwrite(&v_len, 4, 1, f)
            # Write Value
            fwrite(<char*>val_bytes, 1, v_len, f)

    finally:
        fclose(f)
