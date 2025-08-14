from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QPushButton, QListWidget, QLabel,
                            QMessageBox, QInputDialog, QLineEdit, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from src.app.services.diary_service import DiaryService
from src.core.crypto.key_derivation import derive_key
import os
import getpass
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    update_ui_signal = pyqtSignal()

    def __init__(self, diary_service=None):
        super().__init__()
        self.diary_service = diary_service
        self.current_password = None
        self.init_ui()
        self.setup_connections()
        
        if not diary_service:
            self.show_auth_dialog()

    def show_auth_dialog(self):
        """Show authentication dialog"""
        password, ok = QInputDialog.getText(
            self,
            "Unlock CryptoNote",
            "Enter your password:",
            QLineEdit.Password
        )
        
        if ok:
            if password:  # بررسی وجود رمز عبور
                try:
                    self.initialize_services(password)
                    self.update_ui_signal.emit()
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e))
                    self.show_auth_dialog()
            else:
                QMessageBox.warning(self, "Error", "Password cannot be empty!")
        else:
            self.close()

    def initialize_services(self, password: str):
        """Initialize services with password"""
        try:
            self.current_password = password
            self.diary_service = DiaryService(password)
            
            # تأیید رمز عبور
            if not self.diary_service.verify_password():
                raise ValueError("Invalid password or corrupted data")
                
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", str(e))
            raise

    def init_ui(self):
        """Initialize all UI components"""
        self.setWindowTitle("CryptoNote - Secure Blockchain Notebook")
        self.setWindowIcon(QIcon(":/icons/app_icon.png"))
        self.resize(1000, 700)

        # Main Widgets
        self.create_central_widget()
        self.create_actions()
        self.create_menus()
        self.create_status_bar()

    def create_central_widget(self):
        """Create main content area"""
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Left Sidebar
        self.create_sidebar(main_layout)

        # Right Content Area
        self.create_content_area(main_layout)

        self.setCentralWidget(central_widget)

    def create_sidebar(self, parent_layout):
        """Create sidebar with notes list"""
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)

        # Search Box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search notes...")
        sidebar_layout.addWidget(self.search_box)

        # Notes List
        self.notes_list = QListWidget()
        self.notes_list.setContextMenuPolicy(Qt.CustomContextMenu)
        sidebar_layout.addWidget(self.notes_list)

        # Stats Label
        self.stats_label = QLabel("0 notes")
        sidebar_layout.addWidget(self.stats_label)

        parent_layout.addWidget(sidebar)

    def create_content_area(self, parent_layout):
        """Create main content editor"""
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)

        # Note Editor
        self.note_editor = QTextEdit()
        self.note_editor.setPlaceholderText("Write your secure note here...")
        content_layout.addWidget(self.note_editor)

        # Button Row
        button_row = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Save current note (Ctrl+S)")
        
        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        
        button_row.addWidget(self.new_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.delete_button)
        
        content_layout.addLayout(button_row)

        # Metadata
        self.meta_label = QLabel()
        self.meta_label.setAlignment(Qt.AlignRight)
        self.meta_label.setStyleSheet("color: #666; font-size: 12px;")
        content_layout.addWidget(self.meta_label)

        parent_layout.addWidget(content_area)

    def create_actions(self):
        """Create menu actions"""
        # File Menu
        self.new_action = QAction("&New Note", self, shortcut="Ctrl+N")
        self.save_action = QAction("&Save", self, shortcut="Ctrl+S")
        self.export_action = QAction("&Export All", self)
        self.exit_action = QAction("&Exit", self, shortcut="Ctrl+Q")

        # Edit Menu
        self.find_action = QAction("&Find", self, shortcut="Ctrl+F")
        self.prefs_action = QAction("&Preferences", self)

        # Security Menu
        self.change_pw_action = QAction("&Change Password", self)
        self.lock_action = QAction("&Lock Diary", self, shortcut="Ctrl+L")

    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.find_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.prefs_action)

        # Security Menu
        security_menu = menubar.addMenu("&Security")
        security_menu.addAction(self.change_pw_action)
        security_menu.addAction(self.lock_action)

    def create_status_bar(self):
        """Create status bar with security indicators"""
        self.statusBar().showMessage("Ready")
        
        # Security Indicator
        self.security_status = QLabel()
        self.update_security_status()
        self.statusBar().addPermanentWidget(self.security_status)

    def setup_connections(self):
        """Connect signals and slots"""
        # Buttons
        self.save_button.clicked.connect(self.save_note)
        self.new_button.clicked.connect(self.new_note)
        self.delete_button.clicked.connect(self.delete_note)
        
        # List Interactions
        self.notes_list.currentItemChanged.connect(self.load_selected_note)
        self.notes_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Search
        self.search_box.textChanged.connect(self.filter_notes)
        
        # Menu Actions
        self.save_action.triggered.connect(self.save_note)
        self.new_action.triggered.connect(self.new_note)
        self.lock_action.triggered.connect(self.lock_diary)
        self.change_pw_action.triggered.connect(self.change_password)
        
        # Internal Signals
        self.update_ui_signal.connect(self.refresh_ui)

    def show_auth_dialog(self):
        """Show authentication dialog"""
        password, ok = QInputDialog.getText(
            self,
            "Unlock  CryptoNote",
            "Enter your password:",
            QLineEdit.Password
        )
        
        if ok and password:
            try:
                self.initialize_services(password)
                self.update_ui_signal.emit()
            except Exception as e:
                QMessageBox.warning(self, "Authentication Failed", str(e))
                self.show_auth_dialog()

    def initialize_services(self, password):
        """Initialize services with password"""
        self.current_password = password
        self.diary_service = DiaryService(password)
        
        # Verify password by trying to decrypt the genesis block
        if not self.diary_service.verify_password():
            raise ValueError("Invalid password or corrupted data")

    def refresh_ui(self):
        """Refresh all UI elements"""
        self.load_notes()
        self.note_editor.clear()
        self.update_security_status()

    def load_notes(self):
        """Load all notes from blockchain"""
        self.notes_list.clear()
        notes = self.diary_service.get_all_notes()
        
        for note in notes:
            self.notes_list.addItem(f"{note['date']} - {note['content'][:50]}...")
        
        # Get chain length (will handle session internally)
        chain_length = self.diary_service.blockchain.get_chain_length()
        self.stats_label.setText(f"{len(notes)} notes | Chain length: {chain_length}")

    def filter_notes(self):
        """Filter notes based on search text"""
        search_text = self.search_box.text().lower()
        
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def load_selected_note(self, current, previous):
        """Load selected note into editor"""
        if current and self.diary_service:
            note_id = self.notes_list.row(current)
            note = self.diary_service.get_note_by_index(note_id + 1)  # +1 for genesis
            
            if note:
                self.note_editor.setPlainText(note['content'])
                self.meta_label.setText(f"Created: {note['date']} | Block #{note_id + 1}")

    def save_note(self):
        """Save current note to blockchain"""
        if not self.diary_service:
            QMessageBox.warning(self, "Error", "Diary is locked. Please authenticate.")
            return
            
        note_text = self.note_editor.toPlainText().strip()
        
        if note_text:
            try:
                if self.notes_list.currentItem():
                    # Update existing note
                    note_id = self.notes_list.currentRow() + 1
                    success = self.diary_service.update_note(note_id, note_text)
                else:
                    # Create new note
                    success = self.diary_service.add_note(note_text)
                
                if success:
                    self.update_ui_signal.emit()
                    QMessageBox.information(self, "Success", "Note saved securely to blockchain!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save note!")
            except Exception as e:
                logger.error(f"Error saving note: {e}")
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def new_note(self):
        """Create new empty note"""
        self.notes_list.clearSelection()
        self.note_editor.clear()
        self.note_editor.setFocus()
        self.meta_label.clear()

    def delete_note(self):
        """Delete selected note"""
        if not self.diary_service:
            QMessageBox.warning(self, "Error", "Diary is locked. Please authenticate.")
            return
            
        if self.notes_list.currentItem():
            note_id = self.notes_list.currentRow() + 1
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                "Are you sure you want to delete this note?\n"
                "Note: The note will be marked as deleted but remain in the blockchain.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    if self.diary_service.delete_note(note_id):
                        self.update_ui_signal.emit()
                except Exception as e:
                    logger.error(f"Error deleting note: {e}")
                    QMessageBox.critical(self, "Error", str(e))


    def show_context_menu(self, position):
        """Show right-click context menu for notes"""
        menu = QMenu()
        
        view_action = menu.addAction("View Full Note")
        delete_action = menu.addAction("Delete Note")
        
        action = menu.exec_(self.notes_list.mapToGlobal(position))
        
        if action == view_action:
            self.load_selected_note(self.notes_list.currentItem(), None)
        elif action == delete_action:
            self.delete_note()

    def lock_diary(self):
        """Lock the diary and clear sensitive data"""
        self.diary_service = None
        self.current_password = None
        self.notes_list.clear()
        self.note_editor.clear()
        self.show_auth_dialog()

    def change_password(self):
        """Change the encryption password"""
        new_password, ok = QInputDialog.getText(
            self,
            "Change Password",
            "Enter new password:",
            QLineEdit.Password
        )
        
        if ok and new_password:
            try:
                if self.diary_service.change_password(self.current_password, new_password):
                    self.current_password = new_password
                    QMessageBox.information(self, "Success", "Password changed successfully!")
                    self.update_security_status()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def update_security_status(self):
        """Update security indicator in status bar"""
        if self.diary_service and self.diary_service.is_chain_valid():
            self.security_status.setText("🔒 Secure | Chain Valid")
            self.security_status.setStyleSheet("color: green;")
        else:
            self.security_status.setText("⚠️ Not Secure")
            self.security_status.setStyleSheet("color: red;")

    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "Exit CryptoNote",
            "Are you sure you want to exit?\nAll unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear sensitive data from memory
            if self.diary_service:
                self.diary_service.cleanup()
            event.accept()
        else:
            event.ignore()