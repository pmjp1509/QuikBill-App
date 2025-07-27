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
        self.resize(500, 450)  # Reduced from 600
        
        self.init_ui()
        
        if item_data:
            self.load_item_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Reduce spacing between elements
        layout.setContentsMargins(15, 15, 15, 15)  # Reduce margins
        
        # Create form layout
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(8)  # Reduce vertical spacing between rows
        form_layout.setHorizontalSpacing(15)  # Reduce horizontal spacing
        
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
        
        # Base Price (auto-calculated, read-only)
        form_layout.addWidget(QLabel("Base Price (₹):"), 4, 0)
        self.base_price_input = QDoubleSpinBox()
        self.base_price_input.setMinimum(0.01)
        self.base_price_input.setMaximum(99999.99)
        self.base_price_input.setDecimals(2)
        self.base_price_input.setReadOnly(True)
        form_layout.addWidget(self.base_price_input, 4, 1)
        
        # SGST %
        form_layout.addWidget(QLabel("SGST (%):"), 5, 0)
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setMinimum(0.0)
        self.sgst_input.setMaximum(50.0)
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(0.0)
        self.sgst_input.valueChanged.connect(self.calculate_base_price)
        form_layout.addWidget(self.sgst_input, 5, 1)
        
        # CGST %
        form_layout.addWidget(QLabel("CGST (%):"), 6, 0)
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setMinimum(0.0)
        self.cgst_input.setMaximum(50.0)
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(0.0)
        self.cgst_input.valueChanged.connect(self.calculate_base_price)
        form_layout.addWidget(self.cgst_input, 6, 1)
        
        layout.addLayout(form_layout)
        
        # Final Price (user input) at the bottom
        final_price_layout = QHBoxLayout()
        final_price_layout.setSpacing(10)  # Reduce spacing
        final_price_label = QLabel("Final Price (₹):")
        final_price_layout.addWidget(final_price_label)
        self.final_price_input = QDoubleSpinBox()
        self.final_price_input.setMinimum(0.01)
        self.final_price_input.setMaximum(99999.99)
        self.final_price_input.setDecimals(2)
        self.final_price_input.setValue(1.00)
        self.final_price_input.valueChanged.connect(self.calculate_base_price)
        final_price_layout.addWidget(self.final_price_input)
        layout.addLayout(final_price_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Initial calculation
        self.calculate_base_price()
    
    def calculate_base_price(self):
        """Calculate and display total price"""
        final_price = self.final_price_input.value()
        sgst_percent = self.sgst_input.value()
        cgst_percent = self.cgst_input.value()
        
        divisor = 1 + (sgst_percent + cgst_percent) / 100
        base_price = final_price / divisor if divisor != 0 else 0
        self.base_price_input.setValue(base_price)
    
    def load_item_data(self):
        """Load existing item data"""
        if self.item_data:
            self.barcode_input.setText(self.item_data['barcode'])
            self.name_input.setText(self.item_data['name'])
            self.hsn_input.setText(self.item_data.get('hsn_code', ''))
            self.quantity_input.setValue(self.item_data.get('quantity', 0))
            self.sgst_input.setValue(self.item_data.get('sgst_percent', 0))
            self.cgst_input.setValue(self.item_data.get('cgst_percent', 0))
            # Always use total_price for final price input
            if 'total_price' in self.item_data:
                self.final_price_input.setValue(self.item_data['total_price'])
            else:
                sgst = self.item_data.get('sgst_percent', 0)
                cgst = self.item_data.get('cgst_percent', 0)
                base = self.item_data.get('base_price', self.item_data.get('price', 0))
                self.final_price_input.setValue(base * (1 + (sgst + cgst) / 100))
            self.calculate_base_price()
    
    def get_item_data(self):
        """Get item data from form"""
        return {
            'barcode': self.barcode_input.text().strip(),
            'name': self.name_input.text().strip(),
            'hsn_code': self.hsn_input.text().strip(),
            'quantity': self.quantity_input.value(),
            'sgst_percent': self.sgst_input.value(),
            'cgst_percent': self.cgst_input.value(),
            'total_price': self.final_price_input.value()
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
        self.resize(500, 550)  # Reduced from 700
        
        self.init_ui()
        
        if item_data:
            self.load_item_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Reduce spacing between elements
        layout.setContentsMargins(15, 15, 15, 15)  # Reduce margins
        
        # Create form layout
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(8)  # Reduce vertical spacing between rows
        form_layout.setHorizontalSpacing(15)  # Reduce horizontal spacing
        
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
        
        # Base Price (auto-calculated, read-only)
        form_layout.addWidget(QLabel("Base Price per kg (₹):"), 4, 0)
        self.base_price_input = QDoubleSpinBox()
        self.base_price_input.setMinimum(0.01)
        self.base_price_input.setMaximum(99999.99)
        self.base_price_input.setDecimals(2)
        self.base_price_input.setReadOnly(True)
        form_layout.addWidget(self.base_price_input, 4, 1)
        
        # SGST %
        form_layout.addWidget(QLabel("SGST (%):"), 5, 0)
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setMinimum(0.0)
        self.sgst_input.setMaximum(50.0)
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(0.0)
        self.sgst_input.valueChanged.connect(self.calculate_base_price)
        form_layout.addWidget(self.sgst_input, 5, 1)
        
        # CGST %
        form_layout.addWidget(QLabel("CGST (%):"), 6, 0)
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setMinimum(0.0)
        self.cgst_input.setMaximum(50.0)
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(0.0)
        self.cgst_input.valueChanged.connect(self.calculate_base_price)
        form_layout.addWidget(self.cgst_input, 6, 1)
        
        # Image
        form_layout.addWidget(QLabel("Image (optional):"), 7, 0)
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
        form_layout.addWidget(image_widget, 7, 1)
        
        layout.addLayout(form_layout)
        
        # Final Price (user input) at the bottom
        final_price_layout = QHBoxLayout()
        final_price_layout.setSpacing(10)  # Reduce spacing
        final_price_label = QLabel("Final Price per kg (₹):")
        final_price_layout.addWidget(final_price_label)
        self.final_price_input = QDoubleSpinBox()
        self.final_price_input.setMinimum(0.01)
        self.final_price_input.setMaximum(99999.99)
        self.final_price_input.setDecimals(2)
        self.final_price_input.setValue(1.00)
        self.final_price_input.valueChanged.connect(self.calculate_base_price)
        final_price_layout.addWidget(self.final_price_input)
        layout.addLayout(final_price_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Initial calculation
        self.calculate_base_price()
    
    def calculate_base_price(self):
        """Calculate and display total price"""
        final_price = self.final_price_input.value()
        sgst_percent = self.sgst_input.value()
        cgst_percent = self.cgst_input.value()
        
        divisor = 1 + (sgst_percent + cgst_percent) / 100
        base_price = final_price / divisor if divisor != 0 else 0
        self.base_price_input.setValue(base_price)
    
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
                if self.category_combo.itemData(i) == self.item_data.get('category_id'):
                    self.category_combo.setCurrentIndex(i)
                    break
            
            self.name_input.setText(self.item_data['name'])
            self.hsn_input.setText(self.item_data.get('hsn_code', ''))
            self.quantity_input.setValue(self.item_data.get('quantity', 0))
            self.sgst_input.setValue(self.item_data.get('sgst_percent', 0))
            self.cgst_input.setValue(self.item_data.get('cgst_percent', 0))
            
            if 'total_price' in self.item_data:
                self.final_price_input.setValue(self.item_data['total_price'])
            else:
                sgst = self.item_data.get('sgst_percent', 0)
                cgst = self.item_data.get('cgst_percent', 0)
                base = self.item_data.get('base_price', self.item_data.get('price_per_kg', 0))
                self.final_price_input.setValue(base * (1 + (sgst + cgst) / 100))
            
            if self.item_data.get('image_path'):
                self.image_path_input.setText(self.item_data['image_path'])
            self.calculate_base_price()
    
    def get_item_data(self):
        """Get item data from form"""
        return {
            'category_id': self.category_combo.currentData(),
            'name': self.name_input.text().strip(),
            'hsn_code': self.hsn_input.text().strip(),
            'quantity': self.quantity_input.value(),
            'sgst_percent': self.sgst_input.value(),
            'cgst_percent': self.cgst_input.value(),
            'total_price': self.final_price_input.value(),
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
        self.setMinimumSize(900, 600)
        self.db = Database()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header
        header_label = QLabel("Inventory Management")
        header_label.setFont(QFont("Poppins", 22, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        # Tabs
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

        # Set global font to Poppins for the entire inventory window
        poppins_font = QFont("Poppins", 12)
        self.setFont(poppins_font)

        # Make all table headers bold
        self.setStyleSheet(self.styleSheet() + "\nQHeaderView::section { font-weight: bold; }")

    def init_barcode_tab(self):
        layout = QVBoxLayout()
        self.barcode_tab.setLayout(layout)

        # Controls
        controls_layout = QHBoxLayout()
        add_btn = QPushButton("Add Barcode Item")
        add_btn.setFont(QFont("Poppins", 12))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_btn.clicked.connect(self.add_barcode_item)
        controls_layout.addWidget(add_btn)
        upload_btn = QPushButton("Upload CSV")
        upload_btn.setFont(QFont("Poppins", 12))
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        upload_btn.clicked.connect(self.upload_barcode_csv)
        controls_layout.addWidget(upload_btn)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Poppins", 12))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        refresh_btn.clicked.connect(self.load_barcode_items)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Table
        self.barcode_table = QTableWidget()
        self.barcode_table.setColumnCount(10)
        self.barcode_table.setHorizontalHeaderLabels([
            "ID", "Barcode", "Name", "HSN Code", "Quantity", "Base Price", "SGST %", "CGST %", "Total Price", "Actions"
        ])
        self.barcode_table.setAlternatingRowColors(True)
        self.barcode_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.barcode_table.verticalHeader().setDefaultSectionSize(40)
        header = self.barcode_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        layout.addWidget(self.barcode_table)

    def init_loose_tab(self):
        layout = QVBoxLayout()
        self.loose_tab.setLayout(layout)

        # Controls
        controls_layout = QHBoxLayout()
        add_cat_btn = QPushButton("Add Category")
        add_cat_btn.setFont(QFont("Poppins", 12))
        add_cat_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_cat_btn.clicked.connect(self.add_category)
        controls_layout.addWidget(add_cat_btn)
        del_cat_btn = QPushButton("Delete Category")
        del_cat_btn.setFont(QFont("Poppins", 12))
        del_cat_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        del_cat_btn.clicked.connect(self.delete_category)
        controls_layout.addWidget(del_cat_btn)
        add_loose_btn = QPushButton("Add Loose Item")
        add_loose_btn.setFont(QFont("Poppins", 12))
        add_loose_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_loose_btn.clicked.connect(self.add_loose_item)
        controls_layout.addWidget(add_loose_btn)
        upload_btn = QPushButton("Upload CSV")
        upload_btn.setFont(QFont("Poppins", 12))
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        upload_btn.clicked.connect(self.upload_loose_csv)
        controls_layout.addWidget(upload_btn)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Poppins", 12))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        refresh_btn.clicked.connect(self.load_loose_items)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Table
        self.loose_table = QTableWidget()
        self.loose_table.setColumnCount(11)
        self.loose_table.setHorizontalHeaderLabels([
            "ID", "Category", "Name", "HSN Code", "Quantity", "Base Price/kg", "SGST %", "CGST %", "Total Price/kg", "Image", "Actions"
        ])
        self.loose_table.setAlternatingRowColors(True)
        self.loose_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.loose_table.verticalHeader().setDefaultSectionSize(40)
        header = self.loose_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)
        layout.addWidget(self.loose_table)

    # --- Barcode Items Logic ---
    def load_data(self):
        self.load_barcode_items()
        self.load_loose_items()

    def load_barcode_items(self):
        items = self.db.get_all_barcode_items()
        self.display_barcode_items(items)

    def display_barcode_items(self, items):
        self.barcode_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.barcode_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.barcode_table.setItem(row, 1, QTableWidgetItem(item['barcode']))
            self.barcode_table.setItem(row, 2, QTableWidgetItem(item['name']))
            self.barcode_table.setItem(row, 3, QTableWidgetItem(item.get('hsn_code', '')))
            self.barcode_table.setItem(row, 4, QTableWidgetItem(str(item.get('quantity', 0))))
            base_price = item.get('base_price', item.get('price', 0))
            self.barcode_table.setItem(row, 5, QTableWidgetItem(f"₹{base_price:.2f}"))
            self.barcode_table.setItem(row, 6, QTableWidgetItem(f"{item.get('sgst_percent', 0):.2f}%"))
            self.barcode_table.setItem(row, 7, QTableWidgetItem(f"{item.get('cgst_percent', 0):.2f}%"))
            total_price = item.get('total_price', base_price)
            self.barcode_table.setItem(row, 8, QTableWidgetItem(f"₹{total_price:.2f}"))
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(8)
            edit_btn = QPushButton("Edit")
            edit_btn.setMinimumHeight(32)
            edit_btn.setMaximumHeight(32)
            edit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            edit_btn.clicked.connect(lambda checked, item_data=item: self.edit_barcode_item(item_data))
            actions_layout.addWidget(edit_btn)
            delete_btn = QPushButton("Delete")
            delete_btn.setMinimumHeight(32)
            delete_btn.setMaximumHeight(32)
            delete_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, item_id=item['id']: self.delete_barcode_item(item_id))
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)
            self.barcode_table.setCellWidget(row, 9, actions_widget)
            self.barcode_table.setRowHeight(row, 40)

    def add_barcode_item(self):
        dialog = BarcodeItemDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_item_data()
            if self.db.add_barcode_item(data['barcode'], data['name'], data['hsn_code'], 
                                       data['quantity'], data['total_price'], data['sgst_percent'], data['cgst_percent']):
                QMessageBox.information(self, "Success", "Barcode item added successfully!")
                self.load_barcode_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to add barcode item. Barcode might already exist.")
    
    def edit_barcode_item(self, item_data):
        dialog = BarcodeItemDialog(item_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_item_data()
            if self.db.update_barcode_item(item_data['id'], data['barcode'], data['name'], data['hsn_code'],
                                          data['quantity'], data['total_price'], data['sgst_percent'], data['cgst_percent']):
                QMessageBox.information(self, "Success", "Barcode item updated successfully!")
                self.load_barcode_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to update barcode item.")
    
    def delete_barcode_item(self, item_id):
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
    
    def upload_barcode_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", 
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            try:
                success, fail, fail_rows = self.db.import_barcode_items_from_csv(file_path)
                msg = f"Successfully added: {success}\nSkipped: {fail}"
                if fail_rows:
                    msg += "\n\nRows skipped due to errors:\n"
                    msg += "\n".join([f"Row {row}: {reason}" for row, reason in fail_rows])
                QMessageBox.information(self, "CSV Import Result", msg)
                self.load_barcode_items()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import barcode items from CSV: {e}")

    # --- Loose Items Logic ---
    def load_loose_items(self):
        categories = self.db.get_loose_categories()
        all_items = []
        for category in categories:
            items = self.db.get_loose_items_by_category(category['id'])
            for item in items:
                item['category_name'] = category['name']
                item['category_id'] = category['id']
                all_items.append(item)
        self.display_loose_items(all_items)

    def display_loose_items(self, items):
        self.loose_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.loose_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.loose_table.setItem(row, 1, QTableWidgetItem(item['category_name']))
            self.loose_table.setItem(row, 2, QTableWidgetItem(item['name']))
            self.loose_table.setItem(row, 3, QTableWidgetItem(item.get('hsn_code', '')))
            self.loose_table.setItem(row, 4, QTableWidgetItem(str(item.get('quantity', 0))))
            base_price = item.get('base_price', item.get('price_per_kg', 0))
            self.loose_table.setItem(row, 5, QTableWidgetItem(f"₹{base_price:.2f}"))
            self.loose_table.setItem(row, 6, QTableWidgetItem(f"{item.get('sgst_percent', 0):.2f}%"))
            self.loose_table.setItem(row, 7, QTableWidgetItem(f"{item.get('cgst_percent', 0):.2f}%"))
            total_price = item.get('total_price', base_price)
            self.loose_table.setItem(row, 8, QTableWidgetItem(f"₹{total_price:.2f}"))
            # Image
            image_text = "Yes" if item.get('image_path') else "No"
            self.loose_table.setItem(row, 9, QTableWidgetItem(image_text))
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(8)

            edit_btn = QPushButton("Edit")
            edit_btn.setMinimumHeight(32)
            edit_btn.setMaximumHeight(32)
            edit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            edit_btn.clicked.connect(lambda checked, item_data=item: self.edit_loose_item(item_data))
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setMinimumHeight(32)
            delete_btn.setMaximumHeight(32)
            delete_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, item_id=item['id']: self.delete_loose_item(item_id))
            actions_layout.addWidget(delete_btn)

            actions_widget.setLayout(actions_layout)
            self.loose_table.setCellWidget(row, 10, actions_widget)
            self.loose_table.setRowHeight(row, 40)

    def add_category(self):
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
        categories = self.db.get_loose_categories()
        if not categories:
            QMessageBox.warning(self, "Error", "Please add at least one category first!")
            return
        
        dialog = LooseItemDialog(categories, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_item_data()
            if self.db.add_loose_item(data['category_id'], data['name'], data['hsn_code'], data['quantity'],
                                     data['total_price'], data['sgst_percent'], data['cgst_percent'], data['image_path']):
                QMessageBox.information(self, "Success", "Loose item added successfully!")
                self.load_loose_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to add loose item.")
    
    def edit_loose_item(self, item_data):
        categories = self.db.get_loose_categories()
        dialog = LooseItemDialog(categories, item_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_item_data()
            if self.db.update_loose_item(item_data['id'], data['name'], data['hsn_code'], data['quantity'],
                                        data['total_price'], data['sgst_percent'], data['cgst_percent'], data['image_path']):
                QMessageBox.information(self, "Success", "Loose item updated successfully!")
                self.load_loose_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to update loose item.")
    
    def delete_loose_item(self, item_id):
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

    def upload_loose_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", 
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            try:
                success, fail, fail_rows = self.db.import_loose_items_from_csv(file_path)
                msg = f"Successfully added: {success}\nSkipped: {fail}"
                if fail_rows:
                    msg += "\n\nRows skipped due to errors:\n"
                    msg += "\n".join([f"Row {row}: {reason}" for row, reason in fail_rows])
                QMessageBox.information(self, "CSV Import Result", msg)
                self.load_loose_items()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import loose items from CSV: {e}")

    def apply_loose_category_filter(self):
        selected = self.category_filter.currentText()
        if selected == "All":
            self.load_loose_items()
        else:
            # Filter by category
            cat_id = None
            for cat in self.db.get_loose_categories():
                if cat['name'] == selected:
                    cat_id = cat['id']
                    break
            if cat_id is not None:
                items = self.db.get_loose_items_by_category(cat_id)
                # Ensure 'category_name' is present in each item
                for item in items:
                    item['category_name'] = selected
                self.display_loose_items(items)

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
    app = QApplication(sys.argv)
    window = InventoryWindow()
    window.showMaximized()
    sys.exit(app.exec_())