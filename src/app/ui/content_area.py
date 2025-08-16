from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

class ContentArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Note Editor
        self.note_editor = QTextEdit()
        self.note_editor.setPlaceholderText("Write your secure note here...")
        layout.addWidget(self.note_editor)
        
        # Button Row
        button_row = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        button_row.addWidget(self.new_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.delete_button)
        layout.addLayout(button_row)
        
        # Metadata
        self.meta_label = QLabel()
        self.meta_label.setAlignment(Qt.AlignRight)
        self.meta_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.meta_label)