import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from data_base.database import Database

class LoginDialog(QDialog):
    """Login dialog for admin authentication"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Login")
        self.setModal(True)
        self.setFixedSize(500, 350)
        
        self.db = Database()
        self.admin_details = self.db.get_admin_details()
        
        self.username = ""
        self.password = ""
        self.login_successful = False
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Admin Login Required")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 20px;")
        layout.addWidget(title_label)
        
        # Shop info if available
        if self.admin_details:
            shop_info = QLabel(f"Shop: {self.admin_details['shop_name']}")
            shop_info.setFont(QFont("Arial", 14))
            shop_info.setAlignment(Qt.AlignCenter)
            shop_info.setStyleSheet("color: #7f8c8d; padding: 10px;")
            layout.addWidget(shop_info)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        self.username_edit.setMinimumHeight(45)
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 3px solid #bdc3c7;
                border-radius: 10px;
                font-size: 16px;
                margin: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        username_label = QLabel("Username:")
        username_label.setFont(QFont("Arial", 14, QFont.Bold))
        username_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        form_layout.addRow(username_label, self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(45)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 3px solid #bdc3c7;
                border-radius: 10px;
                font-size: 16px;
                margin: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 14, QFont.Bold))
        password_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        form_layout.addRow(password_label, self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.verify_login)
        self.login_button.setMinimumHeight(50)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        layout.addLayout(button_layout)
        
        # Set focus to username field
        self.username_edit.setFocus()
        
        # Remove these lines to avoid double-calling verify_login
        # self.username_edit.returnPressed.connect(self.verify_login)
        # self.password_edit.returnPressed.connect(self.verify_login)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
    
    def verify_login(self):
        """Verify login credentials"""
        self.username = self.username_edit.text().strip()
        self.password = self.password_edit.text().strip()
        if not self.username or not self.password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return  # Do NOT close the dialog
        if self.db.verify_admin_credentials(self.username, self.password):
            self.login_successful = True
            self.accept()  # Do NOT show a 'Login successful!' alert
        else:
            QMessageBox.critical(self, "Error", "Invalid username or password!")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def get_credentials(self):
        """Get the entered credentials"""
        return self.username, self.password 

    def keyPressEvent(self, event):
        from PyQt5.QtCore import Qt
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.verify_login()
        else:
            super().keyPressEvent(event) 