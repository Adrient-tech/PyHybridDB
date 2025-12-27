from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("pyhybriddb.storage.lsm.optimized", ["pyhybriddb/storage/lsm/optimized.pyx"])
]

setup(
    ext_modules=cythonize(extensions, language_level=3),
)
