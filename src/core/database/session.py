from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base
import os
import atexit

class DatabaseManager:
    def __init__(self, db_path="data/database.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.Base = Base
        self._init_db()
        atexit.register(self.close)  # Ensure cleanup on exit

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close(self):
        self.Session.remove()
        self.engine.dispose()

db_manager = DatabaseManager()