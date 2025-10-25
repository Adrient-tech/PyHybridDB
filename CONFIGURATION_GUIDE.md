# 🔧 PyHybridDB Configuration Guide

Complete guide for configuring PyHybridDB after pip installation.

---

## 📋 Overview

PyHybridDB uses **environment variables** for configuration. This allows users to configure the database without modifying package files.

---

## ✅ Configuration Methods

### **Method 1: CLI Init Command (Easiest)** ⭐

After installing PyHybridDB via pip, run:

```bash
# Create .env file with secure defaults
pyhybriddb init

# Or force overwrite existing file
pyhybriddb init --force
```

This creates a `.env` file in your current directory with:
- ✅ Automatically generated secure SECRET_KEY
- ✅ All configuration options with defaults
- ✅ Comments explaining each setting

Then edit the file:
```bash
notepad .env  # Windows
nano .env     # Linux/Mac
```

---

### **Method 2: Manual .env File**

Create a `.env` file in your project directory:

```env
# Security
SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
ADMIN_EMAIL=admin@example.com

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DEFAULT_DB_PATH=./data
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

---

### **Method 3: Environment Variables**

Set environment variables directly:

**Windows PowerShell:**
```powershell
$env:SECRET_KEY = "my-secret-key"
$env:ADMIN_PASSWORD = "secure-password"
$env:API_PORT = "8080"
$env:DEFAULT_DB_PATH = "./my_data"

# Then run
pyhybriddb serve
```

**Linux/Mac:**
```bash
export SECRET_KEY="my-secret-key"
export ADMIN_PASSWORD="secure-password"
export API_PORT="8080"
export DEFAULT_DB_PATH="./my_data"

# Then run
pyhybriddb serve
```

---

### **Method 4: Programmatic Configuration**

Configure in your Python code:

```python
import os

# Set configuration before importing
os.environ['SECRET_KEY'] = 'my-secret-key'
os.environ['ADMIN_PASSWORD'] = 'secure-password'
os.environ['DEFAULT_DB_PATH'] = './my_data'
os.environ['API_PORT'] = '8080'

# Now import and use
from pyhybriddb import Database

db = Database("my_app")
```

---

## 📝 Available Configuration Options

### **Security Settings**

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (random) | JWT secret key for authentication |
| `JWT_ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |

### **Admin Credentials**

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_USERNAME` | admin | Default admin username |
| `ADMIN_PASSWORD` | admin123 | Default admin password ⚠️ CHANGE THIS! |
| `ADMIN_EMAIL` | admin@pyhybriddb.com | Admin email |

### **API Configuration**

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | 0.0.0.0 | API server host |
| `API_PORT` | 8000 | API server port |
| `API_RELOAD` | false | Enable auto-reload (development) |

### **Database Settings**

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_DB_PATH` | ./data | Default database storage path |
| `MAX_DATABASES` | 100 | Maximum number of databases |

### **Logging & CORS**

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CORS_ORIGINS` | * | Allowed CORS origins |
| `CORS_ALLOW_CREDENTIALS` | true | Allow credentials in CORS |

---

## 🔐 Security Best Practices

### 1. **Generate Secure SECRET_KEY**

```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use the init command which generates one automatically:
```bash
pyhybriddb init
```

### 2. **Change Default Password**

```env
ADMIN_PASSWORD=YourSecurePassword123!
```

### 3. **Restrict CORS in Production**

```env
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 4. **Use HTTPS in Production**

Deploy behind a reverse proxy (nginx, Apache) with SSL/TLS.

### 5. **Set Appropriate Log Level**

```env
LOG_LEVEL=WARNING  # For production
```

---

## 📦 Configuration After pip Install

### **Scenario 1: Quick Start**

```bash
# Install
pip install pyhybriddb

# Initialize configuration
pyhybriddb init

# Edit configuration
notepad .env

# Start server
pyhybriddb serve
```

### **Scenario 2: Custom Project**

```bash
# Install
pip install pyhybriddb

# Create project directory
mkdir my_project
cd my_project

# Initialize configuration
pyhybriddb init

# Edit as needed
nano .env

# Use in code
python my_app.py
```

### **Scenario 3: Docker/Container**

```dockerfile
FROM python:3.10

# Install PyHybridDB
RUN pip install pyhybriddb

# Set environment variables
ENV SECRET_KEY="your-secret-key"
ENV ADMIN_PASSWORD="secure-password"
ENV API_HOST="0.0.0.0"
ENV API_PORT="8000"

# Run server
CMD ["pyhybriddb", "serve"]
```

---

## 🎯 Common Use Cases

### **Development Setup**

```env
SECRET_KEY=dev-secret-key-not-for-production
ADMIN_PASSWORD=admin123
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=*
```

### **Production Setup**

```env
SECRET_KEY=<generated-secure-key>
ADMIN_PASSWORD=<strong-password>
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
```

### **Testing Setup**

```env
SECRET_KEY=test-secret-key
ADMIN_PASSWORD=test123
API_HOST=127.0.0.1
API_PORT=8001
DEFAULT_DB_PATH=./test_data
LOG_LEVEL=DEBUG
```

---

## 🔍 View Current Configuration

```bash
# Show all configuration
pyhybriddb config
```

---

## ❓ FAQ

### **Q: Where should I put the .env file?**
A: In your project's root directory where you run `pyhybriddb` commands.

### **Q: Can I use different configurations for different projects?**
A: Yes! Each project can have its own `.env` file.

### **Q: What if I don't create a .env file?**
A: PyHybridDB will use default values, but you'll see warnings about using default passwords.

### **Q: Can I change configuration at runtime?**
A: Yes, set environment variables before importing PyHybridDB in your code.

### **Q: Is the .env file included in the pip package?**
A: No, users create their own `.env` file using `pyhybriddb init` or manually.

### **Q: How do I secure my SECRET_KEY?**
A: Never commit `.env` to git. Add it to `.gitignore`. Use `pyhybriddb init` to generate secure keys.

---

## 📚 Additional Resources

- **Quick Start**: See README.md
- **API Documentation**: http://localhost:8000/docs (when server running)
- **CLI Help**: `pyhybriddb --help`
- **GitHub**: https://github.com/Adrient-tech/PyHybridDB

---

## ✅ Summary

**After pip install, users can configure PyHybridDB by:**

1. ✅ Running `pyhybriddb init` (easiest)
2. ✅ Creating a `.env` file manually
3. ✅ Setting environment variables
4. ✅ Configuring programmatically in code

**The package does NOT require access to the source `config.env` file!**

---

*Last Updated: October 25, 2025*
