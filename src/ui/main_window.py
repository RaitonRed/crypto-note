# src/ui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, 
                            QTextEdit, QPushButton, QListWidget, QLabel)
from PyQt5.QtCore import Qt
from src.app.services.diary_service import DiaryService

class MainWindow(QMainWindow):
    def __init__(self, diary_service: DiaryService):
        super().__init__()
        self.diary_service = diary_service
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("MemChain Diary")
        self.resize(800, 600)

        # Widgets
        self.note_editor = QTextEdit()
        self.save_button = QPushButton("Save Note")
        self.notes_list = QListWidget()
        self.status_label = QLabel()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("New Note:"))
        layout.addWidget(self.note_editor)
        layout.addWidget(self.save_button)
        layout.addWidget(QLabel("Your Notes:"))
        layout.addWidget(self.notes_list)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connections
        self.save_button.clicked.connect(self.save_note)
        self.notes_list.itemDoubleClicked.connect(self.view_note)

        self.load_notes()

    def save_note(self):
        note_text = self.note_editor.toPlainText().strip()
        if note_text:
            self.diary_service.add_note({"content": note_text})
            self.load_notes()
            self.note_editor.clear()
            self.status_label.setText("Note saved securely!")

    def load_notes(self):
        self.notes_list.clear()
        notes = self.diary_service.get_all_notes()
        for note in notes:
            self.notes_list.addItem(f"Note #{note['index']}: {note['content'][:50]}...")

    def view_note(self, item):
        # نمایش کامل یادداشت در یک پنجره جدید
        pass