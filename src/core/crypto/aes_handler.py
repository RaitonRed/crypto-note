from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import base64

class AESHandler:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: str) -> str:
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_GCM, iv)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        return base64.b64encode(iv + tag + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        decoded = base64.b64decode(encrypted_data)
        iv, tag, ciphertext = decoded[:16], decoded[16:32], decoded[32:]
        cipher = AES.new(self.key, AES.MODE_GCM, iv)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')