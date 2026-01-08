import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from django.conf import settings
from django.db import models
from django.utils.encoding import force_bytes


class EncryptedMixin:
    """Mixin for reusable encryption and decryption functionality"""

    @staticmethod
    def get_key(secret, salt):
        """Generate Fernet key from SECRET_KEY + salt using PBKDF2"""
        return b64e(
            PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend(),
            ).derive(secret)
        )

    @classmethod
    def encrypt(cls, value: str) -> str:
        if value is None:
            return None
        
        if cls._looks_encrypted(value):  # Don't re-encrypt
            return value
        
        # Generate random salt and derive key using PBKDF2
        salt = secrets.token_bytes(16)
        key = cls.get_key(force_bytes(settings.SECRET_KEY), salt)
        f = Fernet(key)
        token = f.encrypt(value.encode())
        
        # Store salt + token as base64
        return b64e(salt + b64d(token)).decode()

    @classmethod
    def decrypt(cls, value: str) -> str:
        if value is None:
            return None
        
        try:
            # Decode the base64 to get salt + encrypted_value
            decoded = b64d(value.encode())
            salt, encrypted_value = decoded[:16], b64e(decoded[16:])
            
            # Derive the key using the salt
            key = cls.get_key(force_bytes(settings.SECRET_KEY), salt)
            f = Fernet(key)
            
            return f.decrypt(encrypted_value).decode()
        except (ValueError, TypeError):
            # In case of base64 decode failure or invalid value
            return value
        except Exception:
            # In case of decryption failure - might be plain text
            return value

    @staticmethod
    def _looks_encrypted(value: str) -> bool:
        """Check if the string looks encrypted (salt + token format)"""
        try:
            if not isinstance(value, str) or len(value) < 50:
                return False
            
            # Try to decode and check if it has salt (16 bytes) + encrypted data
            decoded = b64d(value.encode())
            return len(decoded) > 16  # Must contain salt + encrypted data
        except Exception:
            return False

    def get_prep_value(self, value):
        """Called when saving to database"""
        if value is None:
            return None
        if not isinstance(value, str):
            return str(value) if value is not None else None
        return self.encrypt(value)

    def from_db_value(self, value, expression, connection):
        """Called when loading from database - keep encrypted for forms"""
        if value is None:
            return value
        return value

    def to_python(self, value):
        """Called when converting value to Python object - keep encrypted for forms"""
        if value is None:
            return value
        return value
    
    def get_decrypted_value(self, value):
        """Manually decrypt value when needed"""
        if value is None:
            return value
        if not self._looks_encrypted(value):
            return value
        return self.decrypt(value)


class EncryptedTextField(EncryptedMixin, models.TextField):
    pass


class EncryptedCharField(EncryptedMixin, models.CharField):
    pass
