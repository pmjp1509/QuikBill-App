import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QCheckBox, QMessageBox,
                             QFrame, QSizePolicy, QDialog, QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from data_base.database import Database

class CredentialsDialog(QDialog):
    """Dialog for entering admin credentials"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Authentication")
        self.setModal(True)
        self.resize(400, 200)
        
        self.username = ""
        self.password = ""
        self.accepted = False
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Enter Admin Credentials")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Username:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Password:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)
        button_layout.setContentsMargins(20, 20, 20, 20)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 28px;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.ok_button = QPushButton("Login")
        self.ok_button.clicked.connect(self.accept_credentials)
        self.ok_button.setMinimumWidth(120)
        self.ok_button.setMinimumHeight(48)
        self.ok_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 28px;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
        
        # Set focus to username field
        self.username_edit.setFocus()
    
    def accept_credentials(self):
        self.username = self.username_edit.text().strip()
        self.password = self.password_edit.text().strip()
        
        if not self.username or not self.password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return
        
        self.accepted = True
        self.accept()

class EditDetailsDialog(QDialog):
    """Dialog for editing shop details"""
    def __init__(self, current_details, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Shop Details")
        self.setModal(True)
        self.resize(500, 300)
        
        self.current_details = current_details
        self.shop_name = ""
        self.address = ""
        self.phone_number = ""
        self.accepted = False
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Edit Shop Details")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        
        self.shop_name_edit = QLineEdit()
        self.shop_name_edit.setText(self.current_details.get('shop_name', ''))
        self.shop_name_edit.setPlaceholderText("Enter shop name")
        self.shop_name_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Shop Name:", self.shop_name_edit)
        
        self.address_edit = QLineEdit()
        self.address_edit.setText(self.current_details.get('address', ''))
        self.address_edit.setPlaceholderText("Enter shop address")
        self.address_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Address:", self.address_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setText(self.current_details.get('phone_number', ''))
        self.phone_edit.setPlaceholderText("Enter phone number")
        self.phone_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Phone Number:", self.phone_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)
        button_layout.setContentsMargins(20, 20, 20, 20)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_details)
        self.save_button.setMinimumWidth(120)
        self.save_button.setMinimumHeight(48)
        self.save_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 28px;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 28px;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Set focus to first field
        self.shop_name_edit.setFocus()
    
    def save_details(self):
        self.shop_name = self.shop_name_edit.text().strip()
        self.address = self.address_edit.text().strip()
        self.phone_number = self.phone_edit.text().strip()
        
        if not self.shop_name or not self.address or not self.phone_number:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        
        self.accepted = True
        self.accept()

class AdminSettingsWindow(QMainWindow):
    # Signal emitted when shop details are updated
    shop_details_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Settings")
        self.resize(600, 500)
        
        self.db = Database()
        self.admin_details = self.db.get_admin_details()
        self.init_ui()
        self.load_admin_details()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_label = QLabel("Admin Settings")
        header_label.setFont(QFont("Arial", 24, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(header_label)
        
        # Shop Details Group
        shop_group = QGroupBox("Shop Details")
        shop_group.setFont(QFont("Arial", 14, QFont.Bold))
        shop_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        shop_layout = QVBoxLayout()
        shop_group.setLayout(shop_layout)
        
        # Shop details display
        self.shop_name_label = QLabel("Shop Name: Not set")
        self.shop_name_label.setStyleSheet("font-size: 14px; padding: 5px;")
        
        self.address_label = QLabel("Address: Not set")
        self.address_label.setStyleSheet("font-size: 14px; padding: 5px;")
        
        self.phone_label = QLabel("Phone: Not set")
        self.phone_label.setStyleSheet("font-size: 14px; padding: 5px;")
        
        shop_layout.addWidget(self.shop_name_label)
        shop_layout.addWidget(self.address_label)
        shop_layout.addWidget(self.phone_label)
        
        # Edit Details Button
        self.edit_details_btn = QPushButton("Edit Details")
        self.edit_details_btn.clicked.connect(self.edit_details)
        self.edit_details_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        shop_layout.addWidget(self.edit_details_btn)
        
        main_layout.addWidget(shop_group)
        
        # Security Group
        security_group = QGroupBox("Security Settings")
        security_group.setFont(QFont("Arial", 14, QFont.Bold))
        security_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        security_layout = QVBoxLayout()
        security_group.setLayout(security_layout)
        
        # Toggle credentials button
        self.cred_toggle_btn = QPushButton()
        self.cred_toggle_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.cred_toggle_btn.setMinimumHeight(50)
        self.cred_toggle_btn.clicked.connect(self.toggle_credentials)
        security_layout.addWidget(self.cred_toggle_btn)
        self.update_cred_toggle_btn()
        # Credentials info (hidden for security)
        self.credentials_info = QLabel("Default credentials are set. Contact administrator for access.")
        self.credentials_info.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")
        security_layout.addWidget(self.credentials_info)
        
        main_layout.addWidget(security_group)
        
        # Add stretch to push everything to top
        main_layout.addStretch()
        
        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
    
    def load_admin_details(self):
        """Load admin details from database"""
        if self.admin_details:
            self.shop_name_label.setText(f"Shop Name: {self.admin_details['shop_name']}")
            self.address_label.setText(f"Address: {self.admin_details['address']}")
            self.phone_label.setText(f"Phone: {self.admin_details['phone_number']}")
            self.update_cred_toggle_btn()
    
    def edit_details(self):
        """Open edit details dialog"""
        dialog = EditDetailsDialog(self.admin_details, self)
        if dialog.exec_() == QDialog.Accepted and dialog.accepted:
            # Verify credentials before allowing changes
            cred_dialog = CredentialsDialog(self)
            if cred_dialog.exec_() == QDialog.Accepted and cred_dialog.accepted:
                if self.db.verify_admin_credentials(cred_dialog.username, cred_dialog.password):
                    # Update the details
                    success = self.db.update_admin_details(
                        dialog.shop_name,
                        dialog.address,
                        dialog.phone_number,
                        self.admin_details['use_credentials'],
                        self.admin_details['username'],
                        self.admin_details['password']
                    )
                    
                    if success:
                        # Reload admin details
                        self.admin_details = self.db.get_admin_details()
                        self.load_admin_details()
                        # Emit signal to notify other components
                        self.shop_details_updated.emit()
                        QMessageBox.information(self, "Success", "Shop details updated successfully!")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update shop details.")
                else:
                    QMessageBox.warning(self, "Error", "Invalid credentials!")
    
    def update_cred_toggle_btn(self):
        if self.admin_details['use_credentials']:
            self.cred_toggle_btn.setText('Disable Credentials')
            self.cred_toggle_btn.setStyleSheet('background-color: #e74c3c; color: white; border-radius: 10px;')
        else:
            self.cred_toggle_btn.setText('Enable Credentials')
            self.cred_toggle_btn.setStyleSheet('background-color: #27ae60; color: white; border-radius: 10px;')

    def toggle_credentials(self):
        cred_dialog = CredentialsDialog(self)
        result = cred_dialog.exec_()
        if result == QDialog.Accepted and cred_dialog.accepted:
            if self.db.verify_admin_credentials(cred_dialog.username, cred_dialog.password):
                new_state = not self.admin_details['use_credentials']
                success = self.db.update_admin_details(
                    self.admin_details['shop_name'],
                    self.admin_details['address'],
                    self.admin_details['phone_number'],
                    new_state,
                    self.admin_details['username'],
                    self.admin_details['password']
                )
                if success:
                    self.admin_details['use_credentials'] = new_state
                    self.update_cred_toggle_btn()
                    QMessageBox.information(self, 'Success', f'Credentials requirement {"enabled" if new_state else "disabled"}!')
                else:
                    QMessageBox.critical(self, 'Error', 'Failed to update settings.')
            else:
                QMessageBox.warning(self, 'Error', 'Invalid credentials!')
        # If cancelled, do nothing 