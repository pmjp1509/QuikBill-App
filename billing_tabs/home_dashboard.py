import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QApplication, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from billing_tabs.create_bill import CreateBillWindow
from billing_tabs.bill_history import BillHistoryWindow
from billing_tabs.inventory import InventoryWindow

class HomeDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing System - Home")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize child windows
        self.create_bill_window = None
        self.bill_history_window = None
        self.inventory_window = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Billing System")
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
        header_layout.addWidget(header_label)
        main_layout.addLayout(header_layout)
        
        # Main buttons container
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_container.setLayout(buttons_layout)
        
        # Create Bill Button
        create_bill_btn = QPushButton("Create Bill")
        create_bill_btn.setFont(QFont("Arial", 16, QFont.Bold))
        create_bill_btn.setMinimumHeight(120)
        create_bill_btn.clicked.connect(self.open_create_bill)
        create_bill_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        # Bill History Button
        bill_history_btn = QPushButton("Bill History")
        bill_history_btn.setFont(QFont("Arial", 16, QFont.Bold))
        bill_history_btn.setMinimumHeight(120)
        bill_history_btn.clicked.connect(self.open_bill_history)
        bill_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        # Inventory Button
        inventory_btn = QPushButton("Inventory")
        inventory_btn.setFont(QFont("Arial", 16, QFont.Bold))
        inventory_btn.setMinimumHeight(120)
        inventory_btn.clicked.connect(self.open_inventory)
        inventory_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Add buttons to layout
        buttons_layout.addWidget(create_bill_btn)
        buttons_layout.addWidget(bill_history_btn)
        buttons_layout.addWidget(inventory_btn)
        
        # Add stretch to center buttons
        main_layout.addStretch()
        main_layout.addWidget(buttons_container)
        main_layout.addStretch()
        
        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
    
    def showEvent(self, event):
        """Center the window on the screen when shown"""
        super().showEvent(event)
        frame_geom = self.frameGeometry()
        screen = QApplication.primaryScreen()
        center_point = screen.geometry().center()
        frame_geom.moveCenter(center_point)
        self.move(frame_geom.topLeft())
    
    def open_create_bill(self):
        """Open Create Bill window"""
        if self.create_bill_window is None:
            self.create_bill_window = CreateBillWindow()
        self.create_bill_window.showMaximized()
        self.create_bill_window.raise_()
        self.create_bill_window.activateWindow()
    
    def open_bill_history(self):
        """Open Bill History window"""
        if self.bill_history_window is None:
            self.bill_history_window = BillHistoryWindow()
        self.bill_history_window.showMaximized()
        self.bill_history_window.raise_()
        self.bill_history_window.activateWindow()
    
    def open_inventory(self):
        """Open Inventory window"""
        if self.inventory_window is None:
            self.inventory_window = InventoryWindow()
        self.inventory_window.showMaximized()
        self.inventory_window.raise_()
        self.inventory_window.activateWindow()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Close all child windows
        if self.create_bill_window:
            self.create_bill_window.close()
        if self.bill_history_window:
            self.bill_history_window.close()
        if self.inventory_window:
            self.inventory_window.close()
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeDashboard()
    window.show()
    sys.exit(app.exec_())