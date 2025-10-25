from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyhybriddb",
    version="0.1.0",
    author="Infant Nirmal",
    author_email="contact@adrient.com",
    description="A Python-based hybrid database system combining SQL and NoSQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Adrient-tech/PyHybridDB.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
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
    entry_points={
        "console_scripts": [
            "pyhybriddb=pyhybriddb.cli:main",
        ],
    },
)
