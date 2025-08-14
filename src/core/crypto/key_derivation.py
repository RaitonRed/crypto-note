from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import os

def derive_key(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = os.urandom(32)
    key = PBKDF2(password, salt, dkLen=32, count=1000000, hmac_hash_module=SHA256)
    return key, salt