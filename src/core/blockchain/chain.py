from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.core.crypto.aes_handler import AESHandler
from .block import Block
from src.core.database.session import db_manager
import logging

logger = logging.getLogger(__name__)

class Blockchain:
    def __init__(self, crypto: AESHandler):
        self.crypto = crypto
        self.deleted_blocks = set()
        self._initialize_chain()

    def _initialize_chain(self):
        """Initialize blockchain with genesis block if needed"""
        session = db_manager.get_session()
        try:
            if not self.get_latest_block(session):
                genesis_data = {"note": "Genesis Block"}
                genesis_block = Block(
                    index=0,
                    data=genesis_data,
                    previous_hash="0",
                    crypto=self.crypto
                )
                session.add(genesis_block)
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Chain initialization failed: {e}")
        finally:
            session.close()

    def add_block(self, data: Dict[str, Any]) -> bool:
        """Add new block to blockchain"""
        session = db_manager.get_session()
        try:
            last_block = self.get_latest_block(session)
            if not last_block:
                logger.error("No last block found")
                return False
                
            new_block = Block(
                index=last_block.index + 1,
                data=data,
                previous_hash=last_block.current_hash,
                crypto=self.crypto
            )
            
            session.add(new_block)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding block: {e}")
            return False
        finally:
            session.close()

    def get_latest_block(self, session: Session) -> Optional[Block]:
        """Get latest block from blockchain"""
        return session.query(Block).order_by(Block.index.desc()).first()

    def mark_as_deleted(self, index: int) -> bool:
        """Mark block as deleted (soft delete)"""
        if index <= 0:
            return False
            
        self.deleted_blocks.add(index)
        return True

    def is_chain_valid(self, session: Session) -> bool:
        """Validate blockchain integrity"""
        blocks = self.get_all_blocks(session)
        
        for i in range(1, len(blocks)):
            current = blocks[i]
            previous = blocks[i-1]
            
            # Skip deleted blocks in validation
            if current.index in self.deleted_blocks:
                continue
                
            # Validate current hash
            if current.current_hash != current.calculate_hash():
                return False
                
            # Validate link to previous block
            if current.previous_hash != previous.current_hash:
                return False
                
        return True

    def get_all_blocks(self, session: Session) -> List[Block]:
        """Get all blocks from blockchain"""
        return session.query(Block).order_by(Block.index).all()

    def get_chain_length(self, session: Session) -> int:
        """Get blockchain length"""
        return session.query(Block).count()