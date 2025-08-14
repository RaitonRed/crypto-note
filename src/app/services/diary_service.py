from datetime import datetime
from typing import List, Dict, Optional
from src.core.blockchain.chain import Blockchain
from src.core.crypto.aes_handler import AESHandler
from src.core.crypto.key_derivation import derive_key
from src.core.database.session import db_manager
import os
import logging
import hashlib

logger = logging.getLogger(__name__)

class DiaryService:
    def __init__(self, password: str):
        self.password = password
        self.crypto = self._init_crypto()
        self.blockchain = Blockchain(self.crypto)

    def _init_crypto(self):
        """Initialize crypto with proper key derivation"""
        salt_path = "data/keystore/salt.bin"
        
        if os.path.exists(salt_path):
            with open(salt_path, 'rb') as f:
                salt = f.read()
        else:
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)
            salt = os.urandom(32)
            with open(salt_path, 'wb') as f:
                f.write(salt)
        
        key, _ = derive_key(self.password, salt)
        return AESHandler(key)

    def verify_password(self) -> bool:
        """Verify password by decrypting genesis block"""
        try:
            genesis_block = self.blockchain.get_block_by_index(0)
            if genesis_block:
                data = genesis_block.get_decrypted_data(self.blockchain.crypto)
                return data.get("note") == "Genesis Block"
            return False
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    def add_note(self, note_content: str) -> bool:
        """Add new note to blockchain"""
        try:
            note_data = {
                "content": note_content,
                "created_at": str(datetime.utcnow()),
                "hash": hashlib.sha256(note_content.encode()).hexdigest()
            }
            return self.blockchain.add_block(note_data)
        except Exception as e:
            logger.error(f"Error adding note: {e}")
            return False

    def update_note(self, index: int, content: str) -> bool:
        """Update existing note by marking old as deleted and creating new"""
        try:
            # Mark old note as deleted
            self.blockchain.mark_as_deleted(index)
            
            # Create new note with updated content
            note_data = {
                "content": content,
                "created_at": str(datetime.utcnow()),
                "updated_from": index,
                "hash": hashlib.sha256(content.encode()).hexdigest()
            }
            return self.blockchain.add_block(note_data)
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            return False

    def delete_note(self, index: int) -> bool:
        """Mark note as deleted in blockchain"""
        try:
            return self.blockchain.mark_as_deleted(index)
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            return False

    def get_all_notes(self) -> List[Dict]:
        """Get all active notes from blockchain"""
        notes = []
        session = db_manager.get_session()
        try:
            blocks = self.blockchain.get_all_blocks(session)
            for block in blocks[1:]:  # Skip genesis
                if block.index in self.blockchain.deleted_blocks:
                    continue
                    
                try:
                    data = block.get_decrypted_data(self.blockchain.crypto)
                    notes.append({
                        "id": block.index,
                        "content": data["content"],
                        "date": data.get("created_at", ""),
                        "hash": data.get("hash", "")
                    })
                except Exception as e:
                    logger.error(f"Error decrypting block {block.index}: {e}")
            return notes
        finally:
            session.close()

    def get_note_by_index(self, index: int) -> Optional[Dict]:
        """Get specific note by index"""
        session = db_manager.get_session()
        try:
            block = self.blockchain.get_block_by_index(index, session)
            if block and block.index != 0:  # Skip genesis
                return block.get_decrypted_data(self.blockchain.crypto)
            return None
        finally:
            session.close()

    def cleanup(self):
        """Securely clear sensitive data"""
        self.password = None
        self.crypto.key = None
        del self.crypto