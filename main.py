import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.app.services.diary_service import DiaryService

def main():
    app = QApplication(sys.argv)
    
    diary_service = DiaryService()
    window = MainWindow(diary_service)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()