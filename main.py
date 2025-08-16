import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.app.ui.main_window import MainWindow
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure application logging"""
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    
    # File handler with rotation
    file_handler = RotatingFileHandler('app.log', maxBytes=5*1024*1024, backupCount=2)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def main():
    setup_logging()
    app = QApplication(sys.argv)
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Application crash: {e}")
        QMessageBox.critical(None, "Fatal Error", 
            f"The application encountered a fatal error:\n{str(e)}")

if __name__ == "__main__":
    main()