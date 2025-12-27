from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as _build_ext

# Try to import Cython to build extensions
try:
    from Cython.Build import cythonize
    HAS_CYTHON = True
except ImportError:
    HAS_CYTHON = False

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extensions = []
if HAS_CYTHON:
    extensions = [
        Extension(
            "pyhybriddb.storage.lsm.optimized",
            ["pyhybriddb/storage/lsm/optimized.pyx"],
        )
    ]
    ext_modules = cythonize(extensions, language_level=3)
else:
    # Fallback or pre-compiled?
    # For source distribution without Cython installed, we might skip or fail.
    # Ideally, we ship .c files, but here we just skip optimization if Cython missing
    # or rely on users installing Cython.
    ext_modules = []

setup(
    name="pyhybriddb",
    version="2.0.0",
    author="Infant Nirmal",
    author_email="contact@adrient.com",
    description="The Versatile Local Database: Hybrid Tiered Storage (LSM, Columnar, Vector)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Adrient-tech/PyHybridDB.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "msgpack>=1.0.0",
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "sqlparse>=0.4.4",
        "aiofiles>=23.2.1",
        "python-dotenv>=1.0.0",
        "bcrypt>=4.1.1",
    ],
    setup_requires=[
        "setuptools>=18.0",
        "cython"
    ],
    ext_modules=ext_modules,
    entry_points={
        "console_scripts": [
            "pyhybriddb=pyhybriddb.cli:main",
        ],
    },
)
