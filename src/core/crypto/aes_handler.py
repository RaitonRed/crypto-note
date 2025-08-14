from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import os

class AESHandler:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt with AES-GCM authenticated encryption"""
        iv = get_random_bytes(12)  # 96-bit IV for GCM
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        return base64.b64encode(iv + tag + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt and verify with AES-GCM"""
        decoded = base64.b64decode(encrypted_data)
        iv, tag, ciphertext = decoded[:12], decoded[12:28], decoded[28:]
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')