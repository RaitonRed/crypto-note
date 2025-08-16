import logging
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QMessageBox, QStatusBar, QLineEdit, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from src.app.services.diary_service import DiaryService
from .auth_dialog import AuthDialog
from .sidebar import Sidebar
from .content_area import ContentArea
from .menu_bar import MenuBar

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    update_ui_signal = pyqtSignal()

    def __init__(self, diary_service=None, parent=None):
        super().__init__(parent)
        self.diary_service = diary_service
        self.current_password = None
        self.init_ui()
        self.setup_connections()
        
        if not diary_service:
            self.show_auth_dialog()

    def init_ui(self):
        """Initialize the main UI components"""
        self.setWindowTitle("CryptoNote - Secure Blockchain Notebook")
        self.setWindowIcon(QIcon(":/icons/app_icon.png"))
        self.resize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create UI components
        self.sidebar = Sidebar()
        self.content_area = ContentArea()
        
        main_layout.addWidget(self.sidebar, 1)  # Sidebar takes 1 part
        main_layout.addWidget(self.content_area, 3)  # Content takes 3 parts
        
        self.setCentralWidget(central_widget)
        
        # Create menus and status bar
        self.menu_bar = MenuBar()
        self.setMenuBar(self.menu_bar)
        self.create_status_bar()
        
        # Initialize security status
        self.update_security_status()

    def create_status_bar(self):
        """Create status bar with security indicators"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Security Indicator
        self.security_status = QLabel()
        self.status_bar.addPermanentWidget(self.security_status)
        self.status_bar.showMessage("Ready")

    def setup_connections(self):
        """Connect all signals and slots"""
        # Buttons
        self.content_area.save_button.clicked.connect(self.save_note)
        self.content_area.new_button.clicked.connect(self.new_note)
        self.content_area.delete_button.clicked.connect(self.delete_note)
        
        # List Interactions
        self.sidebar.notes_list.currentItemChanged.connect(self.load_selected_note)
        self.sidebar.notes_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Search
        self.sidebar.search_box.textChanged.connect(self.filter_notes)
        
        # Menu Actions
        self.menu_bar.save_action.triggered.connect(self.save_note)
        self.menu_bar.new_action.triggered.connect(self.new_note)
        self.menu_bar.lock_action.triggered.connect(self.lock_diary)
        self.menu_bar.change_pw_action.triggered.connect(self.change_password)
        self.menu_bar.exit_action.triggered.connect(self.close)
        
        # Internal Signals
        self.update_ui_signal.connect(self.refresh_ui)

    def show_auth_dialog(self):
        """Show authentication dialog to unlock the diary"""
        auth_dialog = AuthDialog(self)
        if auth_dialog.exec_() == AuthDialog.Accepted:
            password = auth_dialog.get_password()
            if password:
                try:
                    self.initialize_services(password)
                    self.update_ui_signal.emit()
                except Exception as e:
                    QMessageBox.warning(self, "Authentication Failed", str(e))
                    self.show_auth_dialog()
            else:
                QMessageBox.warning(self, "Error", "Password cannot be empty!")
                self.show_auth_dialog()
        else:
            self.close()

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
        self.content_area.note_editor.clear()
        self.content_area.meta_label.clear()
        self.update_security_status()

    def load_notes(self):
        """Load all notes from blockchain into the sidebar"""
        if not self.diary_service:
            return
            
        self.sidebar.notes_list.clear()
        try:
            notes = self.diary_service.get_all_notes()
            
            for note in notes:
                self.sidebar.notes_list.addItem(f"{note['date']} - {note['content'][:50]}...")
            
            # Update stats
            chain_length = self.diary_service.blockchain.get_chain_length()
            self.sidebar.stats_label.setText(f"{len(notes)} notes | Chain length: {chain_length}")
        except Exception as e:
            logger.error(f"Error loading notes: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load notes: {str(e)}")

    def filter_notes(self):
        """Filter notes based on search text"""
        search_text = self.sidebar.search_box.text().lower()
        
        for i in range(self.sidebar.notes_list.count()):
            item = self.sidebar.notes_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def load_selected_note(self, current, previous):
        """Load selected note into editor"""
        if not self.diary_service:
            return
            
        if current:
            note_id = self.sidebar.notes_list.row(current)
            try:
                note = self.diary_service.get_note_by_index(note_id + 1)  # +1 for genesis
                
                if note:
                    self.content_area.note_editor.setPlainText(note['content'])
                    self.content_area.meta_label.setText(
                        f"Created: {note['date']} | Block #{note_id + 1}"
                    )
            except Exception as e:
                logger.error(f"Error loading note: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load note: {str(e)}")

    def save_note(self):
        """Save current note to blockchain"""
        if not self.diary_service:
            QMessageBox.warning(self, "Error", "Diary is locked. Please authenticate.")
            return
            
        note_text = self.content_area.note_editor.toPlainText().strip()
        
        if not note_text:
            QMessageBox.warning(self, "Empty Note", "Note cannot be empty!")
            return
            
        try:
            current_item = self.sidebar.notes_list.currentItem()
            if current_item:
                # Update existing note
                note_id = self.sidebar.notes_list.row(current_item) + 1
                success = self.diary_service.update_note(note_id, note_text)
                message = "Note updated successfully!"
            else:
                # Create new note
                success = self.diary_service.add_note(note_text)
                message = "Note created successfully!"
            
            if success:
                self.update_ui_signal.emit()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", "Failed to save note!")
        except Exception as e:
            logger.error(f"Error saving note: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def new_note(self):
        """Create new empty note"""
        self.sidebar.notes_list.clearSelection()
        self.content_area.note_editor.clear()
        self.content_area.note_editor.setFocus()
        self.content_area.meta_label.clear()

    def delete_note(self):
        """Delete selected note"""
        if not self.diary_service:
            QMessageBox.warning(self, "Error", "Diary is locked. Please authenticate.")
            return
            
        current_item = self.sidebar.notes_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a note to delete.")
            return
            
        note_id = self.sidebar.notes_list.row(current_item) + 1
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
                    QMessageBox.information(self, "Success", "Note marked as deleted.")
            except Exception as e:
                logger.error(f"Error deleting note: {e}")
                QMessageBox.critical(self, "Error", str(e))

    def show_context_menu(self, position):
        """Show right-click context menu for notes"""
        menu = self.sidebar.create_context_menu()
        action = menu.exec_(self.sidebar.notes_list.mapToGlobal(position))
        
        if action:
            if action.text() == "View Full Note":
                self.load_selected_note(self.sidebar.notes_list.currentItem(), None)
            elif action.text() == "Delete Note":
                self.delete_note()

    def lock_diary(self):
        """Lock the diary and clear sensitive data"""
        self.diary_service = None
        self.current_password = None
        self.sidebar.notes_list.clear()
        self.content_area.note_editor.clear()
        self.content_area.meta_label.clear()
        self.sidebar.stats_label.setText("0 notes")
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
            status_text = "🔒 Secure | Chain Valid"
            style = "color: green; font-weight: bold;"
        else:
            status_text = "⚠️ Not Secure"
            style = "color: red; font-weight: bold;"
        
        self.security_status.setText(status_text)
        self.security_status.setStyleSheet(style)

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