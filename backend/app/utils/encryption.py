import base64
from cryptography.fernet import Fernet
from app.config import get_settings

settings = get_settings()


def get_cipher() -> Fernet:
    """Get Fernet cipher for encryption/decryption."""
    key = settings.encryption_key.encode()
    if len(key) < 32:
        key = base64.urlsafe_b64encode(key.ljust(32)[:32])
    else:
        key = base64.urlsafe_b64encode(key[:32])
    return Fernet(key)


def encrypt_token(token: str) -> str:
    """Encrypt a token."""
    cipher = get_cipher()
    encrypted = cipher.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token."""
    cipher = get_cipher()
    decrypted = cipher.decrypt(encrypted_token.encode())
    return decrypted.decode()
