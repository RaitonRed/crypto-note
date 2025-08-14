import hashlib
from datetime import datetime
from typing import Dict, Any
import json

class Block:
    def __init__(self, index: int, data: Dict[str, Any], previous_hash: str, crypto):
        self.index = index
        self.timestamp = str(datetime.utcnow())
        self.encrypted_data = crypto.encrypt(json.dumps(data))
        self.previous_hash = previous_hash
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        sha = hashlib.sha256()
        sha.update(f"{self.index}{self.timestamp}{self.encrypted_data}{self.previous_hash}".encode())
        return sha.hexdigest()

    def get_data(self, crypto) -> Dict[str, Any]:
        return json.loads(crypto.decrypt(self.encrypted_data))