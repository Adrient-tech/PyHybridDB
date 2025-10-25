"""
Configuration module - Loads settings from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try config.env as fallback
    config_env_path = Path(__file__).parent.parent / 'config.env'
    if config_env_path.exists():
        load_dotenv(config_env_path)


class Config:
    """Application configuration from environment variables"""
    
    # API Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_RELOAD: bool = os.getenv('API_RELOAD', 'false').lower() == 'true'
    
    # Security - JWT Configuration
    SECRET_KEY: str = os.getenv(
        'SECRET_KEY',
        'default-secret-key-CHANGE-THIS-IN-PRODUCTION'
    )
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    # Default Admin Credentials
    ADMIN_USERNAME: str = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD: str = os.getenv('ADMIN_PASSWORD', 'admin123')
    ADMIN_EMAIL: str = os.getenv('ADMIN_EMAIL', 'admin@pyhybriddb.com')
    
    # Database Configuration
    DEFAULT_DB_PATH: str = os.getenv('DEFAULT_DB_PATH', './data')
    MAX_DATABASES: int = int(os.getenv('MAX_DATABASES', '100'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'pyhybriddb.log')
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    CORS_ALLOW_CREDENTIALS: bool = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
    REMEMBER_ME_DAYS: int = int(os.getenv('REMEMBER_ME_DAYS', '7'))
    
    @classmethod
    def get_cors_origins(cls) -> list:
        """Get CORS origins as a list"""
        if cls.CORS_ORIGINS == '*':
            return ['*']
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(',')]
    
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        if cls.SECRET_KEY == 'default-secret-key-CHANGE-THIS-IN-PRODUCTION':
            import warnings
            warnings.warn(
                "WARNING: Using default SECRET_KEY. "
                "Please set a secure SECRET_KEY in .env file for production!",
                UserWarning
            )
        
        if cls.ADMIN_PASSWORD == 'admin123':
            import warnings
            warnings.warn(
                "WARNING: Using default admin password. "
                "Please change ADMIN_PASSWORD in .env file for production!",
                UserWarning
            )
    
    @classmethod
    def display(cls):
        """Display current configuration (hiding sensitive data)"""
        print("PyHybridDB Configuration:")
        print(f"  API Host: {cls.API_HOST}")
        print(f"  API Port: {cls.API_PORT}")
        print(f"  Secret Key: {'*' * 20} (hidden)")
        print(f"  JWT Algorithm: {cls.JWT_ALGORITHM}")
        print(f"  Token Expiry: {cls.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        print(f"  Admin Username: {cls.ADMIN_USERNAME}")
        print(f"  Admin Password: {'*' * len(cls.ADMIN_PASSWORD)} (hidden)")
        print(f"  Database Path: {cls.DEFAULT_DB_PATH}")
        print(f"  Log Level: {cls.LOG_LEVEL}")
        print(f"  CORS Origins: {cls.CORS_ORIGINS}")


# Validate configuration on import
Config.validate()


# Convenience exports
SECRET_KEY = Config.SECRET_KEY
JWT_ALGORITHM = Config.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
ADMIN_USERNAME = Config.ADMIN_USERNAME
ADMIN_PASSWORD = Config.ADMIN_PASSWORD
ADMIN_EMAIL = Config.ADMIN_EMAIL
