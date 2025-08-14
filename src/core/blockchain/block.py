from datetime import datetime
from typing import Dict, Any
import hashlib
import json
from src.core.database.models import Base
from src.core.crypto.aes_handler import AESHandler
from sqlalchemy import Column, Integer, Text, String, DateTime

class Block(Base):
    __tablename__ = 'blocks'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    index = Column(Integer, unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    encrypted_data = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), unique=True, nullable=False)
    
    def __init__(self, index: int, data: Dict[str, Any], previous_hash: str, crypto: AESHandler):
        self.index = index
        self.timestamp = datetime.utcnow()
        self.previous_hash = previous_hash
        # Encrypt the data first
        encrypted_data = crypto.encrypt(json.dumps(data))
        self.encrypted_data = encrypted_data
        # Calculate hash using the encrypted data
        self.current_hash = self.calculate_hash()

    def calculate_hash(self, data: Dict[str, Any] = None) -> str:
        """Calculate hash with optional data parameter"""
        if data is None:
            # Use encrypted data if no data provided
            data_str = self.encrypted_data
        else:
            data_str = json.dumps(data, sort_keys=True)

        raw_string = f"{self.index}{self.timestamp}{self.encrypted_data}{self.previous_hash}"
        return hashlib.sha256(raw_string.encode()).hexdigest()
    
    def get_decrypted_data(self, crypto) -> Dict[str, Any]:
        """Decrypt block data"""
        return json.loads(crypto.decrypt(self.encrypted_data))