# src/core/utils/setup_database.py
import sys
from os.path import dirname, abspath

# اضافه کردن مسیر پروژه به sys.path
project_root = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.insert(0, project_root)

from src.core.database.session import db_manager
from src.core.blockchain.chain import Blockchain
from src.core.crypto.aes_handler import AESHandler

def init_db():
    try:
        # پاکسازی دیتابیس (فقط برای توسعه)
        db_manager.Base.metadata.drop_all(db_manager.engine)
        
        # ایجاد جداول جدید
        db_manager.Base.metadata.create_all(db_manager.engine)
        
        # ایجاد بلاک جنسیس
        crypto = AESHandler(b'\x00'*32)  # کلید موقت
        blockchain = Blockchain(crypto)
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    init_db()