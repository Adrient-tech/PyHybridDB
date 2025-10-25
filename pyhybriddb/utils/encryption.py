"""
Encryption utilities for PyHybridDB
Provides transparent encryption/decryption for data at rest
"""

import os
import base64
from typing import Union, Optional


class EncryptionManager:
    """Manage encryption/decryption of data"""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption manager
        
        Args:
            key: 32-byte encryption key (generated if not provided)
        """
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
            
            self.Fernet = Fernet
            self.hashes = hashes
            self.PBKDF2 = PBKDF2
            
        except ImportError:
            raise ImportError(
                "cryptography not installed. Install with: pip install cryptography"
            )
        
        if key is None:
            key = Fernet.generate_key()
        
        self.key = key
        self.cipher = Fernet(key)
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key"""
        from cryptography.fernet import Fernet
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Derive encryption key from password
        
        Returns:
            (key, salt) tuple
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        from cryptography.hazmat.backends import default_backend
        
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return key, salt
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """Encrypt data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data"""
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_string(self, text: str) -> str:
        """Encrypt string and return base64 encoded result"""
        encrypted = self.encrypt(text)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded string"""
        encrypted = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted = self.decrypt(encrypted)
        return decrypted.decode('utf-8')
    
    def encrypt_file(self, input_file: str, output_file: str):
        """Encrypt a file"""
        with open(input_file, 'rb') as f:
            data = f.read()
        
        encrypted = self.encrypt(data)
        
        with open(output_file, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_file(self, input_file: str, output_file: str):
        """Decrypt a file"""
        with open(input_file, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.decrypt(encrypted)
        
        with open(output_file, 'wb') as f:
            f.write(decrypted)
    
    def save_key(self, key_file: str):
        """Save encryption key to file"""
        with open(key_file, 'wb') as f:
            f.write(self.key)
    
    @staticmethod
    def load_key(key_file: str) -> bytes:
        """Load encryption key from file"""
        with open(key_file, 'rb') as f:
            return f.read()


class EncryptedStorage:
    """Wrapper for encrypted storage operations"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption = encryption_manager
    
    def write_encrypted(self, file_path: str, data: Union[str, bytes]):
        """Write encrypted data to file"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self.encryption.encrypt(data)
        
        with open(file_path, 'wb') as f:
            f.write(encrypted)
    
    def read_encrypted(self, file_path: str) -> bytes:
        """Read and decrypt data from file"""
        with open(file_path, 'rb') as f:
            encrypted = f.read()
        
        return self.encryption.decrypt(encrypted)
    
    def read_encrypted_string(self, file_path: str) -> str:
        """Read and decrypt string from file"""
        data = self.read_encrypted(file_path)
        return data.decode('utf-8')


# Example usage functions
def setup_encryption(password: Optional[str] = None) -> EncryptionManager:
    """
    Setup encryption for database
    
    Args:
        password: Optional password to derive key from
    
    Returns:
        EncryptionManager instance
    """
    if password:
        key, salt = EncryptionManager.derive_key_from_password(password)
        # Save salt for later use
        with open('.encryption_salt', 'wb') as f:
            f.write(salt)
    else:
        key = EncryptionManager.generate_key()
        # Save key securely
        with open('.encryption_key', 'wb') as f:
            f.write(key)
    
    return EncryptionManager(key)


def load_encryption(password: Optional[str] = None) -> EncryptionManager:
    """
    Load existing encryption setup
    
    Args:
        password: Optional password if key was derived from password
    
    Returns:
        EncryptionManager instance
    """
    if password:
        # Load salt and derive key
        with open('.encryption_salt', 'rb') as f:
            salt = f.read()
        key, _ = EncryptionManager.derive_key_from_password(password, salt)
    else:
        # Load key directly
        key = EncryptionManager.load_key('.encryption_key')
    
    return EncryptionManager(key)
