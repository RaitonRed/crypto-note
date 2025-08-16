from PyQt5.QtWidgets import QMenuBar, QAction

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_menus()
    
    def setup_menus(self):
        # File Menu
        file_menu = self.addMenu("&File")
        self.new_action = QAction("&New Note")
        self.save_action = QAction("&Save")
        self.export_action = QAction("&Export All")
        self.exit_action = QAction("&Exit")
        
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Edit Menu
        edit_menu = self.addMenu("&Edit")
        self.find_action = QAction("&Find")
        self.prefs_action = QAction("&Preferences")
        
        edit_menu.addAction(self.find_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.prefs_action)
        
        # Security Menu
        security_menu = self.addMenu("&Security")
        self.change_pw_action = QAction("&Change Password")
        self.lock_action = QAction("&Lock Diary")
        
        security_menu.addAction(self.change_pw_action)
        security_menu.addAction(self.lock_action)