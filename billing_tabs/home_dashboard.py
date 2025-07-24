import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QApplication, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from billing_tabs.create_bill import CreateBillWindow
from billing_tabs.bill_history import BillHistoryWindow
from billing_tabs.inventory import InventoryWindow
from billing_tabs.admin_settings import AdminSettingsWindow
from billing_tabs.thermal_printer import ThermalPrinter

class HomeDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickBill - Home")
        # Set window size based on screen resolution or sensible default
        screen = QApplication.primaryScreen()
        screen_size = screen.size() if screen else None
        default_width, default_height = 1280, 720
        if screen_size and (screen_size.width() < default_width or screen_size.height() < default_height):
            self.resize(screen_size.width() * 0.95, screen_size.height() * 0.95)
        else:
            self.resize(default_width, default_height)
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initialize child windows
        self.create_bill_window = None
        self.bill_history_window = None
        self.inventory_window = None
        self.admin_settings_window = None
        
        # Initialize printer instance
        self.printer = ThermalPrinter()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 20, 0, 20)  # Add vertical margin buffer
        central_widget.setLayout(main_layout)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("GST Billing System")
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

        # Subtitle
        subtitle_label = QLabel("Complete Offline Billing Solution with GST Support")
        subtitle_label.setFont(QFont("Arial", 14))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(subtitle_label)
        
        # Main buttons container
        # buttons_container = QWidget()
        # buttons_layout = QVBoxLayout()
        # buttons_container.setLayout(buttons_layout)

        # Main buttons container
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(20)  # More spacing between buttons
        buttons_layout.setContentsMargins(40, 20, 40, 20)  # Outer margin
        buttons_container.setLayout(buttons_layout)
        buttons_container.setFixedHeight(420)  # Enough to fit all buttons + spacing

        # Create Bill Button
        create_bill_btn = QPushButton("Create Bill")
        create_bill_btn.setFont(QFont("Arial", 14, QFont.Bold))
        create_bill_btn.setMinimumHeight(70)
        create_bill_btn.clicked.connect(self.open_create_bill)
        create_bill_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px;
                margin: 0px;
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
        bill_history_btn.setFont(QFont("Arial", 14, QFont.Bold))
        bill_history_btn.setMinimumHeight(70)
        bill_history_btn.clicked.connect(self.open_bill_history)
        bill_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)

        # Inventory Button (Purple)
        inventory_btn = QPushButton("Inventory Management")
        inventory_btn.setFont(QFont("Arial", 14, QFont.Bold))
        inventory_btn.setMinimumHeight(70)
        inventory_btn.clicked.connect(self.open_inventory)
        inventory_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)

        # Settings Button (Red)
        settings_btn = QPushButton("Settings")
        settings_btn.setFont(QFont("Arial", 14, QFont.Bold))
        settings_btn.setMinimumHeight(70)
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px;
                margin: 0px;
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
        buttons_layout.addWidget(settings_btn)

        main_layout.addWidget(buttons_container)

        # Footer with features
        footer_label = QLabel("✓ GST Support  ✓ Thermal Printing  ✓ Barcode Scanning  ✓ Offline Database")
        footer_label.setFont(QFont("Arial", 12))
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-top: 20px;
            }
        """)
        main_layout.addWidget(footer_label)
        
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
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Adjust button sizes based on window size
        width = self.width()
        height = self.height()
        
        # Scale button heights based on window size
        if height < 600:
            button_height = 80
            font_size = 14
        elif height < 800:
            button_height = 100
            font_size = 16
        else:
            button_height = 120
            font_size = 18
        
        # Update button styles dynamically
        button_style_template = """
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
                min-height: {height}px;
                font-size: {font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """
        
        # Find and update buttons
        for child in self.findChildren(QPushButton):
            if child.text() == "Create Bill":
                child.setStyleSheet(button_style_template.format(
                    color="#3498db", hover_color="#2980b9", pressed_color="#21618c",
                    height=button_height, font_size=font_size
                ))
            elif child.text() == "Bill History":
                child.setStyleSheet(button_style_template.format(
                    color="#2ecc71", hover_color="#27ae60", pressed_color="#1e8449",
                    height=button_height, font_size=font_size
                ))
            elif child.text() == "Inventory Management":
                child.setStyleSheet(button_style_template.format(
                    color="#9b59b6", hover_color="#8e44ad", pressed_color="#7d3c98",
                    height=button_height, font_size=font_size
                ))
            elif child.text() == "Settings":
                child.setStyleSheet(button_style_template.format(
                    color="#e74c3c", hover_color="#c0392b", pressed_color="#a93226",
                    height=button_height, font_size=font_size
                ))
    
    def open_create_bill(self):
        """Open Create Bill window"""
        if self.create_bill_window is None:
            self.create_bill_window = CreateBillWindow(self.printer)
        self.create_bill_window.showMaximized()
        self.create_bill_window.raise_()
        self.create_bill_window.activateWindow()
    
    def open_bill_history(self):
        """Open Bill History window"""
        if self.bill_history_window is None:
            self.bill_history_window = BillHistoryWindow(self.printer)
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
    
    def open_settings(self):
        """Open admin settings window"""
        if self.admin_settings_window is None:
            self.admin_settings_window = AdminSettingsWindow()
            # Connect signal to refresh printer shop details
            self.admin_settings_window.shop_details_updated.connect(self.refresh_printer_details)
        # Always restore and bring to front
        self.admin_settings_window.showNormal()
        self.admin_settings_window.raise_()
        self.admin_settings_window.activateWindow()
    
    def refresh_printer_details(self):
        """Refresh printer shop details when admin settings are updated"""
        if self.printer:
            self.printer.refresh_shop_details()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Close all child windows
        if self.create_bill_window:
            self.create_bill_window.close()
        if self.bill_history_window:
            self.bill_history_window.close()
        if self.inventory_window:
            self.inventory_window.close()
        if self.admin_settings_window:
            self.admin_settings_window.close()
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeDashboard()
    window.show()
    sys.exit(app.exec_())