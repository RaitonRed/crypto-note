# src/app/services/diary_service.py
from src.core.blockchain.chain import Blockchain
from src.core.crypto.aes_handler import AESHandler
from src.core.crypto.key_derivation import derive_key
import os

class DiaryService:
    def __init__(self):
        self.crypto = self._init_crypto()
        self.blockchain = Blockchain(self.crypto)
        self._load_data()

    def _init_crypto(self):
        # در محیط واقعی، پسورد باید از کاربر دریافت شود
        password = os.getenv("DIARY_PASSWORD", "default_strong_password")
        salt_path = "data/keystore/salt.der"
        
        if os.path.exists(salt_path):
            with open(salt_path, 'rb') as f:
                salt = f.read()
        else:
            key, salt = derive_key(password)
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)
            with open(salt_path, 'wb') as f:
                f.write(salt)
        
        key, _ = derive_key(password, salt)
        return AESHandler(key)

    def _load_data(self):
        self.blockchain.load_from_file("data/chains/main_chain.json")

    def add_note(self, note_data: dict):
        self.blockchain.add_block(note_data)
        self.blockchain.save_to_file("data/chains/main_chain.json")

    def get_all_notes(self) -> list:
        notes = []
        for block in self.blockchain.chain[1:]:  # Skip genesis block
            try:
                data = block.get_data(self.blockchain.crypto)
                notes.append({
                    "index": block.index,
                    "content": data.get("content", ""),
                    "timestamp": block.timestamp
                })
            except:
                continue
        return notes