import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QDialog, QGridLayout, QSpinBox,
                             QDoubleSpinBox, QMessageBox, QFrame, QScrollArea,
                             QTextEdit, QDialogButtonBox, QInputDialog, QSizePolicy,
                             QHeaderView, QToolButton)
from PyQt5.QtCore import Qt, QTimer, QEvent, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon
from data_base.database import Database
from billing_tabs.thermal_printer import ThermalPrinter
from PIL import Image
import os

class CustomerInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Information")
        self.setModal(True)
        self.resize(400, 200)
        
        self.customer_name = ""
        self.customer_phone = ""
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Customer Name
        layout.addWidget(QLabel("Customer Name (Required):"))
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 12))
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
        self.resize(400, 250)
        
        self.quantity = 0
        self.price_per_kg = item_data['price_per_kg']
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Item name
        name_label = QLabel(f"Item: {self.item_data['name']}")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(name_label)
        
        # Quantity
        layout.addWidget(QLabel("Quantity (kg):"))
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(999.99)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setSingleStep(0.1)
        self.quantity_input.setValue(1.0)
        self.quantity_input.valueChanged.connect(self.update_total)
        layout.addWidget(self.quantity_input)
        
        # Price per kg
        layout.addWidget(QLabel("Price per kg (₹):"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0.01)
        self.price_input.setMaximum(9999.99)
        self.price_input.setDecimals(2)
        self.price_input.setValue(self.price_per_kg)
        self.price_input.valueChanged.connect(self.update_total)
        layout.addWidget(self.price_input)
        
        # Total
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.total_label)
        
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
        
        # Initial total calculation
        self.update_total()
    
    def update_total(self):
        quantity = self.quantity_input.value()
        price = self.price_input.value()
        total = quantity * price
        self.total_label.setText(f"Total: ₹{total:.2f}")
    
    def accept_item(self):
        self.quantity = self.quantity_input.value()
        self.price_per_kg = self.price_input.value()
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
            text = f"{item['name']}\n₹{item['price_per_kg']:.2f}/kg"
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
        self.setGeometry(100, 100, 1200, 800)
        
        self.db = Database()
        self.thermal_printer = ThermalPrinter()
        
        # Bill data
        self.bill_items = []
        self.total_amount = 0.0
        self.total_items = 0
        self.total_weight = 0.0
        
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
        
        # Left panel - Item input
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
        
        # Right panel - Bill display
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Bill table
        bill_label = QLabel("Current Bill:")
        bill_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(bill_label)
        
        self.bill_table = QTableWidget()
        self.bill_table.setColumnCount(6)
        self.bill_table.setHorizontalHeaderLabels([
            "Item Name", "Quantity", "Unit Price", "Subtotal", "Actions", "Remove"
        ])
        self.bill_table.setAlternatingRowColors(True)
        left_layout.addWidget(self.bill_table)
        
        header = self.bill_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Totals panel
        totals_frame = QFrame()
        totals_frame.setFrameStyle(QFrame.Box)
        totals_layout = QVBoxLayout()
        totals_frame.setLayout(totals_layout)
        
        self.items_count_label = QLabel("Total Items: 0")
        self.items_count_label.setFont(QFont("Arial", 12, QFont.Bold))
        totals_layout.addWidget(self.items_count_label)
        
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
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
        
        # Focus on barcode input
        self.barcode_input.setFocus()
    
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
                existing_item['subtotal'] = existing_item['quantity'] * existing_item['unit_price']
                self.update_bill_display()
                return
        
        # Add new item
        bill_item = {
            'name': item['name'],
            'quantity': 1,
            'unit_price': item['price'],
            'subtotal': item['price'],
            'item_type': 'barcode',
            'barcode': barcode
        }
        
        self.bill_items.append(bill_item)
        self.update_bill_display()
    
    def add_loose_items(self):
        """Add loose items"""
        dialog = LooseCategoryDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_item:
            item_dialog = LooseItemDialog(dialog.selected_item, self)
            if item_dialog.exec_() == QDialog.Accepted:
                bill_item = {
                    'name': dialog.selected_item['name'],
                    'quantity': item_dialog.quantity,
                    'unit_price': item_dialog.price_per_kg,
                    'subtotal': item_dialog.quantity * item_dialog.price_per_kg,
                    'item_type': 'loose'
                }
                
                self.bill_items.append(bill_item)
                self.update_bill_display()
    
    def update_bill_display(self):
        """Update the bill table and totals"""
        self.bill_table.setRowCount(len(self.bill_items))
        
        total_amount = 0
        total_items = len(self.bill_items)
        
        for row, item in enumerate(self.bill_items):
            # Item name
            self.bill_table.setItem(row, 0, QTableWidgetItem(item['name']))
            
            # Quantity with +/- buttons
            quantity_widget = QWidget()
            quantity_layout = QHBoxLayout()
            quantity_layout.setContentsMargins(5, 0, 5, 0)
            
            minus_btn = QPushButton("-")
            minus_btn.setMaximumWidth(30)
            minus_btn.clicked.connect(lambda checked, r=row: self.decrease_quantity(r))
            
            quantity_label = QLabel(f"{item['quantity']:.2f}")
            quantity_label.setAlignment(Qt.AlignCenter)
            
            plus_btn = QPushButton("+")
            plus_btn.setMaximumWidth(30)
            plus_btn.clicked.connect(lambda checked, r=row: self.increase_quantity(r))
            
            quantity_layout.addWidget(minus_btn)
            quantity_layout.addWidget(quantity_label)
            quantity_layout.addWidget(plus_btn)
            quantity_widget.setLayout(quantity_layout)
            
            self.bill_table.setCellWidget(row, 1, quantity_widget)
            
            # Unit price
            self.bill_table.setItem(row, 2, QTableWidgetItem(f"₹{item['unit_price']:.2f}"))
            
            # Subtotal
            self.bill_table.setItem(row, 3, QTableWidgetItem(f"₹{item['subtotal']:.2f}"))
            
            # Actions (Edit)
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_item(r))
            self.bill_table.setCellWidget(row, 4, edit_btn)
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.bill_table.setCellWidget(row, 5, remove_btn)
            
            # Calculate totals
            total_amount += item['subtotal']
        
        # Update totals display
        self.total_amount = total_amount
        self.total_items = total_items
        
        self.items_count_label.setText(f"Total Items: {total_items}")
        self.total_amount_label.setText(f"Total Amount: ₹{total_amount:.2f}")
    
    def increase_quantity(self, row):
        """Increase item quantity"""
        if row < len(self.bill_items):
            self.bill_items[row]['quantity'] += 1 if self.bill_items[row]['item_type'] == 'barcode' else 0.1
            self.bill_items[row]['subtotal'] = self.bill_items[row]['quantity'] * self.bill_items[row]['unit_price']
            self.update_bill_display()
    
    def decrease_quantity(self, row):
        """Decrease item quantity"""
        if row < len(self.bill_items):
            if self.bill_items[row]['item_type'] == 'barcode':
                if self.bill_items[row]['quantity'] > 1:
                    self.bill_items[row]['quantity'] -= 1
                    self.bill_items[row]['subtotal'] = self.bill_items[row]['quantity'] * self.bill_items[row]['unit_price']
                    self.update_bill_display()
            else:  # loose item
                if self.bill_items[row]['quantity'] > 0.1:
                    self.bill_items[row]['quantity'] -= 0.1
                    self.bill_items[row]['subtotal'] = self.bill_items[row]['quantity'] * self.bill_items[row]['unit_price']
                    self.update_bill_display()
    
    def edit_item(self, row):
        """Edit item quantity or price"""
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
            item['subtotal'] = quantity * item['unit_price']
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
        
        # Get customer information
        customer_dialog = CustomerInfoDialog(self)
        if customer_dialog.exec_() != QDialog.Accepted:
            return
        
        customer_name = customer_dialog.customer_name
        customer_phone = customer_dialog.customer_phone
        
        # Save bill to database
        bill_id = self.db.save_bill(
            customer_name, customer_phone, self.bill_items,
            self.total_amount, self.total_items, self.total_weight
        )
        
        # Prepare bill data for printing
        bill_data = {
            'id': bill_id,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'total_amount': self.total_amount,
            'total_items': self.total_items,
            'total_weight': self.total_weight,
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