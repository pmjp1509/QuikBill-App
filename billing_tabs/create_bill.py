import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QDialog, QGridLayout, QSpinBox,
                             QDoubleSpinBox, QMessageBox, QFrame, QScrollArea,
                             QTextEdit, QDialogButtonBox, QInputDialog, QSizePolicy,
                             QHeaderView, QToolButton, QCompleter, QApplication)
from PyQt5.QtCore import Qt, QTimer, QEvent, QSize, QStringListModel
from PyQt5.QtGui import QFont, QPixmap, QIcon
from data_base.database import Database
from billing_tabs.thermal_printer import ThermalPrinter
from PIL import Image
import os

class CustomerInfoDialog(QDialog):
    def __init__(self, customer_names=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Information")
        self.setModal(True)
        self.resize(400, 200)
        
        self.customer_name = ""
        self.customer_phone = ""
        self.customer_names = customer_names or []
        
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
        self.base_price = item_data.get('base_price', item_data.get('price_per_kg', 0))
        self.sgst_percent = item_data.get('sgst_percent', 0)
        self.cgst_percent = item_data.get('cgst_percent', 0)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Item name
        name_label = QLabel(f"Item: {self.item_data['name']}")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(name_label)
        
        # HSN Code
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
        
        # Base price per kg
        layout.addWidget(QLabel("Base Price per kg (₹):"))
        self.base_price_input = QDoubleSpinBox()
        self.base_price_input.setMinimum(0.01)
        self.base_price_input.setMaximum(9999.99)
        self.base_price_input.setDecimals(2)
        self.base_price_input.setValue(self.base_price)
        self.base_price_input.valueChanged.connect(self.update_calculations)
        layout.addWidget(self.base_price_input)
        
        # SGST %
        layout.addWidget(QLabel("SGST (%):"))
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setMinimum(0.0)
        self.sgst_input.setMaximum(50.0)
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(self.sgst_percent)
        self.sgst_input.valueChanged.connect(self.update_calculations)
        layout.addWidget(self.sgst_input)
        
        # CGST %
        layout.addWidget(QLabel("CGST (%):"))
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setMinimum(0.0)
        self.cgst_input.setMaximum(50.0)
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(self.cgst_percent)
        self.cgst_input.valueChanged.connect(self.update_calculations)
        layout.addWidget(self.cgst_input)
        
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
        
        # Initial calculation
        self.update_calculations()
    
    def update_calculations(self):
        quantity = self.quantity_input.value()
        base_price = self.base_price_input.value()
        sgst_percent = self.sgst_input.value()
        cgst_percent = self.cgst_input.value()
        
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
        self.base_price = self.base_price_input.value()
        self.sgst_percent = self.sgst_input.value()
        self.cgst_percent = self.cgst_input.value()
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Bill")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set size policy for responsive design
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.db = Database()
        self.thermal_printer = ThermalPrinter()
        
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
                bill_item = {
                    'name': dialog.selected_item['name'],
                    'hsn_code': dialog.selected_item.get('hsn_code', ''),
                    'quantity': item_dialog.quantity,
                    'base_price': item_dialog.base_price,
                    'sgst_percent': item_dialog.sgst_percent,
                    'cgst_percent': item_dialog.cgst_percent,
                    'item_type': 'loose'
                }
                
                self.calculate_item_totals(bill_item)
                self.bill_items.append(bill_item)
                self.update_bill_display()
    
    def update_bill_display(self):
        """Update the bill table and totals"""
        self.bill_table.setRowCount(len(self.bill_items))
        
        total_amount = 0
        total_items = len(self.bill_items)
        total_sgst = 0
        total_cgst = 0
        
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
        
        # Update totals display
        self.total_amount = total_amount
        self.total_items = total_items
        self.total_sgst = total_sgst
        self.total_cgst = total_cgst
        
        self.items_count_label.setText(f"Total Items: {total_items}")
        self.total_sgst_label.setText(f"Total SGST: ₹{total_sgst:.2f}")
        self.total_cgst_label.setText(f"Total CGST: ₹{total_cgst:.2f}")
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
        """Edit item quantity"""
        if row >= len(self.bill_items):
            return
        
        item = self.bill_items[row]
        
        # Get new quantity
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
        customer_phone = customer_dialog.customer_phone
        
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
        
        # Try to print
        try:
            # Try USB connection first
            if self.thermal_printer.connect_usb_printer():
                if self.thermal_printer.print_bill(bill_data):
                    QMessageBox.information(self, "Success", 
                                            f"Bill #{bill_id} saved and printed successfully!")
                else:
                    QMessageBox.warning(self, "Print Error", 
                                        f"Bill #{bill_id} saved but printing failed!")
            else:
                QMessageBox.warning(self, "Printer Error", 
                                    f"Bill #{bill_id} saved but printer not connected!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Bill saved but printing failed: {str(e)}")
        
        # Clear the bill
        self.bill_items = []
        self.update_bill_display()
        self.barcode_input.setFocus()

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