from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
import os

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive secure encryption key (returns only the key)"""
    return PBKDF2(
        password, 
        salt, 
        dkLen=32, 
        count=2_000_000,
        hmac_hash_module=SHA512
    )