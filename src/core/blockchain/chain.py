from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.core.crypto.aes_handler import AESHandler
from .block import Block
import logging

logger = logging.getLogger(__name__)

class Blockchain:
    def __init__(self, crypto: AESHandler, db_manager):
        self.crypto = crypto
        self.deleted_blocks = set()
        self.db_manager = db_manager
        self._initialize_chain()

    def _initialize_chain(self):
        """Initialize blockchain with genesis block if needed"""
        session = self.db_manager.get_session()
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
        session = self.db_manager.get_session()
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

    def get_block_by_index(self, index: int, session: Session = None) -> Optional[Block]:
        """Get block by index with optional session management"""
        should_close = False
        if session is None:
            session = self.db_manager.get_session()
            should_close = True
        
        try:
            block = session.query(Block).filter(Block.index == index).first()
            if not block and index == 0:
                # Handle genesis block case if needed
                return self._initialize_chain()
            return block
        except Exception as e:
            logger.error(f"Error getting block {index}: {e}")
            return None
        finally:
            if should_close:
                session.close()

    def mark_as_deleted(self, index: int) -> bool:
        """Mark block as deleted (soft delete)"""
        if index <= 0:
            return False
            
        self.deleted_blocks.add(index)
        return True

    def is_chain_valid(self, session: Session = None) -> bool:
        """Validate blockchain integrity"""
        should_close = False
        if session is None:
            session = self.db_manager.get_session()
            should_close = True
        
        try:
            blocks = session.query(Block).order_by(Block.index).all()
            
            for i in range(1, len(blocks)):
                current = blocks[i]
                previous = blocks[i-1]
                
                if current.index in self.deleted_blocks:
                    continue
                    
                # Get decrypted data for validation
                current_data = current.get_decrypted_data(self.crypto)
                if current.current_hash != current.calculate_hash(current_data):
                    return False
                    
                if current.previous_hash != previous.current_hash:
                    return False
                    
            return True
        finally:
            if should_close:
                session.close()

    def get_all_blocks(self, session: Session) -> List[Block]:
        """Get all blocks from blockchain"""
        return session.query(Block).order_by(Block.index).all()

    def get_chain_length(self, session: Session = None) -> int:
        """Get blockchain length with optional session parameter"""
        should_close = False
        if session is None:
            session = self.db_manager.get_session()
            should_close = True
        
        try:
            return session.query(Block).count()
        finally:
            if should_close:
                session.close()