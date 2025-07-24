import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QDialog, QGridLayout, QSpinBox,
                             QDoubleSpinBox, QMessageBox, QFrame, QScrollArea,
                             QTextEdit, QDialogButtonBox, QInputDialog, QSizePolicy,
                             QHeaderView, QToolButton, QCompleter, QApplication)
from PyQt5.QtCore import Qt, QTimer, QEvent, QSize, QStringListModel
from PyQt5.QtGui import QFont, QPixmap, QIcon, QImage
from data_base.database import Database
from billing_tabs.thermal_printer import ThermalPrinter
from billing_tabs.whatsapp_dialog import WhatsAppDialog
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import re
import pyautogui
import qrcode
import random

class CustomerInfoDialog(QDialog):
    def __init__(self, customer_names=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Information")
        self.setModal(True)
        self.resize(400, 200)
        
        self.customer_name = ""
        self.customer_phone = ""
        self.customer_names = customer_names or []
        self.db = Database()
        self._last_lookup_name = None
        self._last_lookup_phone = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Customer Name with autocomplete
        layout.addWidget(QLabel("Customer Name (Required):"))
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 12))
        
        # Setup autocomplete
        if self.customer_names:
            completer = QCompleter(self.customer_names)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            self.name_input.setCompleter(completer)
        
        layout.addWidget(self.name_input)
        
        # When name changes or loses focus, try to fill phone
        self.name_input.editingFinished.connect(self.autofill_phone_for_name)
        self.name_input.textChanged.connect(self.clear_phone_if_name_changed)
        
        # Customer Phone
        layout.addWidget(QLabel("Customer Phone (Optional):"))
        self.phone_input = QLineEdit()
        self.phone_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.phone_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept_input)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def autofill_phone_for_name(self):
        name = self.name_input.text().strip()
        if not name:
            return
        # Only query DB if name changed
        if name == self._last_lookup_name:
            if self._last_lookup_phone:
                self.phone_input.setText(self._last_lookup_phone)
            return
        # Query the database for the most recent phone for this customer
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT customer_phone FROM bills WHERE customer_name = ? AND customer_phone IS NOT NULL AND customer_phone != "" ORDER BY id DESC LIMIT 1', (name,))
        result = cursor.fetchone()
        conn.close()
        phone = result[0] if result and result[0] else ""
        self._last_lookup_name = name
        self._last_lookup_phone = phone
        if phone:
            self.phone_input.setText(phone)
    
    def clear_phone_if_name_changed(self):
        # If the user is typing a new name, clear the phone field and cache
        self.phone_input.clear()
        self._last_lookup_name = None
        self._last_lookup_phone = None
    
    def accept_input(self):
        self.customer_name = self.name_input.text().strip()
        self.customer_phone = self.phone_input.text().strip()
        
        if not self.customer_name:
            QMessageBox.warning(self, "Error", "Customer name is required!")
            return
        
        self.accept()

class LooseItemDialog(QDialog):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setWindowTitle(f"Add {item_data['name']}")
        self.setModal(True)
        self.resize(500, 400)
        self.quantity = 0
        self.sgst_percent = item_data.get('sgst_percent', 0)
        self.cgst_percent = item_data.get('cgst_percent', 0)
        self.base_price = 0
        self.final_price = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        name_label = QLabel(f"Item: {self.item_data['name']}")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(name_label)
        hsn_label = QLabel(f"HSN Code: {self.item_data.get('hsn_code', 'N/A')}")
        hsn_label.setFont(QFont("Arial", 12))
        layout.addWidget(hsn_label)
        # Quantity
        layout.addWidget(QLabel("Quantity (kg):"))
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(999.99)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setSingleStep(0.1)
        self.quantity_input.setValue(1.0)
        self.quantity_input.valueChanged.connect(self.update_calculations)
        layout.addWidget(self.quantity_input)
        # Final Price (user input)
        layout.addWidget(QLabel("Final Price per kg (₹):"))
        self.final_price_input = QDoubleSpinBox()
        self.final_price_input.setMinimum(0.01)
        self.final_price_input.setMaximum(9999.99)
        self.final_price_input.setDecimals(2)
        self.final_price_input.setValue(self.item_data.get('total_price', self.item_data.get('base_price', self.item_data.get('price_per_kg', 0))))
        self.final_price_input.valueChanged.connect(self.update_calculations)
        layout.addWidget(self.final_price_input)
        # Show SGST/CGST as labels (not editable)
        sgst_label = QLabel(f"SGST (%): {self.sgst_percent}")
        sgst_label.setFont(QFont("Arial", 12))
        layout.addWidget(sgst_label)
        cgst_label = QLabel(f"CGST (%): {self.cgst_percent}")
        cgst_label.setFont(QFont("Arial", 12))
        layout.addWidget(cgst_label)
        # Base price display (read-only)
        self.base_price_label = QLabel()
        self.base_price_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.base_price_label.setStyleSheet("background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc;")
        layout.addWidget(self.base_price_label)
        # Calculations display
        self.calculations_label = QLabel()
        self.calculations_label.setFont(QFont("Arial", 12))
        self.calculations_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(self.calculations_label)
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add to Bill")
        cancel_button = QPushButton("Cancel")
        add_button.clicked.connect(self.accept_item)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.update_calculations()

    def update_calculations(self):
        quantity = self.quantity_input.value()
        final_price = self.final_price_input.value()
        sgst_percent = self.sgst_percent
        cgst_percent = self.cgst_percent
        divisor = 1 + (sgst_percent + cgst_percent) / 100
        base_price = final_price / divisor if divisor != 0 else 0
        self.base_price = base_price
        self.final_price = final_price
        self.base_price_label.setText(f"Base Price per kg (calculated): ₹{base_price:.2f}")
        base_amount = quantity * base_price
        sgst_amount = base_amount * sgst_percent / 100
        cgst_amount = base_amount * cgst_percent / 100
        final_amount = base_amount + sgst_amount + cgst_amount
        calculations_text = f"""
Base Amount: ₹{base_amount:.2f}
SGST ({sgst_percent}%): ₹{sgst_amount:.2f}
CGST ({cgst_percent}%): ₹{cgst_amount:.2f}
Final Amount: ₹{final_amount:.2f}
        """.strip()
        self.calculations_label.setText(calculations_text)

    def accept_item(self):
        self.quantity = self.quantity_input.value()
        self.base_price = self.base_price
        self.final_price = self.final_price
        self.sgst_percent = self.item_data.get('sgst_percent', 0)
        self.cgst_percent = self.item_data.get('cgst_percent', 0)
        self.accept()

class LooseCategoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Category")
        self.setModal(True)
        self.resize(900, 600)
        
        self.db = Database()
        self.selected_item = None
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Select Category")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Categories
        categories = self.db.get_loose_categories()
        self.categories_layout = QHBoxLayout()
        self.category_buttons = []
        for category in categories:
            cat_button = QPushButton(category['name'])
            cat_button.setFont(QFont("Arial", 12))
            cat_button.setMinimumHeight(60)
            cat_button.clicked.connect(lambda checked, cat_id=category['id']: self.show_items(cat_id))
            self.categories_layout.addWidget(cat_button)
            self.category_buttons.append((cat_button, category['id']))
        layout.addLayout(self.categories_layout)
        
        # Items area
        self.items_scroll = QScrollArea()
        self.items_widget = QWidget()
        self.items_layout = QGridLayout()
        self.items_widget.setLayout(self.items_layout)
        self.items_scroll.setWidget(self.items_widget)
        self.items_scroll.setWidgetResizable(True)
        layout.addWidget(self.items_scroll)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)
        
        self.setLayout(layout)
        
        # Show items for the first category by default
        if categories:
            self.show_items(categories[0]['id'])
    
    def resizeEvent(self, event):
        if hasattr(self, 'current_category_id'):
            self.show_items(self.current_category_id)
        super().resizeEvent(event)

    def show_items(self, category_id):
        self.current_category_id = category_id  # Track current category
        # Clear existing items
        for i in reversed(range(self.items_layout.count())):
            self.items_layout.itemAt(i).widget().setParent(None)
        # Get items for category
        items = self.db.get_loose_items_by_category(category_id)
        # Calculate columns based on width
        scroll_width = self.items_scroll.viewport().width()
        button_width = 150  # Approximate width of each button
        columns = max(1, scroll_width // button_width)
        # Display items in grid
        row = 0
        col = 0
        for item in items:
            item_button = QToolButton()
            
            # Display total price (with tax) for user
            total_price = item.get('total_price', item.get('base_price', item.get('price_per_kg', 0)))
            text = f"{item['name']}\n₹{total_price:.2f}/kg"
            if item.get('hsn_code'):
                text += f"\nHSN: {item['hsn_code']}"
            
            item_button.setText(text)
            item_button.setFont(QFont("Arial", 12))
            item_button.setMinimumHeight(180)
            item_button.setMinimumWidth(180)
            item_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            
            # If image exists, set as icon (large, on top)
            if getattr(sys, 'frozen', False):
                # Running as a PyInstaller bundle
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as a script
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            default_image_path = os.path.join(base_dir, 'data_base', 'images', 'ImageNotFound.png')
            image_path = item.get('image_path') or default_image_path
            if not os.path.isfile(image_path) or not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = default_image_path
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                item_button.setIcon(icon)
                item_button.setIconSize(QSize(128, 128))
            item_button.clicked.connect(lambda checked, item_data=item: self.select_item(item_data))
            self.items_layout.addWidget(item_button, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1
    
    def select_item(self, item_data):
        self.selected_item = item_data
        self.accept()

class CreateBillWindow(QMainWindow):
    def __init__(self, printer_instance=None):
        super().__init__()
        self.setWindowTitle("Create Bill")
        # Set window size based on screen resolution or sensible default
        screen = QApplication.primaryScreen()
        screen_size = screen.size() if screen else None
        default_width, default_height = 1280, 720
        if screen_size:
            width = min(default_width, screen_size.width())
            height = min(default_height, screen_size.height())
            self.resize(width, height)
        else:
            self.resize(default_width, default_height)
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.db = Database()
        # Use provided printer instance or create new one
        self.thermal_printer = printer_instance if printer_instance else ThermalPrinter()
        
        # Bill data
        self.bill_items = []
        self.total_amount = 0.0
        self.total_items = 0
        self.total_weight = 0.0
        self.total_sgst = 0.0
        self.total_cgst = 0.0
        
        self.init_ui()
        
        # Setup barcode scanner timer
        self.barcode_buffer = ""
        self.barcode_timer = QTimer()
        self.barcode_timer.timeout.connect(self.process_barcode)
        self.barcode_timer.setSingleShot(True)
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Bill display
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Bill table
        bill_label = QLabel("Current Bill:")
        bill_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(bill_label)
        
        self.bill_table = QTableWidget()
        self.bill_table.setColumnCount(9)
        self.bill_table.setHorizontalHeaderLabels([
            "Item Name", "HSN", "Qty", "Base Price", "SGST%", "CGST%", "Final Price", "Actions", "Remove"
        ])
        self.bill_table.setAlternatingRowColors(True)
        left_layout.addWidget(self.bill_table)
        
        header = self.bill_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Item Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # HSN
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Qty
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Base Price
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # SGST%
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # CGST%
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Final Price
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Actions
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Remove
        
        # Totals panel
        totals_frame = QFrame()
        totals_frame.setFrameStyle(QFrame.Box)
        totals_layout = QVBoxLayout()
        totals_frame.setLayout(totals_layout)
        
        self.items_count_label = QLabel("Total Items: 0")
        self.items_count_label.setFont(QFont("Arial", 12, QFont.Bold))
        totals_layout.addWidget(self.items_count_label)
        
        self.total_sgst_label = QLabel("Total SGST: ₹0.00")
        self.total_sgst_label.setFont(QFont("Arial", 12))
        totals_layout.addWidget(self.total_sgst_label)
        
        self.total_cgst_label = QLabel("Total CGST: ₹0.00")
        self.total_cgst_label.setFont(QFont("Arial", 12))
        totals_layout.addWidget(self.total_cgst_label)
        
        self.total_amount_label = QLabel("Total Amount: ₹0.00")
        self.total_amount_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.total_amount_label.setStyleSheet("color: #e74c3c;")
        totals_layout.addWidget(self.total_amount_label)
        
        left_layout.addWidget(totals_frame)
        
        # Finish button
        finish_btn = QPushButton("Finish & Print Bill")
        finish_btn.setFont(QFont("Arial", 14, QFont.Bold))
        finish_btn.setMinimumHeight(60)
        finish_btn.clicked.connect(self.finish_bill)
        finish_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        left_layout.addWidget(finish_btn)
        
        # Right panel - Item input
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        right_panel.setMaximumWidth(500)
        
        # Barcode input
        barcode_label = QLabel("Scan Barcode:")
        barcode_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(barcode_label)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setFont(QFont("Arial", 12))
        self.barcode_input.setPlaceholderText("Scan or enter barcode...")
        self.barcode_input.textChanged.connect(self.on_barcode_input)
        right_layout.addWidget(self.barcode_input)
        
        # Add loose items button
        loose_items_btn = QPushButton("Add Loose Items")
        loose_items_btn.setFont(QFont("Arial", 12, QFont.Bold))
        loose_items_btn.setMinimumHeight(50)
        loose_items_btn.clicked.connect(self.add_loose_items)
        loose_items_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        right_layout.addWidget(loose_items_btn)
        
        right_layout.addStretch()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
        
        # Focus on barcode input
        self.barcode_input.setFocus()
        
        # Set responsive styles
        self.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
                font-size: 12px;
            }
            QHeaderView::section {
                font-size: 12px;
                padding: 5px;
            }
        """)
    
    def on_barcode_input(self, text):
        """Handle barcode input with timer for keyboard wedge scanner"""
        self.barcode_buffer = text
        self.barcode_timer.start(500)  # Wait 500ms after last character
    
    def process_barcode(self):
        """Process the barcode after timer expires"""
        barcode = self.barcode_buffer.strip()
        if barcode:
            self.add_barcode_item(barcode)
            self.barcode_input.clear()
            self.barcode_buffer = ""
    
    def add_barcode_item(self, barcode):
        """Add item by barcode"""
        item = self.db.get_barcode_item(barcode)
        if not item:
            QMessageBox.warning(self, "Error", f"Item with barcode {barcode} not found!")
            return
        
        # Check if item already exists in bill
        for existing_item in self.bill_items:
            if existing_item.get('item_type') == 'barcode' and existing_item.get('barcode') == barcode:
                existing_item['quantity'] += 1
                self.calculate_item_totals(existing_item)
                self.update_bill_display()
                return
        
        # Add new item with GST calculations
        base_price = item.get('base_price', item.get('price', 0))
        sgst_percent = item.get('sgst_percent', 0)
        cgst_percent = item.get('cgst_percent', 0)
        
        bill_item = {
            'name': item['name'],
            'hsn_code': item.get('hsn_code', ''),
            'quantity': 1,
            'base_price': base_price,
            'sgst_percent': sgst_percent,
            'cgst_percent': cgst_percent,
            'item_type': 'barcode',
            'barcode': barcode
        }
        
        self.calculate_item_totals(bill_item)
        self.bill_items.append(bill_item)
        self.update_bill_display()
    
    def calculate_item_totals(self, item):
        """Calculate SGST, CGST, and final price for an item"""
        base_amount = item['quantity'] * item['base_price']
        sgst_amount = base_amount * item['sgst_percent'] / 100
        cgst_amount = base_amount * item['cgst_percent'] / 100
        final_price = base_amount + sgst_amount + cgst_amount
        
        item['sgst_amount'] = sgst_amount
        item['cgst_amount'] = cgst_amount
        item['final_price'] = final_price
    
    def add_loose_items(self):
        """Add loose items"""
        dialog = LooseCategoryDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_item:
            item_dialog = LooseItemDialog(dialog.selected_item, self)
            if item_dialog.exec_() == QDialog.Accepted:
                # Prepare new item
                new_item = {
                    'name': dialog.selected_item['name'],
                    'hsn_code': dialog.selected_item.get('hsn_code', ''),
                    'quantity': item_dialog.quantity,
                    'base_price': item_dialog.base_price,
                    # Always use DB values for SGST/CGST
                    'sgst_percent': dialog.selected_item.get('sgst_percent', 0),
                    'cgst_percent': dialog.selected_item.get('cgst_percent', 0),
                    'item_type': 'loose'
                }
                self.calculate_item_totals(new_item)
                # Check for existing loose item with same name and price
                for existing_item in self.bill_items:
                    if (
                        existing_item.get('item_type') == 'loose' and
                        existing_item.get('name') == new_item['name'] and
                        abs(existing_item.get('base_price', 0) - new_item['base_price']) < 0.01  # Allow small float diff
                    ):
                        # Same item and price: add quantity and update totals
                        existing_item['quantity'] += new_item['quantity']
                        self.calculate_item_totals(existing_item)
                        self.update_bill_display()
                        return
                # Otherwise, add as new row
                self.bill_items.append(new_item)
                self.update_bill_display()
    
    def update_bill_display(self):
        """Update the bill table and totals"""
        self.bill_table.setRowCount(len(self.bill_items))
        total_amount = 0
        total_items = len(self.bill_items)
        total_sgst = 0
        total_cgst = 0
        sgst_percent_sum = 0
        cgst_percent_sum = 0
        sgst_count = 0
        cgst_count = 0
        for row, item in enumerate(self.bill_items):
            # Item name
            self.bill_table.setItem(row, 0, QTableWidgetItem(item['name']))
            
            # HSN Code
            self.bill_table.setItem(row, 1, QTableWidgetItem(item.get('hsn_code', '')))
            
            # Quantity with +/- buttons
            quantity_widget = QWidget()
            quantity_layout = QHBoxLayout()
            quantity_layout.setContentsMargins(2, 0, 2, 0)
            
            minus_btn = QPushButton("-")
            minus_btn.setMaximumWidth(25)
            minus_btn.setMaximumHeight(25)
            minus_btn.clicked.connect(lambda checked, r=row: self.decrease_quantity(r))
            
            quantity_label = QLabel(f"{item['quantity']:.2f}")
            quantity_label.setAlignment(Qt.AlignCenter)
            quantity_label.setMinimumWidth(40)
            
            plus_btn = QPushButton("+")
            plus_btn.setMaximumWidth(25)
            plus_btn.setMaximumHeight(25)
            plus_btn.clicked.connect(lambda checked, r=row: self.increase_quantity(r))
            
            quantity_layout.addWidget(minus_btn)
            quantity_layout.addWidget(quantity_label)
            quantity_layout.addWidget(plus_btn)
            quantity_widget.setLayout(quantity_layout)
            
            self.bill_table.setCellWidget(row, 2, quantity_widget)
            
            # Base price
            self.bill_table.setItem(row, 3, QTableWidgetItem(f"₹{item['base_price']:.2f}"))
            
            # SGST %
            self.bill_table.setItem(row, 4, QTableWidgetItem(f"{item['sgst_percent']:.1f}%"))
            
            # CGST %
            self.bill_table.setItem(row, 5, QTableWidgetItem(f"{item['cgst_percent']:.1f}%"))
            
            # Final price
            self.bill_table.setItem(row, 6, QTableWidgetItem(f"₹{item['final_price']:.2f}"))
            
            # Actions (Edit)
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 10px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_item(r))
            self.bill_table.setCellWidget(row, 7, edit_btn)
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 10px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.bill_table.setCellWidget(row, 8, remove_btn)
            
            # Calculate totals
            total_amount += item['final_price']
            total_sgst += item['sgst_amount']
            total_cgst += item['cgst_amount']
            if item.get('sgst_percent', 0) > 0:
                sgst_percent_sum += item['sgst_percent']
                sgst_count += 1
            if item.get('cgst_percent', 0) > 0:
                cgst_percent_sum += item['cgst_percent']
                cgst_count += 1
        # Update totals display
        self.total_amount = total_amount
        self.total_items = total_items
        self.total_sgst = total_sgst
        self.total_cgst = total_cgst
        self.items_count_label.setText(f"Total Items: {total_items}")
        avg_sgst = (sgst_percent_sum / sgst_count) if sgst_count else 0
        avg_cgst = (cgst_percent_sum / cgst_count) if cgst_count else 0
        self.total_sgst_label.setText(f"Avg SGST%: {avg_sgst:.2f}%")
        self.total_cgst_label.setText(f"Avg CGST%: {avg_cgst:.2f}%")
        self.total_amount_label.setText(f"Total Amount: ₹{total_amount:.2f}")
    
    def increase_quantity(self, row):
        """Increase item quantity"""
        if row < len(self.bill_items):
            if self.bill_items[row]['item_type'] == 'barcode':
                self.bill_items[row]['quantity'] += 1
            else:
                self.bill_items[row]['quantity'] += 0.1
            self.calculate_item_totals(self.bill_items[row])
            self.update_bill_display()
    
    def decrease_quantity(self, row):
        """Decrease item quantity"""
        if row < len(self.bill_items):
            if self.bill_items[row]['item_type'] == 'barcode':
                if self.bill_items[row]['quantity'] > 1:
                    self.bill_items[row]['quantity'] -= 1
                    self.calculate_item_totals(self.bill_items[row])
                    self.update_bill_display()
            else:  # loose item
                if self.bill_items[row]['quantity'] > 0.1:
                    self.bill_items[row]['quantity'] -= 0.1
                    self.calculate_item_totals(self.bill_items[row])
                    self.update_bill_display()
    
    def edit_item(self, row):
        """Edit item quantity and final price for loose items"""
        if row >= len(self.bill_items):
            return
        item = self.bill_items[row]
        if item['item_type'] == 'loose':
            # Prepare item_data for dialog
            item_data = {
                'name': item['name'],
                'hsn_code': item.get('hsn_code', ''),
                'sgst_percent': item.get('sgst_percent', 0),
                'cgst_percent': item.get('cgst_percent', 0),
                'total_price': item.get('final_price', 0),
            }
            dialog = LooseItemDialog(item_data, self)
            dialog.quantity_input.setValue(item['quantity'])
            dialog.final_price_input.setValue(item.get('final_price', 0))
            if dialog.exec_() == QDialog.Accepted:
                item['quantity'] = dialog.quantity
                item['base_price'] = dialog.base_price
                item['final_price'] = dialog.final_price
                # SGST/CGST remain from DB
                self.calculate_item_totals(item)
                self.update_bill_display()
        else:
            # For barcode items, keep old logic (edit quantity only)
            quantity, ok = QInputDialog.getDouble(
                self, "Edit Quantity", 
                f"Enter new quantity for {item['name']}:",
                item['quantity'], 0.01, 999.99, 2
            )
            if ok:
                item['quantity'] = quantity
                self.calculate_item_totals(item)
                self.update_bill_display()
    
    def remove_item(self, row):
        """Remove item from bill"""
        if row < len(self.bill_items):
            del self.bill_items[row]
            self.update_bill_display()
    
    def finish_bill(self):
        """Finish the bill and print"""
        if not self.bill_items:
            QMessageBox.warning(self, "Error", "Please add items to the bill first!")
            return
        
        # Get customer names for autocomplete
        customer_names = self.db.get_customer_names()
        
        # Get customer information
        customer_dialog = CustomerInfoDialog(customer_names, self)
        if customer_dialog.exec_() != QDialog.Accepted:
            return
        
        customer_name = customer_dialog.customer_name
        customer_phone = customer_dialog.customer_phone.strip()
        
        # --- ENFORCE +91 FORMAT AND VALIDATE ---
        phone_digits = re.sub(r'\D', '', customer_phone)
        if len(phone_digits) == 10:
            customer_phone = f'+91{phone_digits}'
        elif len(phone_digits) == 12 and phone_digits.startswith('91'):
            customer_phone = f'+{phone_digits}'
        elif customer_phone.startswith('+91') and len(phone_digits) == 12:
            pass  # already correct
        else:
            QMessageBox.warning(self, "Invalid Phone Number", "Please enter a valid 10-digit phone number. Only Indian numbers (+91) are supported for WhatsApp sending.")
            return
        
        # Save bill to database
        bill_id = self.db.save_bill(
            customer_name, customer_phone, self.bill_items,
            self.total_amount, self.total_items, self.total_weight,
            self.total_sgst, self.total_cgst
        )
        
        # Prepare bill data for printing
        bill_data = {
            'id': bill_id,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'total_amount': self.total_amount,
            'total_items': self.total_items,
            'total_weight': self.total_weight,
            'total_sgst': self.total_sgst,
            'total_cgst': self.total_cgst,
            'items': self.bill_items
        }
        
        # --- Print to console and perform both actions ---
        print("[INFO] Starting thermal print...")
        thermal_success = False
        if self.thermal_printer.connect_usb_printer():
            thermal_success = self.thermal_printer.print_bill(bill_data)
            if thermal_success:
                print("[INFO] Thermal print completed.")
            else:
                print("[ERROR] Thermal print failed.")
                QMessageBox.warning(self, "Print Error", "Thermal print failed!")
        else:
            print("[ERROR] Could not connect to thermal printer.")
            QMessageBox.warning(self, "Printer Error", "Could not connect to thermal printer!")
        
        print("[INFO] Sending bill to WhatsApp...")
        self.save_and_send_whatsapp(bill_data, customer_name, customer_phone)
        print("[INFO] WhatsApp send triggered.")
        
        # Clear the bill
        self.bill_items = []
        self.update_bill_display()
        self.barcode_input.setFocus()

    def share_via_whatsapp(self, bill_data, customer_name):
        """Share bill via WhatsApp"""
        try:
            # Create a temporary widget to render the bill for WhatsApp sharing
            bill_widget = self.create_bill_widget_for_sharing(bill_data)
            
            # Open WhatsApp dialog
            whatsapp_dialog = WhatsAppDialog(bill_widget, customer_name, self)
            if whatsapp_dialog.exec_() == QDialog.Accepted:
                # Optionally save customer data if requested
                customer_data = whatsapp_dialog.get_customer_data()
                if customer_data['save_to_db'] and customer_data['name']:
                    # Customer data is already saved in the bill, no need to save again
                    pass
            
            # Clean up the temporary widget
            bill_widget.deleteLater()
            
        except Exception as e:
            QMessageBox.critical(self, "WhatsApp Error", f"Failed to share via WhatsApp: {str(e)}")
    
    def create_bill_widget_for_sharing(self, bill_data):
        """Create a widget containing the bill layout for image capture, matching the requested format"""
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHBoxLayout
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont

        n_items = len(bill_data['items'])
        table_row_height = 36  # Approximate row height in pixels
        table_header_height = 40
        table_height = (n_items + 1) * table_row_height + table_header_height  # +1 for total row
        widget_height = 250 + table_height + 120  # 250 for header/info, 120 for footer, adjust as needed
        widget_width = 1123

        widget = QWidget()
        widget.setFixedSize(widget_width, widget_height)
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: Arial;
            }
        """)
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # --- SHOP DETAILS (fetch once and reuse) ---
        if hasattr(self, '_cached_admin_details'):
            admin_details = self._cached_admin_details
        else:
            db = Database()
            admin_details = db.get_admin_details() or {}
            self._cached_admin_details = admin_details
        shop_name = admin_details.get('shop_name', 'Shop Name')
        shop_address = admin_details.get('address', 'Shop Address')
        shop_phone = admin_details.get('phone_number', 'Shop Phone')
        # Shop name bold, address and phone not bold, emojis
        shop_label = QLabel(f"<b>{shop_name}</b><br/>📍{shop_address}<br/>📞{shop_phone}")
        shop_label.setFont(QFont("Arial", 15))
        shop_label.setAlignment(Qt.AlignCenter)
        shop_label.setStyleSheet("padding: 8px; border-bottom: 2px solid #000;")
        layout.addWidget(shop_label)

        # --- BILL INFO ROW: Bill ID (left), Date (right, date only) ---
        info_row = QHBoxLayout()
        bill_id_label = QLabel(f"Bill ID: {bill_data['id']}")
        bill_id_label.setFont(QFont("Arial", 10))
        bill_id_label.setAlignment(Qt.AlignLeft)
        info_row.addWidget(bill_id_label, alignment=Qt.AlignLeft)
        info_row.addStretch()
        # Format date only
        date_label = QLabel(f"Date: {datetime.now().strftime('%d/%m/%Y')}")
        date_label.setFont(QFont("Arial", 10))
        date_label.setAlignment(Qt.AlignRight)
        info_row.addWidget(date_label, alignment=Qt.AlignRight)
        layout.addLayout(info_row)

        # --- CUSTOMER NAME (left) AND TIME (right) ROW ---
        customer_time_row = QHBoxLayout()
        customer_time_row.setContentsMargins(0, 0, 0, 0)  # Remove all margins

        customer_label = QLabel(f"Customer: {bill_data['customer_name']}")
        customer_label.setFont(QFont("Arial", 10))
        customer_label.setAlignment(Qt.AlignLeft)
        customer_label.setStyleSheet("padding: 0px; margin: 0px;")  # Remove all padding/margin
        customer_time_row.addWidget(customer_label, alignment=Qt.AlignLeft)

        customer_time_row.addStretch()

        time_label = QLabel(f"Time: {datetime.now().strftime('%I:%M %p')}")
        time_label.setFont(QFont("Arial", 10))
        time_label.setAlignment(Qt.AlignRight)
        customer_time_row.addWidget(time_label, alignment=Qt.AlignRight)

        layout.addLayout(customer_time_row)

        # --- TABLE HEADER ---
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "HSN Code", "Item", "Qty", "Base Price", "SGST (%/₹)", "CGST (%/₹)", "Final Price"
        ])
        table.setRowCount(n_items + 1)  # +1 for total row
        table.setStyleSheet("""
            QTableWidget { font-size: 15px; }
            QHeaderView::section { font-size: 16px; font-weight: bold; background: #e0e0e0; }
        """)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setFocusPolicy(Qt.NoFocus)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setFixedHeight(table_height)

        # Set column widths for A4 landscape (sum should be <= 1123)
        table.setColumnWidth(0, 120)   # HSN
        table.setColumnWidth(1, 370)   # Item
        table.setColumnWidth(2, 90)    # Qty
        table.setColumnWidth(3, 170)   # Base Price
        table.setColumnWidth(4, 120)   # SGST
        table.setColumnWidth(5, 120)   # CGST
        # Final Price will stretch to fill remaining space

        # Set row heights
        for row in range(n_items + 1):
            table.setRowHeight(row, table_row_height)
        table.horizontalHeader().setFixedHeight(table_header_height)

        # --- FILL TABLE ROWS ---
        total_base = 0
        total_sgst = 0
        total_cgst = 0
        total_final = 0
        for row, item in enumerate(bill_data['items']):
            hsn = str(item.get('hsn_code', ''))
            name = str(item.get('name', ''))
            qty = f"{item.get('quantity', 0):.2f}"
            base_price_val = item.get('base_price', 0)
            base_price = f"₹{base_price_val:.2f}"
            sgst_percent = item.get('sgst_percent', 0)
            sgst_amt = item.get('sgst_amount', 0)
            cgst_percent = item.get('cgst_percent', 0)
            cgst_amt = item.get('cgst_amount', 0)
            final_price_val = item.get('final_price', 0)
            final_price = f"₹{final_price_val:.2f}"

            table.setItem(row, 0, QTableWidgetItem(hsn))
            table.setItem(row, 1, QTableWidgetItem(name))
            table.setItem(row, 2, QTableWidgetItem(qty))
            table.setItem(row, 3, QTableWidgetItem(base_price))
            table.setItem(row, 4, QTableWidgetItem(f"{sgst_percent:.1f}%\n₹{sgst_amt:.2f}"))
            table.setItem(row, 5, QTableWidgetItem(f"{cgst_percent:.1f}%\n₹{cgst_amt:.2f}"))
            table.setItem(row, 6, QTableWidgetItem(final_price))

            total_base += base_price_val
            total_sgst += sgst_amt
            total_cgst += cgst_amt
            total_final += final_price_val

        # --- TOTAL ROW ---
        total_row = n_items
        table.setItem(total_row, 0, QTableWidgetItem(""))
        table.setItem(total_row, 1, QTableWidgetItem("Total"))
        table.setItem(total_row, 2, QTableWidgetItem(""))
        table.setItem(total_row, 3, QTableWidgetItem(f"₹{total_base:.2f}"))
        table.setItem(total_row, 4, QTableWidgetItem(f"₹{total_sgst:.2f}"))
        table.setItem(total_row, 5, QTableWidgetItem(f"₹{total_cgst:.2f}"))
        table.setItem(total_row, 6, QTableWidgetItem(f"₹{total_final:.2f}"))
        for col in [1,3,4,5,6]:
            item = table.item(total_row, col)
            if item:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
        table.setSpan(total_row, 0, 1, 1)  # No span, just label in Item column

        layout.addWidget(table)

        # --- GRAND TOTAL FOOTER ---
        total_label = QLabel(f"GRAND TOTAL: ₹{total_final:.2f}")
        total_label.setFont(QFont("Arial", 16, QFont.Bold))
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("padding: 10px; background-color: #e8f4fd; border: 2px solid #3498db;")
        layout.addWidget(total_label)

        # Footer label with random thank you message
        db = Database()
        admin_details = db.get_admin_details() or {}
        shop_name = admin_details.get('shop_name', 'Shop Name')
        thank_you_messages = [
            f"Thank you for shopping in {shop_name}!",
            f"We appreciate your business at {shop_name}.",
            f"Hope to see you again at {shop_name}!",
            f"Your support means a lot to {shop_name}!",
            f"Thanks for choosing {shop_name}!",
            f"Thank you for shopping at {shop_name}! We hope you had a great experience.",
            f"Your purchase at {shop_name} made our day!",
            f"Thank you for trusting {shop_name}!",
            f"{shop_name} is grateful for your business!",
            f"Thanks for shopping local with {shop_name}!",
        ]
        footer_label = QLabel(random.choice(thank_you_messages))
        footer_label.setFont(QFont("Arial", 12))
        footer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer_label)

        # --- QR CODE (bottom left) ---
        qr_data = admin_details.get('location', 'https://maps.app.goo.gl/qthz7Drt5WBdwBj49?g_st=aw')
        qr = qrcode.QRCode(box_size=2, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_size = 80
        img = img.resize((qr_size, qr_size))
        qimg = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format_RGB888)
        qr_pixmap = QPixmap.fromImage(qimg)
        qr_label = QLabel()
        qr_label.setPixmap(qr_pixmap)
        qr_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        qr_text = QLabel("Scan QR for location")
        qr_text.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        qr_layout = QVBoxLayout()
        qr_layout.addWidget(qr_label)
        qr_layout.addWidget(qr_text)
        qr_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        # Add QR layout to the main layout at the bottom
        layout.addLayout(qr_layout)
        layout.addStretch()
        return widget

    def send_bill_image_via_whatsapp(self, phone, image_path, caption):
        import pywhatkit
        import time
        pywhatkit.sendwhats_image(phone, image_path, caption=caption, wait_time=30, tab_close=False, close_time=3)
        # Wait for WhatsApp Web to be ready, then press Enter to send
        try:
            import pyautogui
            time.sleep(10)  # Increased wait time for WhatsApp Web to load
            pyautogui.press('enter')
            time.sleep(3)  # Wait for message to be sent
            pyautogui.hotkey('ctrl', 'w')  # Close the tab
        except Exception as e:
            print(f"pyautogui not available or failed to press enter/close tab: {e}")

    def save_and_send_whatsapp(self, bill_data, customer_name, customer_phone):
        """Save the bill as an image in a 'bills' folder and send via WhatsApp using pywhatkit, ensuring the correct Chrome profile is used."""
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            from PyQt5.QtCore import QBuffer, QIODevice
            import os
            # Create a widget for the bill
            bill_widget = self.create_bill_widget_for_sharing(bill_data)
            # Render to QPixmap
            pixmap = bill_widget.grab()
            # Ensure 'data_base/bills' folder exists in both development and PyInstaller modes
            if getattr(sys, 'frozen', False):
                # Running as a PyInstaller bundle
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as a script
                base_dir = os.getcwd()
            bills_dir = os.path.join(base_dir, 'data_base', 'bills')
            os.makedirs(bills_dir, exist_ok=True)
            # Save to file in 'data_base/bills' folder
            image_path = os.path.join(bills_dir, f"bill_{bill_data['id']}.png")
            pixmap.save(image_path, 'PNG')
            # Send via WhatsApp if phone number is valid
            if customer_phone and customer_phone.startswith('+') and len(customer_phone) > 7:
                try:
                    db = Database()
                    admin_details = db.get_admin_details() or {}
                    shop_name = admin_details.get('shop_name', 'Shop Name')
                    greetings = ["Hi", "Hello", "Hey", "Dear"]
                    thanks = [
                        "Thanks for shopping with us!",
                        "We appreciate your purchase!",
                        "Hope to see you again!",
                    ]
                    caption = f"{random.choice(greetings)} {customer_name},\nBill #{bill_data['id']} from {shop_name} is attached.\n{random.choice(thanks)}"
                    QMessageBox.information(self, "Debug", f"About to send bill image via WhatsApp\nNumber: {customer_phone}\nImage: {image_path}")
                    print(f"About to send bill image via WhatsApp\nNumber: {customer_phone}\nImage: {image_path}")
                    self.send_bill_image_via_whatsapp(customer_phone, image_path, caption)
                    QMessageBox.information(self, "WhatsApp", "✅ Bill sent via WhatsApp!")
                    print("✅ Bill sent via WhatsApp!")
                except Exception as e:
                    QMessageBox.warning(self, "WhatsApp Error", f"❌ Failed to send bill via WhatsApp.\n{str(e)}")
                    print(f"❌ Failed to send bill via WhatsApp. {str(e)}")
            else:
                QMessageBox.information(self, "WhatsApp", "Bill image saved, but phone number is invalid or not provided.")
                print("Bill image saved, but phone number is invalid or not provided.")
            bill_widget.deleteLater()
        except Exception as e:
            QMessageBox.critical(self, "WhatsApp Error", f"Failed to share via WhatsApp: {str(e)}")
            print(f"Failed to share via WhatsApp: {str(e)}")

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Adjust font sizes based on window size
        width = self.width()
        if width < 1200:
            font_size = 10
        elif width < 1600:
            font_size = 12
        else:
            font_size = 14
        
        # Update table font sizes
        self.bill_table.setStyleSheet(f"""
            QTableWidget {{
                font-size: {font_size}px;
            }}
            QTableWidget::item {{
                padding: 5px;
                font-size: {font_size}px;
            }}
            QHeaderView::section {{
                font-size: {font_size}px;
                padding: 5px;
            }}
        """)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if not self.isMinimized():
                # Center the window and restore its size
                screen = self.screen() if hasattr(self, 'screen') else QApplication.primaryScreen()
                if hasattr(screen, 'geometry'):
                    center_point = screen.geometry().center()
                    frame_geom = self.frameGeometry()
                    frame_geom.moveCenter(center_point)
                    self.move(frame_geom.topLeft())
                self.showNormal()
        super().changeEvent(event)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = CreateBillWindow()
    window.showMaximized()
    sys.exit(app.exec_())