from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QLabel, QMenu
from PyQt5.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Search Box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search notes...")
        layout.addWidget(self.search_box)
        
        # Notes List
        self.notes_list = QListWidget()
        self.notes_list.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.notes_list)
        
        # Stats Label
        self.stats_label = QLabel("0 notes")
        layout.addWidget(self.stats_label)
    
    def create_context_menu(self):
        menu = QMenu()
        menu.addAction("View Full Note")
        menu.addAction("Delete Note")
        return menu