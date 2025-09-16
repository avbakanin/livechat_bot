"""
Advanced encryption and data protection system.
"""

import base64
import hashlib
import secrets
from typing import Any, Dict, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json


class EncryptionService:
    """Advanced encryption service for data protection."""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize encryption service."""
        if master_key:
            self.master_key = master_key.encode()
        else:
            # Generate random master key (in production, store securely)
            self.master_key = Fernet.generate_key()
            
        self.fernet = Fernet(self.master_key)
        
    def encrypt_string(self, plaintext: str) -> str:
        """Encrypt string data."""
        if not plaintext:
            return ""
            
        encrypted_bytes = self.fernet.encrypt(plaintext.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
        
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt string data."""
        if not encrypted_text:
            return ""
            
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception:
            raise EncryptionException("Failed to decrypt data")
            
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt dictionary data."""
        json_str = json.dumps(data, ensure_ascii=False)
        return self.encrypt_string(json_str)
        
    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt dictionary data."""
        json_str = self.decrypt_string(encrypted_data)
        return json.loads(json_str)
        
    def encrypt_file(self, file_path: str, output_path: str) -> None:
        """Encrypt file."""
        with open(file_path, 'rb') as f:
            data = f.read()
            
        encrypted_data = self.fernet.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
            
    def decrypt_file(self, encrypted_path: str, output_path: str) -> None:
        """Decrypt file."""
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
            
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
        except Exception:
            raise EncryptionException("Failed to decrypt file")


class PasswordHasher:
    """Secure password hashing service."""
    
    def __init__(self):
        self.salt_length = 32
        
    def hash_password(self, password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_hex(self.salt_length)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return f"{salt}:{password_hash.hex()}"
        
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            salt, stored_hash = hashed_password.split(':')
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return password_hash.hex() == stored_hash
        except ValueError:
            return False


class DataMasker:
    """Data masking service for sensitive information."""
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address."""
        if '@' not in email:
            return email
            
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
            
        return f"{masked_local}@{domain}"
        
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number."""
        if len(phone) <= 4:
            return '*' * len(phone)
            
        return phone[:2] + '*' * (len(phone) - 4) + phone[-2:]
        
    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """Mask credit card number."""
        if len(card_number) <= 4:
            return '*' * len(card_number)
            
        return '*' * (len(card_number) - 4) + card_number[-4:]
        
    @staticmethod
    def mask_personal_data(data: str, mask_char: str = '*') -> str:
        """Mask personal data."""
        if len(data) <= 2:
            return mask_char * len(data)
            
        return data[0] + mask_char * (len(data) - 2) + data[-1]


class SecureStorage:
    """Secure storage for sensitive data."""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
        self.sensitive_fields = {
            'password', 'api_key', 'secret', 'token',
            'email', 'phone', 'credit_card', 'ssn'
        }
        
    def store_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store sensitive data with encryption."""
        encrypted_data = {}
        
        for key, value in data.items():
            if self._is_sensitive_field(key):
                encrypted_data[key] = self.encryption_service.encrypt_string(str(value))
            else:
                encrypted_data[key] = value
                
        return encrypted_data
        
    def retrieve_sensitive_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve and decrypt sensitive data."""
        decrypted_data = {}
        
        for key, value in encrypted_data.items():
            if self._is_sensitive_field(key) and isinstance(value, str):
                try:
                    decrypted_data[key] = self.encryption_service.decrypt_string(value)
                except EncryptionException:
                    decrypted_data[key] = value  # Return as-is if decryption fails
            else:
                decrypted_data[key] = value
                
        return decrypted_data
        
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if field contains sensitive data."""
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self.sensitive_fields)


class KeyManager:
    """Key management service."""
    
    def __init__(self):
        self.keys: Dict[str, bytes] = {}
        
    def generate_key(self, key_name: str) -> bytes:
        """Generate new encryption key."""
        key = Fernet.generate_key()
        self.keys[key_name] = key
        return key
        
    def get_key(self, key_name: str) -> Optional[bytes]:
        """Get encryption key by name."""
        return self.keys.get(key_name)
        
    def rotate_key(self, key_name: str) -> bytes:
        """Rotate encryption key."""
        return self.generate_key(key_name)
        
    def delete_key(self, key_name: str) -> bool:
        """Delete encryption key."""
        if key_name in self.keys:
            del self.keys[key_name]
            return True
        return False


class EncryptionException(Exception):
    """Encryption-related exception."""
    pass


# Global instances
encryption_service = EncryptionService()
password_hasher = PasswordHasher()
data_masker = DataMasker()
secure_storage = SecureStorage(encryption_service)
key_manager = KeyManager()
