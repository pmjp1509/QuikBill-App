import sys
import os
import re
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout,
                             QCheckBox, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter
import pywhatkit
from datetime import datetime, timedelta

class WhatsAppSender(QThread):
    """Thread for sending WhatsApp message to avoid blocking UI"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, phone_number, image_path):
        super().__init__()
        self.phone_number = phone_number
        self.image_path = image_path
    
    def run(self):
        try:
            # Calculate time 2 minutes from now to allow WhatsApp Web to load
            now = datetime.now()
            send_time = now + timedelta(minutes=2)
            
            # Send image via WhatsApp
            pywhatkit.sendwhats_image(
                receiver=self.phone_number,
                img_path=self.image_path,
                caption="",  # No caption as per requirement
                wait_time=15,  # Wait time for WhatsApp Web to load
                tab_close=True,  # Close tab after sending
                close_time=3  # Time to wait before closing
            )
            
            self.finished.emit(True, "Bill sent successfully via WhatsApp!")
            
        except Exception as e:
            self.finished.emit(False, f"Failed to send WhatsApp message: {str(e)}")

class WhatsAppDialog(QDialog):
    """Dialog for WhatsApp bill sharing"""
    
    def __init__(self, bill_widget, customer_name="", parent=None):
        super().__init__(parent)
        self.bill_widget = bill_widget
        self.customer_name = customer_name
        self.setWindowTitle("Share Bill via WhatsApp")
        self.setModal(True)
        self.resize(450, 350)
        
        self.phone_number = ""
        self.save_customer = False
        self.image_path = ""
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Share Bill via WhatsApp")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 15px;")
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Customer Name (optional)
        self.customer_name_edit = QLineEdit()
        self.customer_name_edit.setText(self.customer_name)
        self.customer_name_edit.setPlaceholderText("Enter customer name (optional)")
        self.customer_name_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("Customer Name:", self.customer_name_edit)
        
        # WhatsApp Number (required)
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Enter WhatsApp number (e.g., +919876543210)")
        self.phone_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("WhatsApp Number:", self.phone_edit)
        
        layout.addLayout(form_layout)
        
        # Save customer checkbox
        self.save_customer_checkbox = QCheckBox("Save customer details to database")
        self.save_customer_checkbox.setStyleSheet("font-size: 12px; padding: 10px;")
        layout.addWidget(self.save_customer_checkbox)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.send_button = QPushButton("Send via WhatsApp")
        self.send_button.clicked.connect(self.send_whatsapp)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)
        layout.addLayout(button_layout)
        
        # Set focus to phone number field
        self.phone_edit.setFocus()
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
    
    def validate_phone_number(self, phone):
        """Validate WhatsApp phone number format"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Check if it starts with + and has country code
        if cleaned.startswith('+') and len(cleaned) >= 10:
            return cleaned
        
        # If no +, assume it's an Indian number and add +91
        if not cleaned.startswith('+'):
            if cleaned.startswith('91') and len(cleaned) >= 12:
                return '+' + cleaned
            elif len(cleaned) == 10:
                return '+91' + cleaned
        
        return None
    
    def capture_bill_image(self):
        """Capture bill widget as image"""
        try:
            # Create pixmap of the bill widget
            pixmap = QPixmap(self.bill_widget.size())
            pixmap.fill(Qt.white)
            
            # Render the widget to pixmap
            painter = QPainter(pixmap)
            self.bill_widget.render(painter)
            painter.end()
            
            # Save to temporary file
            if getattr(sys, 'frozen', False):
                # Running as a PyInstaller bundle
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as a script
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            temp_dir = os.path.join(base_dir, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.image_path = os.path.join(temp_dir, f"bill_{timestamp}.png")
            
            if pixmap.save(self.image_path, "PNG"):
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error capturing bill image: {e}")
            return False
    
    def send_whatsapp(self):
        """Send bill via WhatsApp"""
        # Validate inputs
        phone = self.phone_edit.text().strip()
        customer_name = self.customer_name_edit.text().strip()
        
        if not phone:
            QMessageBox.warning(self, "Error", "Please enter a WhatsApp number!")
            return
        
        # Validate phone number
        validated_phone = self.validate_phone_number(phone)
        if not validated_phone:
            QMessageBox.warning(self, "Error", 
                              "Please enter a valid WhatsApp number!\n"
                              "Format: +919876543210 or 9876543210")
            return
        
        self.phone_number = validated_phone
        self.save_customer = self.save_customer_checkbox.isChecked()
        
        # Capture bill image
        self.status_label.setText("Capturing bill image...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        if not self.capture_bill_image():
            QMessageBox.critical(self, "Error", "Failed to capture bill image!")
            self.progress_bar.setVisible(False)
            return
        
        # Disable buttons during sending
        self.send_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        
        # Show instructions
        self.status_label.setText("Preparing to send via WhatsApp Web...")
        
        QMessageBox.information(self, "WhatsApp Instructions", 
                              "WhatsApp Web will open in your browser.\n"
                              "Please ensure you are logged in to WhatsApp Web.\n"
                              "The bill will be sent automatically in 2 minutes.\n\n"
                              "Click OK to continue...")
        
        # Start WhatsApp sender thread
        self.whatsapp_sender = WhatsAppSender(self.phone_number, self.image_path)
        self.whatsapp_sender.finished.connect(self.on_whatsapp_finished)
        self.whatsapp_sender.start()
        
        self.status_label.setText("Sending via WhatsApp... Please wait...")
    
    def on_whatsapp_finished(self, success, message):
        """Handle WhatsApp sending completion"""
        self.progress_bar.setVisible(False)
        self.send_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        
        if success:
            # Clean up temporary image file
            try:
                if os.path.exists(self.image_path):
                    os.remove(self.image_path)
            except:
                pass
            
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", message)
            self.status_label.setText("Failed to send. Please try again.")
    
    def get_customer_data(self):
        """Get customer data for saving"""
        return {
            'name': self.customer_name_edit.text().strip(),
            'phone': self.phone_number,
            'save_to_db': self.save_customer
        }