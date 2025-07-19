import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QTabWidget, QDialog, QGridLayout,
                             QDoubleSpinBox, QMessageBox, QFileDialog, QComboBox,
                             QHeaderView, QAbstractItemView, QDialogButtonBox,
                             QSpinBox, QSizePolicy, QApplication)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont, QPixmap
from data_base.database import Database
from PIL import Image

class BarcodeItemDialog(QDialog):
    def __init__(self, item_data=None, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setWindowTitle("Add/Edit Barcode Item" if not item_data else "Edit Barcode Item")
        self.setModal(True)
        self.resize(500, 600)
        
        self.init_ui()
        
        if item_data:
            self.load_item_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create form layout
        form_layout = QGridLayout()
        
        # Barcode
        form_layout.addWidget(QLabel("Barcode:"), 0, 0)
        self.barcode_input = QLineEdit()
        self.barcode_input.setFont(QFont("Arial", 12))
        form_layout.addWidget(self.barcode_input, 0, 1)
        
        # Item Name
        form_layout.addWidget(QLabel("Item Name:"), 1, 0)
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 12))
        form_layout.addWidget(self.name_input, 1, 1)
        
        # HSN Code
        form_layout.addWidget(QLabel("HSN Code:"), 2, 0)
        self.hsn_input = QLineEdit()
        self.hsn_input.setFont(QFont("Arial", 12))
        form_layout.addWidget(self.hsn_input, 2, 1)
        
        # Quantity
        form_layout.addWidget(QLabel("Quantity:"), 3, 0)
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setValue(0)
        form_layout.addWidget(self.quantity_input, 3, 1)
        
        # Base Price
        form_layout.addWidget(QLabel("Base Price (₹):"), 4, 0)
        self.base_price_input = QDoubleSpinBox()
        self.base_price_input.setMinimum(0.01)
        self.base_price_input.setMaximum(99999.99)
        self.base_price_input.setDecimals(2)
        self.base_price_input.setValue(1.00)
        self.base_price_input.valueChanged.connect(self.calculate_total_price)
        form_layout.addWidget(self.base_price_input, 4, 1)
        
        # SGST %
        form_layout.addWidget(QLabel("SGST (%):"), 5, 0)
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setMinimum(0.0)
        self.sgst_input.setMaximum(50.0)
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(0.0)
        self.sgst_input.valueChanged.connect(self.calculate_total_price)
        form_layout.addWidget(self.sgst_input, 5, 1)
        
        # CGST %
        form_layout.addWidget(QLabel("CGST (%):"), 6, 0)
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setMinimum(0.0)
        self.cgst_input.setMaximum(50.0)
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(0.0)
        self.cgst_input.valueChanged.connect(self.calculate_total_price)
        form_layout.addWidget(self.cgst_input, 6, 1)
        
        # Total Price (calculated)
        form_layout.addWidget(QLabel("Total Price (₹):"), 7, 0)
        self.total_price_label = QLabel("₹1.00")
        self.total_price_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_price_label.setStyleSheet("color: #e74c3c; padding: 5px; border: 1px solid #ccc;")
        form_layout.addWidget(self.total_price_label, 7, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Initial calculation
        self.calculate_total_price()
    
    def calculate_total_price(self):
        """Calculate and display total price"""
        base_price = self.base_price_input.value()
        sgst_percent = self.sgst_input.value()
        cgst_percent = self.cgst_input.value()
        
        total_price = base_price + (base_price * sgst_percent / 100) + (base_price * cgst_percent / 100)
        self.total_price_label.setText(f"₹{total_price:.2f}")
    
    def load_item_data(self):
        """Load existing item data"""
        if self.item_data:
            self.barcode_input.setText(self.item_data['barcode'])
            self.name_input.setText(self.item_data['name'])
            self.hsn_input.setText(self.item_data.get('hsn_code', ''))
            self.quantity_input.setValue(self.item_data.get('quantity', 0))
            self.base_price_input.setValue(self.item_data.get('base_price', self.item_data.get('price', 0)))
            self.sgst_input.setValue(self.item_data.get('sgst_percent', 0))
            self.cgst_input.setValue(self.item_data.get('cgst_percent', 0))
    
    def get_item_data(self):
        """Get item data from form"""
        return {
            'barcode': self.barcode_input.text().strip(),
            'name': self.name_input.text().strip(),
            'hsn_code': self.hsn_input.text().strip(),
            'quantity': self.quantity_input.value(),
            'base_price': self.base_price_input.value(),
            'sgst_percent': self.sgst_input.value(),
            'cgst_percent': self.cgst_input.value()
        }
    
    def accept(self):
        """Validate and accept"""
        data = self.get_item_data()
        
        if not data['barcode']:
            QMessageBox.warning(self, "Error", "Barcode is required!")
            return
        
        if not data['name']:
            QMessageBox.warning(self, "Error", "Item name is required!")
            return
        
        super().accept()

class LooseItemDialog(QDialog):
    def __init__(self, categories, item_data=None, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.item_data = item_data
        self.setWindowTitle("Add/Edit Loose Item")
        self.setModal(True)
        self.resize(500, 700)
        
        self.init_ui()
        
        if item_data:
            self.load_item_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create form layout
        form_layout = QGridLayout()
        
        # Category
        form_layout.addWidget(QLabel("Category:"), 0, 0)
        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont("Arial", 12))
        for category in self.categories:
            self.category_combo.addItem(category['name'], category['id'])
        form_layout.addWidget(self.category_combo, 0, 1)
        
        # Item Name
        form_layout.addWidget(QLabel("Item Name:"), 1, 0)
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 12))
        form_layout.addWidget(self.name_input, 1, 1)
        
        # HSN Code
        form_layout.addWidget(QLabel("HSN Code:"), 2, 0)
        self.hsn_input = QLineEdit()
        self.hsn_input.setFont(QFont("Arial", 12))
        form_layout.addWidget(self.hsn_input, 2, 1)
        
        # Quantity
        form_layout.addWidget(QLabel("Quantity:"), 3, 0)
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setValue(0)
        form_layout.addWidget(self.quantity_input, 3, 1)
        
        # Base Price per kg
        form_layout.addWidget(QLabel("Base Price per kg (₹):"), 4, 0)
        self.base_price_input = QDoubleSpinBox()
        self.base_price_input.setMinimum(0.01)
        self.base_price_input.setMaximum(99999.99)
        self.base_price_input.setDecimals(2)
        self.base_price_input.setValue(1.00)
        self.base_price_input.valueChanged.connect(self.calculate_total_price)
        form_layout.addWidget(self.base_price_input, 4, 1)
        
        # SGST %
        form_layout.addWidget(QLabel("SGST (%):"), 5, 0)
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setMinimum(0.0)
        self.sgst_input.setMaximum(50.0)
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(0.0)
        self.sgst_input.valueChanged.connect(self.calculate_total_price)
        form_layout.addWidget(self.sgst_input, 5, 1)
        
        # CGST %
        form_layout.addWidget(QLabel("CGST (%):"), 6, 0)
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setMinimum(0.0)
        self.cgst_input.setMaximum(50.0)
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(0.0)
        self.cgst_input.valueChanged.connect(self.calculate_total_price)
        form_layout.addWidget(self.cgst_input, 6, 1)
        
        # Total Price (calculated)
        form_layout.addWidget(QLabel("Total Price per kg (₹):"), 7, 0)
        self.total_price_label = QLabel("₹1.00")
        self.total_price_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_price_label.setStyleSheet("color: #e74c3c; padding: 5px; border: 1px solid #ccc;")
        form_layout.addWidget(self.total_price_label, 7, 1)
        
        # Image
        form_layout.addWidget(QLabel("Image (optional):"), 8, 0)
        image_layout = QHBoxLayout()
        self.image_path_input = QLineEdit()
        self.image_path_input.setFont(QFont("Arial", 12))
        self.image_path_input.setPlaceholderText("Select image file...")
        image_layout.addWidget(self.image_path_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_image)
        image_layout.addWidget(browse_btn)
        
        image_widget = QWidget()
        image_widget.setLayout(image_layout)
        form_layout.addWidget(image_widget, 8, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Initial calculation
        self.calculate_total_price()
    
    def calculate_total_price(self):
        """Calculate and display total price"""
        base_price = self.base_price_input.value()
        sgst_percent = self.sgst_input.value()
        cgst_percent = self.cgst_input.value()
        
        total_price = base_price + (base_price * sgst_percent / 100) + (base_price * cgst_percent / 100)
        self.total_price_label.setText(f"₹{total_price:.2f}")
    
    def browse_image(self):
        """Browse for image file and copy to images folder if not already there"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_path:
            import shutil
            import os
            import sys
            if getattr(sys, 'frozen', False):
                # Running as a PyInstaller bundle
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as a script
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            images_folder = os.path.join(base_dir, 'data_base', 'images')
            os.makedirs(images_folder, exist_ok=True)
            filename = os.path.basename(file_path)
            dest_path = os.path.join(images_folder, filename)
            # Only copy if not already in images_folder
            if os.path.abspath(file_path) == os.path.abspath(dest_path):
                self.image_path_input.setText(dest_path)
            else:
                try:
                    shutil.copy(file_path, dest_path)
                    self.image_path_input.setText(dest_path)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to copy image: {e}")
    
    def load_item_data(self):
        """Load existing item data"""
        if self.item_data:
            # Set category
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == self.item_data['category_id']:
                    self.category_combo.setCurrentIndex(i)
                    break
            
            self.name_input.setText(self.item_data['name'])
            self.hsn_input.setText(self.item_data.get('hsn_code', ''))
            self.quantity_input.setValue(self.item_data.get('quantity', 0))
            self.base_price_input.setValue(self.item_data.get('base_price', self.item_data.get('price_per_kg', 0)))
            self.sgst_input.setValue(self.item_data.get('sgst_percent', 0))
            self.cgst_input.setValue(self.item_data.get('cgst_percent', 0))
            
            if self.item_data.get('image_path'):
                self.image_path_input.setText(self.item_data['image_path'])
    
    def get_item_data(self):
        """Get item data from form"""
        return {
            'category_id': self.category_combo.currentData(),
            'name': self.name_input.text().strip(),
            'hsn_code': self.hsn_input.text().strip(),
            'quantity': self.quantity_input.value(),
            'base_price': self.base_price_input.value(),
            'sgst_percent': self.sgst_input.value(),
            'cgst_percent': self.cgst_input.value(),
            'image_path': self.image_path_input.text().strip() or None
        }
    
    def accept(self):
        """Validate and accept"""
        data = self.get_item_data()
        
        if not data['name']:
            QMessageBox.warning(self, "Error", "Item name is required!")
            return
        
        if not data['category_id']:
            QMessageBox.warning(self, "Error", "Please select a category!")
            return
        
        super().accept()

class CategoryDialog(QDialog):
    def __init__(self, category_name=None, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.setWindowTitle("Add Category" if not category_name else "Edit Category")
        self.setModal(True)
        self.resize(300, 150)
        
        self.init_ui()
        
        if category_name:
            self.name_input.setText(category_name)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Category Name
        layout.addWidget(QLabel("Category Name:"))
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.name_input)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_category_name(self):
        """Get category name from form"""
        return self.name_input.text().strip()
    
    def accept(self):
        """Validate and accept"""
        name = self.get_category_name()
        
        if not name:
            QMessageBox.warning(self, "Error", "Category name is required!")
            return
        
        super().accept()

class InventoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set size policy for responsive design
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.db = Database()
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_label = QLabel("Inventory Management")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(header_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Barcode Items Tab
        self.barcode_tab = QWidget()
        self.init_barcode_tab()
        self.tab_widget.addTab(self.barcode_tab, "Barcode Items")
        
        # Loose Items Tab
        self.loose_tab = QWidget()
        self.init_loose_tab()
        self.tab_widget.addTab(self.loose_tab, "Loose Items")
        
        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #dee2e6;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #dee2e6;
                font-size: 12px;
            }
        """)
    
    def init_barcode_tab(self):
        """Initialize barcode items tab"""
        layout = QVBoxLayout()
        self.barcode_tab.setLayout(layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_barcode_btn = QPushButton("Add Barcode Item")
        add_barcode_btn.setFont(QFont("Arial", 12))
        add_barcode_btn.clicked.connect(self.add_barcode_item)
        add_barcode_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        controls_layout.addWidget(add_barcode_btn)
        
        controls_layout.addStretch()
        
        refresh_barcode_btn = QPushButton("Refresh")
        refresh_barcode_btn.setFont(QFont("Arial", 12))
        refresh_barcode_btn.clicked.connect(self.load_barcode_items)
        refresh_barcode_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        controls_layout.addWidget(refresh_barcode_btn)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.barcode_table = QTableWidget()
        self.barcode_table.setColumnCount(10)
        self.barcode_table.setHorizontalHeaderLabels([
            "ID", "Barcode", "Name", "HSN Code", "Quantity", "Base Price", "SGST %", "CGST %", "Total Price", "Actions"
        ])
        
        # Table settings
        self.barcode_table.setAlternatingRowColors(True)
        self.barcode_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Set column widths
        header = self.barcode_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Barcode
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # HSN Code
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Base Price
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # SGST %
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # CGST %
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Total Price
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Actions
        
        layout.addWidget(self.barcode_table)
    
    def init_loose_tab(self):
        """Initialize loose items tab"""
        layout = QVBoxLayout()
        self.loose_tab.setLayout(layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_category_btn = QPushButton("Add Category")
        add_category_btn.setFont(QFont("Arial", 12))
        add_category_btn.clicked.connect(self.add_category)
        add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        controls_layout.addWidget(add_category_btn)

        delete_category_btn = QPushButton("Delete Category")
        delete_category_btn.setFont(QFont("Arial", 12))
        delete_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_category_btn.clicked.connect(self.delete_category)
        controls_layout.addWidget(delete_category_btn)
        
        add_loose_btn = QPushButton("Add Loose Item")
        add_loose_btn.setFont(QFont("Arial", 12))
        add_loose_btn.clicked.connect(self.add_loose_item)
        add_loose_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        controls_layout.addWidget(add_loose_btn)
        
        controls_layout.addStretch()
        
        refresh_loose_btn = QPushButton("Refresh")
        refresh_loose_btn.setFont(QFont("Arial", 12))
        refresh_loose_btn.clicked.connect(self.load_loose_items)
        refresh_loose_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        controls_layout.addWidget(refresh_loose_btn)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.loose_table = QTableWidget()
        self.loose_table.setColumnCount(11)
        self.loose_table.setHorizontalHeaderLabels([
            "ID", "Category", "Name", "HSN Code", "Quantity", "Base Price/kg", "SGST %", "CGST %", "Total Price/kg", "Image", "Actions"
        ])
        
        # Table settings
        self.loose_table.setAlternatingRowColors(True)
        self.loose_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Set column widths
        header = self.loose_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # HSN Code
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Base Price/kg
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # SGST %
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # CGST %
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Total Price/kg
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Image
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)  # Actions
        
        layout.addWidget(self.loose_table)
    
    def load_data(self):
        """Load all data"""
        self.load_barcode_items()
        self.load_loose_items()
    
    def load_barcode_items(self):
        """Load barcode items"""
        try:
            items = self.db.get_all_barcode_items()
            self.display_barcode_items(items)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load barcode items: {str(e)}")
    
    def display_barcode_items(self, items):
        """Display barcode items in table"""
        self.barcode_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # ID
            self.barcode_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            
            # Barcode
            self.barcode_table.setItem(row, 1, QTableWidgetItem(item['barcode']))
            
            # Name
            self.barcode_table.setItem(row, 2, QTableWidgetItem(item['name']))
            
            # HSN Code
            self.barcode_table.setItem(row, 3, QTableWidgetItem(item.get('hsn_code', '')))
            
            # Quantity
            self.barcode_table.setItem(row, 4, QTableWidgetItem(str(item.get('quantity', 0))))
            
            # Base Price
            base_price = item.get('base_price', item.get('price', 0))
            self.barcode_table.setItem(row, 5, QTableWidgetItem(f"₹{base_price:.2f}"))
            
            # SGST %
            self.barcode_table.setItem(row, 6, QTableWidgetItem(f"{item.get('sgst_percent', 0):.2f}%"))
            
            # CGST %
            self.barcode_table.setItem(row, 7, QTableWidgetItem(f"{item.get('cgst_percent', 0):.2f}%"))
            
            # Total Price
            total_price = item.get('total_price', base_price)
            self.barcode_table.setItem(row, 8, QTableWidgetItem(f"₹{total_price:.2f}"))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                    font-size: 10px;
                    min-width: 50px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            edit_btn.clicked.connect(lambda checked, item_data=item: self.edit_barcode_item(item_data))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                    font-size: 10px;
                    min-width: 50px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, item_id=item['id']: self.delete_barcode_item(item_id))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.barcode_table.setCellWidget(row, 9, actions_widget)
    
    def load_loose_items(self):
        """Load loose items"""
        try:
            categories = self.db.get_loose_categories()
            all_items = []
            
            for category in categories:
                items = self.db.get_loose_items_by_category(category['id'])
                for item in items:
                    item['category_name'] = category['name']
                    item['category_id'] = category['id']
                    all_items.append(item)
            
            self.display_loose_items(all_items)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load loose items: {str(e)}")
    
    def display_loose_items(self, items):
        """Display loose items in table"""
        self.loose_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # ID
            self.loose_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            
            # Category
            self.loose_table.setItem(row, 1, QTableWidgetItem(item['category_name']))
            
            # Name
            self.loose_table.setItem(row, 2, QTableWidgetItem(item['name']))
            
            # HSN Code
            self.loose_table.setItem(row, 3, QTableWidgetItem(item.get('hsn_code', '')))
            
            # Quantity
            self.loose_table.setItem(row, 4, QTableWidgetItem(str(item.get('quantity', 0))))
            
            # Base Price/kg
            base_price = item.get('base_price', item.get('price_per_kg', 0))
            self.loose_table.setItem(row, 5, QTableWidgetItem(f"₹{base_price:.2f}"))
            
            # SGST %
            self.loose_table.setItem(row, 6, QTableWidgetItem(f"{item.get('sgst_percent', 0):.2f}%"))
            
            # CGST %
            self.loose_table.setItem(row, 7, QTableWidgetItem(f"{item.get('cgst_percent', 0):.2f}%"))
            
            # Total Price/kg
            total_price = item.get('total_price', base_price)
            self.loose_table.setItem(row, 8, QTableWidgetItem(f"₹{total_price:.2f}"))
            
            # Image
            image_text = "Yes" if item.get('image_path') else "No"
            self.loose_table.setItem(row, 9, QTableWidgetItem(image_text))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                    font-size: 10px;
                    min-width: 50px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            edit_btn.clicked.connect(lambda checked, item_data=item: self.edit_loose_item(item_data))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                    font-size: 10px;
                    min-width: 50px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, item_id=item['id']: self.delete_loose_item(item_id))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.loose_table.setCellWidget(row, 10, actions_widget)
    
    def add_barcode_item(self):
        """Add new barcode item"""
        dialog = BarcodeItemDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_item_data()
            if self.db.add_barcode_item(data['barcode'], data['name'], data['hsn_code'], 
                                       data['quantity'], data['base_price'], data['sgst_percent'], data['cgst_percent']):
                QMessageBox.information(self, "Success", "Barcode item added successfully!")
                self.load_barcode_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to add barcode item. Barcode might already exist.")
    
    def edit_barcode_item(self, item_data):
        """Edit barcode item"""
        dialog = BarcodeItemDialog(item_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_item_data()
            if self.db.update_barcode_item(item_data['id'], data['barcode'], data['name'], data['hsn_code'],
                                          data['quantity'], data['base_price'], data['sgst_percent'], data['cgst_percent']):
                QMessageBox.information(self, "Success", "Barcode item updated successfully!")
                self.load_barcode_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to update barcode item.")
    
    def delete_barcode_item(self, item_id):
        """Delete barcode item"""
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this barcode item?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_barcode_item(item_id):
                QMessageBox.information(self, "Success", "Barcode item deleted successfully!")
                self.load_barcode_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete barcode item.")
    
    def add_category(self):
        """Add new category"""
        dialog = CategoryDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            category_name = dialog.get_category_name()
            if self.db.add_loose_category(category_name):
                QMessageBox.information(self, "Success", "Category added successfully!")
                self.load_loose_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to add category. Category might already exist.")
    
    def delete_category(self):
        categories = self.db.get_loose_categories()
        if not categories:
            QMessageBox.information(self, "Delete Category", "No categories to delete.")
            return
        from PyQt5.QtWidgets import QInputDialog
        items = [cat['name'] for cat in categories]
        cat_name, ok = QInputDialog.getItem(self, "Delete Category", "Select category to delete:", items, 0, False)
        if ok and cat_name:
            confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete category '{cat_name}'? This will also delete all loose items in this category.", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                # Find category id
                cat_id = next((cat['id'] for cat in categories if cat['name'] == cat_name), None)
                if cat_id is not None:
                    conn = self.db.get_connection()
                    try:
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM loose_items WHERE category_id = ?', (cat_id,))
                        cursor.execute('DELETE FROM loose_categories WHERE id = ?', (cat_id,))
                        conn.commit()
                        QMessageBox.information(self, "Success", f"Category '{cat_name}' and its items deleted.")
                        self.load_loose_items()
                        self.load_data()  # Ensure all UI is refreshed
                    finally:
                        conn.close()
                else:
                    QMessageBox.warning(self, "Error", "Category not found.")
    
    def add_loose_item(self):
        """Add new loose item"""
        categories = self.db.get_loose_categories()
        if not categories:
            QMessageBox.warning(self, "Error", "Please add at least one category first!")
            return
        
        dialog = LooseItemDialog(categories, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_item_data()
            if self.db.add_loose_item(data['category_id'], data['name'], data['hsn_code'], data['quantity'],
                                     data['base_price'], data['sgst_percent'], data['cgst_percent'], data['image_path']):
                QMessageBox.information(self, "Success", "Loose item added successfully!")
                self.load_loose_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to add loose item.")
    
    def edit_loose_item(self, item_data):
        """Edit loose item"""
        categories = self.db.get_loose_categories()
        dialog = LooseItemDialog(categories, item_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_item_data()
            if self.db.update_loose_item(item_data['id'], data['name'], data['hsn_code'], data['quantity'],
                                        data['base_price'], data['sgst_percent'], data['cgst_percent'], data['image_path']):
                QMessageBox.information(self, "Success", "Loose item updated successfully!")
                self.load_loose_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to update loose item.")
    
    def delete_loose_item(self, item_id):
        """Delete loose item"""
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this loose item?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_loose_item(item_id):
                QMessageBox.information(self, "Success", "Loose item deleted successfully!")
                self.load_loose_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete loose item.")

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
        self.barcode_table.setStyleSheet(f"font-size: {font_size}px;")
        self.loose_table.setStyleSheet(f"font-size: {font_size}px;")

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
    window = InventoryWindow()
    window.showMaximized()
    sys.exit(app.exec_())