from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox

class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unlock CryptoNote")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Enter your password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        
        layout.addWidget(self.label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.buttons)
        
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
    
    def get_password(self):
        return self.password_input.text()