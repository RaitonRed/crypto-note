from sqlalchemy import Column, Integer, MetaData, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class BlockModel(Base):
    __tablename__ = 'blocks'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    index = Column(Integer, unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    encrypted_data = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<Block(index={self.index}, hash={self.current_hash[:8]}...)>"