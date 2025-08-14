import json
from pathlib import Path
from typing import Any
from ..crypto.aes_handler import AESHandler

class SecureFileHandler:
    def __init__(self, crypto_handler: AESHandler):
        self.crypto = crypto_handler

    def save_encrypted(self, path: str, data: Any):
        """ذخیره داده با فرمت JSON رمزنگاری شده"""
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        encrypted = self.crypto.encrypt(json.dumps(data))
        with open(path, 'w') as f:
            f.write(encrypted)

    def load_encrypted(self, path: str) -> Any:
        """بارگذاری و رمزگشایی داده"""
        try:
            with open(path, 'r') as f:
                return json.loads(self.crypto.decrypt(f.read()))
        except (FileNotFoundError, json.JSONDecodeError):
            return None