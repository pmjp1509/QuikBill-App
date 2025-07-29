import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QCheckBox, QMessageBox,
                             QFrame, QSizePolicy, QDialog, QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from data_base.database import Database
import random
import smtplib
from email.mime.text import MIMEText

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
        title_label.setFont(QFont("Poppins", 16, QFont.Bold))
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
        self.cancel_button.setFont(QFont("Poppins", 14, QFont.Bold))
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
        self.ok_button.setFont(QFont("Poppins", 14, QFont.Bold))
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
        self.ok_button.setDefault(True)
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
        self.resize(500, 350)
        
        self.current_details = current_details
        self.shop_name = ""
        self.address = ""
        self.phone_number = ""
        self.location = ""
        self.gmail = ""
        self.accepted = False
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Edit Shop Details")
        title_label.setFont(QFont("Poppins", 16, QFont.Bold))
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
        
        self.gmail_edit = QLineEdit()
        self.gmail_edit.setText(self.current_details.get('gmail', ''))
        self.gmail_edit.setPlaceholderText("Enter Gmail address")
        self.gmail_edit.setStyleSheet("""
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
        form_layout.addRow("Gmail:", self.gmail_edit)
        
        self.location_edit = QLineEdit()
        self.location_edit.setText(self.current_details.get('location', ''))
        self.location_edit.setPlaceholderText("Enter shop location (Google Maps URL)")
        self.location_edit.setStyleSheet("""
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
        form_layout.addRow("Location:", self.location_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)
        button_layout.setContentsMargins(20, 20, 20, 20)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_details)
        self.save_button.setMinimumWidth(120)
        self.save_button.setMinimumHeight(48)
        self.save_button.setFont(QFont("Poppins", 14, QFont.Bold))
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
        self.save_button.setDefault(True)

        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.setFont(QFont("Poppins", 14, QFont.Bold))
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
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Set focus to first field
        self.shop_name_edit.setFocus()
    
    def save_details(self):
        self.shop_name = self.shop_name_edit.text().strip()
        self.address = self.address_edit.text().strip()
        self.phone_number = self.phone_edit.text().strip()
        self.location = self.location_edit.text().strip()
        self.gmail = self.gmail_edit.text().strip()
        if not self.shop_name or not self.address or not self.phone_number or not self.location or not self.gmail:
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
        header_label.setFont(QFont("Poppins", 24, QFont.Bold))
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
        shop_group.setFont(QFont("Poppins", 14, QFont.Bold))
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
        
        self.gmail_label = QLabel(f"Gmail: {self.admin_details.get('gmail', '')}")
        self.gmail_label.setStyleSheet("font-size: 14px; padding: 5px;")

        self.location_label = QLabel(f"Location: {self.admin_details['location']}")
        
        shop_layout.addWidget(self.shop_name_label)
        shop_layout.addWidget(self.address_label)
        shop_layout.addWidget(self.phone_label)
        shop_layout.addWidget(self.gmail_label)
        shop_layout.addWidget(self.location_label)

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
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        shop_layout.addWidget(self.edit_details_btn)
        
        main_layout.addWidget(shop_group)
        
        # Security Group
        security_group = QGroupBox("Security Settings")
        security_group.setFont(QFont("Poppins", 14, QFont.Bold))
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
        self.cred_toggle_btn.setFont(QFont("Poppins", 14, QFont.Bold))
        self.cred_toggle_btn.setMinimumHeight(50)
        self.cred_toggle_btn.clicked.connect(self.toggle_credentials)
        self.cred_toggle_btn.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                padding: 12px 28px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')
        security_layout.addWidget(self.cred_toggle_btn)
        self.update_cred_toggle_btn()
        # Add Change Credentials button at the bottom of security settings
        self.change_credentials_btn = QPushButton("Change Credentials")
        self.change_credentials_btn.setFont(QFont("Poppins", 14, QFont.Bold))
        self.change_credentials_btn.setMinimumHeight(50)
        self.change_credentials_btn.clicked.connect(self.change_credentials)
        self.change_credentials_btn.setStyleSheet('''
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 20px;
                padding: 12px 28px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        ''')
        security_layout.addWidget(self.change_credentials_btn)
        
        main_layout.addWidget(security_group)
        
        # Printer Settings Group
        printer_group = QGroupBox("Printer Settings")
        printer_group.setFont(QFont("Poppins", 14, QFont.Bold))
        printer_group.setStyleSheet("""
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
        
        printer_layout = QVBoxLayout()
        printer_group.setLayout(printer_layout)
        
        # Paper width selection
        from PyQt5.QtWidgets import QComboBox
        from billing_tabs.thermal_printer import ThermalPrinter
        
        paper_width_layout = QHBoxLayout()
        paper_width_layout.addWidget(QLabel("Paper Width:"))
        
        self.paper_width_combo = QComboBox()
        self.paper_width_combo.addItems(["58mm", "80mm", "112mm"])
        self.paper_width_combo.setCurrentText(self.admin_details.get('paper_width', '80mm'))
        self.paper_width_combo.currentTextChanged.connect(self.change_paper_width)
        paper_width_layout.addWidget(self.paper_width_combo)
        
        printer_layout.addLayout(paper_width_layout)
        
        # Paper width description
        self.paper_width_desc = QLabel("80mm - Standard receipt width (32 characters)")
        self.paper_width_desc.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")
        printer_layout.addWidget(self.paper_width_desc)
        
        # Test print buttons
        test_buttons_layout = QHBoxLayout()
        
        self.test_print_btn = QPushButton("Test Print")
        self.test_print_btn.clicked.connect(self.test_print)
        self.test_print_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        test_buttons_layout.addWidget(self.test_print_btn)
        
        self.format_demo_btn = QPushButton("Format Demo")
        self.format_demo_btn.clicked.connect(self.print_format_demo)
        self.format_demo_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        test_buttons_layout.addWidget(self.format_demo_btn)
        
        printer_layout.addLayout(test_buttons_layout)
        
        main_layout.addWidget(printer_group)
        
        # Add stretch to push everything to top
        main_layout.addStretch()
        
        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
    def change_credentials(self):
        dialog = ChangePasswordDialog(self.admin_details['username'], self)
        if dialog.exec_() == QDialog.Accepted:
            db = self.db
            if hasattr(dialog, 'old_password') and dialog.old_password:
                if not db.verify_admin_credentials(self.admin_details['username'], dialog.old_password):
                    QMessageBox.warning(self, "Error", "Old password is incorrect!")
                    return
            success = db.update_admin_details(
                shop_name=self.admin_details['shop_name'],
                address=self.admin_details['address'],
                phone_number=self.admin_details['phone_number'],
                use_credentials=self.admin_details['use_credentials'],
                username=self.admin_details['username'],
                password=dialog.new_password,
                location=self.admin_details['location']
            )
            if success:
                self.admin_details = db.get_admin_details()
                QMessageBox.information(self, "Success", "Password changed successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to update password.")


    def load_admin_details(self):
        """Load admin details from database"""
        if self.admin_details:
            self.shop_name_label.setText(f"Shop Name: {self.admin_details['shop_name']}")
            self.address_label.setText(f"Address: {self.admin_details['address']}")
            self.phone_label.setText(f"Phone: {self.admin_details['phone_number']}")
            self.location_label.setText(f"Location: {self.admin_details['location']}")
            self.gmail_label.setText(f"Gmail: {self.admin_details.get('gmail', '')}")
            self.update_cred_toggle_btn()
    
    def edit_details(self):
        """Open edit details dialog"""
        dialog = EditDetailsDialog(self.admin_details, self)
        if dialog.exec_() == QDialog.Accepted and dialog.accepted:
            # Verify credentials before allowing changes
            cred_dialog = CredentialsDialog(self)
            if cred_dialog.exec_() == QDialog.Accepted and cred_dialog.accepted:
                if self.db.verify_admin_credentials(cred_dialog.username, cred_dialog.password):
                    print("[DEBUG] Updating admin details (username/password will NOT change):")
                    print(f"  username: {self.admin_details['username']}")
                    print(f"  password: {self.admin_details['password']}")
                    success =   self.db.update_admin_details(
                        shop_name=dialog.shop_name,
                        address=dialog.address,
                        phone_number=dialog.phone_number,
                        use_credentials=self.admin_details['use_credentials'],
                        username=self.admin_details['username'],
                        password=self.admin_details['password'],
                        location=dialog.location,
                        gmail=dialog.gmail
                    )
                    print(f"[DEBUG] Database update success: {success}")
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
                    shop_name=self.admin_details['shop_name'],
                    address=self.admin_details['address'],
                    phone_number=self.admin_details['phone_number'],
                    use_credentials=new_state,                            # use_credentials (boolean)
                    username=self.admin_details['username'],        # username (string)
                    password=self.admin_details['password'],        # password (string)
                    location=self.admin_details['location']        # location (string)
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

    def change_paper_width(self, width):
        """Change paper width setting"""
        try:
            from billing_tabs.thermal_printer import ThermalPrinter
            printer = ThermalPrinter()
            if printer.set_paper_width(width):
                # Update description
                descriptions = {
                    "58mm": "58mm - Compact width (24 characters)",
                    "80mm": "80mm - Standard receipt width (32 characters)", 
                    "112mm": "112mm - Wide format (48 characters)"
                }
                self.paper_width_desc.setText(descriptions.get(width, "Unknown width"))
                QMessageBox.information(self, "Success", f"Paper width changed to {width}")
            else:
                QMessageBox.warning(self, "Error", "Failed to change paper width")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error changing paper width: {str(e)}")
    
    def test_print(self):
        """Print a test page"""
        try:
            from billing_tabs.thermal_printer import ThermalPrinter
            printer = ThermalPrinter()
            
            # Try to connect to printer (you may need to adjust connection method)
            if not printer.is_connected:
                # Try USB connection first
                if not printer.connect_usb_printer():
                    QMessageBox.warning(self, "Printer Not Connected", 
                                       "Please connect your thermal printer first.\n\n"
                                       "Supported connection methods:\n"
                                       "- USB (most common)\n"
                                       "- Serial (COM port)\n"
                                       "- Network (IP address)")
                    return
            
            if printer.print_test_page():
                QMessageBox.information(self, "Success", "Test page printed successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to print test page")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error printing test page: {str(e)}")
    
    def print_format_demo(self):
        """Print a format demo showing how bills will look"""
        try:
            from billing_tabs.thermal_printer import ThermalPrinter
            printer = ThermalPrinter()
            
            # Try to connect to printer
            if not printer.is_connected:
                if not printer.connect_usb_printer():
                    QMessageBox.warning(self, "Printer Not Connected", 
                                       "Please connect your thermal printer first.")
                    return
            
            if printer.print_format_demo():
                QMessageBox.information(self, "Success", "Format demo printed successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to print format demo")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error printing format demo: {str(e)}")

# 1. Add ChangePasswordDialog class
class ChangePasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Credentials")
        self.setModal(True)
        self.resize(400, 300)
        self.username = username
        self.new_password = None
        self.old_password = "" # Initialize old_password
        self.init_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        title_label = QLabel("Change Credentials")
        title_label.setFont(QFont("Poppins", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        form_layout = QFormLayout()
        self.username_label = QLabel(self.username)
        self.username_label.setFont(QFont("Poppins", 12))
        form_layout.addRow("Username:", self.username_label)
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Old Password:", self.old_password_edit)
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("New Password:", self.new_password_edit)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirm New Password:", self.confirm_password_edit)
        layout.addLayout(form_layout)
        # Forgot password link
        self.forgot_label = QLabel('<a href="#">Forgot password?</a>')
        self.forgot_label.setTextFormat(Qt.RichText)
        self.forgot_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.forgot_label.setOpenExternalLinks(False)
        self.forgot_label.setStyleSheet("color: #f39c12; font-size: 12px; margin-bottom: 8px;")
        self.forgot_label.linkActivated.connect(self.open_forgot_password)
        form_layout.addRow("", self.forgot_label)
        # Button layout
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Change Password")
        self.save_button.setFont(QFont("Poppins", 14, QFont.Bold))
        self.save_button.setMinimumHeight(48)
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_button.clicked.connect(self.change_password)
        self.save_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(QFont("Poppins", 14, QFont.Bold))
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.old_password_edit.setFocus()

    def open_forgot_password(self):
        otp_dialog = ForgotPasswordDialog(self.username, self)
        if otp_dialog.exec_() == QDialog.Accepted:
            pw_dialog = NewPasswordDialog(self)
            if pw_dialog.exec_() == QDialog.Accepted:
                self.new_password = pw_dialog.new_password
                self.accept()

    def change_password(self):
        old_pass = self.old_password_edit.text().strip()
        new_pass = self.new_password_edit.text().strip()
        confirm_pass = self.confirm_password_edit.text().strip()
        if not old_pass or not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            return
        self.old_password = old_pass
        self.new_password = new_pass
        self.accept()

# Add ForgotPasswordDialog class
class ForgotPasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forgot Password")
        self.setModal(True)
        self.resize(400, 220)
        self.username = username
        self.otp = None
        self.otp_valid = False
        self.otp_timer = QTimer(self)
        self.otp_timer.setSingleShot(True)
        self.otp_timer.timeout.connect(self.enable_resend)
        self.resend_seconds = 60
        self.resend_countdown_timer = QTimer(self)
        self.resend_countdown_timer.timeout.connect(self.update_resend_text)
        self.init_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        title_label = QLabel("Forgot Password")
        title_label.setFont(QFont("Poppins", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        db = Database()
        admin_details = db.get_admin_details()
        self.email = admin_details.get('gmail', '')
        self.masked_email = self.mask_email(self.email)
        self.email_label = QLabel(f"Send OTP to: <b>{self.masked_email}</b>")
        self.email_label.setStyleSheet("font-size: 14px; margin-bottom: 8px;")
        layout.addWidget(self.email_label)
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Enter OTP")
        self.otp_input.setMaxLength(6)
        self.otp_input.setVisible(False)
        layout.addWidget(self.otp_input)
        self.resend_label = QLabel("")
        self.resend_label.setStyleSheet("color: #f39c12; font-size: 12px; margin-bottom: 8px;")
        self.resend_label.setVisible(False)
        layout.addWidget(self.resend_label)
        self.send_button = QPushButton("Send OTP")
        self.send_button.setFont(QFont("Poppins", 14, QFont.Bold))
        self.send_button.setMinimumHeight(40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                padding: 12px 28px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.send_button.clicked.connect(self.handle_send_or_confirm)
        layout.addWidget(self.send_button)
        self.otp_status = QLabel("")
        self.otp_status.setStyleSheet("color: #e67e22; font-size: 12px;")
        layout.addWidget(self.otp_status)

    def mask_email(self, email):
        if not email or '@' not in email:
            return '***@***'
        name, domain = email.split('@', 1)
        if len(name) <= 2:
            masked = '*' * len(name)
        else:
            masked = name[:2] + '*' * (len(name)-2)
        return masked + '@' + domain

    def handle_send_or_confirm(self):
        if self.send_button.text() == "Send OTP" or self.send_button.text() == "Resend OTP":
            self.send_otp()
        else:
            self.confirm_otp()

    def send_otp(self):
        if not self.email:
            self.otp_status.setText("No email set for admin!")
            return
        self.otp = str(random.randint(100000, 999999))
        self.otp_valid = True
        try:
            from_email = 'joey561509@gmail.com'  # TODO: Replace with your Gmail
            password = 'dosx madc bccw gwyy'  # TODO: Replace with your Gmail app password
            msg = MIMEText(f'Your OTP for password reset is: {self.otp}')
            msg['Subject'] = 'Your OTP for Password Reset'
            msg['From'] = from_email
            msg['To'] = self.email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(from_email, password)
                server.send_message(msg)
            if self.send_button.text() == "Resend OTP":
                self.otp_status.setText("OTP Resent! Please recheck your email.")
            else:
                self.otp_status.setText("OTP sent! Please check your email.")
            self.otp_input.setVisible(True)
            self.send_button.setText("Confirm")
            self.resend_label.setVisible(True)
            self.resend_seconds = 60
            self.update_resend_text()
            self.resend_label.setText(f"Resend in {self.resend_seconds}s")
            self.resend_label.setTextInteractionFlags(Qt.NoTextInteraction)
            self.send_button.setEnabled(True)
            self.otp_input.textChanged.connect(self.clear_status)
            self.send_button.setEnabled(True)
            self.send_button.setStyleSheet(self.send_button.styleSheet().replace('background-color: #f39c12;', 'background-color: #27ae60;'))
            self.otp_timer.start(60000)  # 1 minute
            self.resend_countdown_timer.start(1000)
        except Exception as e:
            self.otp_status.setText(f"Failed to send OTP: {e}")

    def update_resend_text(self):
        if self.resend_seconds > 1:
            self.resend_seconds -= 1
            self.resend_label.setText(f"Resend in {self.resend_seconds}s")
        else:
            self.resend_label.setText('<a href="#">Resend OTP</a>')
            self.resend_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            self.resend_label.linkActivated.connect(self.resend_otp)
            self.resend_countdown_timer.stop()

    def enable_resend(self):
        self.send_button.setEnabled(True)
        self.resend_label.setText('<a href="#">Resend OTP</a>')
        self.resend_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.resend_label.linkActivated.connect(self.resend_otp)

    def resend_otp(self):
        self.send_button.setText("Resend OTP")
        self.send_otp()

    def clear_status(self):
        self.otp_status.setText("")

    def confirm_otp(self):
        if self.otp_input.text().strip() == self.otp and self.otp_valid:
            self.otp_status.setText("")
            self.otp_valid = False
            self.accept()  # Close this dialog, proceed to password dialog
        else:
            self.otp_status.setText("Invalid OTP. Please try again.")

# Add NewPasswordDialog class
class NewPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set New Password")
        self.setModal(True)
        self.resize(400, 180)
        self.new_password = None
        self.init_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        title_label = QLabel("Set New Password")
        title_label.setFont(QFont("Poppins", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setPlaceholderText("New Password")
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_edit)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Confirm New Password")
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_edit)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #e67e22; font-size: 12px;")
        layout.addWidget(self.status_label)
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Set Password")
        self.save_button.setFont(QFont("Poppins", 14, QFont.Bold))
        self.save_button.setMinimumHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                padding: 12px 28px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.save_button.clicked.connect(self.set_password)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

    def set_password(self):
        new_pass = self.new_password_edit.text().strip()
        confirm_pass = self.confirm_password_edit.text().strip()
        if not new_pass or not confirm_pass:
            self.status_label.setText("Please enter and confirm your new password.")
            return
        if new_pass != confirm_pass:
            self.status_label.setText("Passwords do not match.")
            return
        # Update password in DB
        db = Database()
        admin_details = db.get_admin_details()
        success = db.update_admin_details(
            shop_name=admin_details['shop_name'],
            address=admin_details['address'],
            phone_number=admin_details['phone_number'],
            use_credentials=admin_details['use_credentials'],
            username=admin_details['username'],
            password=new_pass,
            location=admin_details['location'],
            gmail=admin_details['gmail']
        )
        if success:
            self.new_password = new_pass
            self.accept()
        else:
            self.status_label.setText("Failed to update password.")