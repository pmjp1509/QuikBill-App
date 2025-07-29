import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QTabWidget, QDialog, QGridLayout,
                             QDoubleSpinBox, QMessageBox, QFileDialog, QComboBox,
                             QHeaderView, QAbstractItemView, QDialogButtonBox,
                             QSpinBox, QSizePolicy, QApplication, QFormLayout)
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
        self.resize(400, 380)
        self.setStyleSheet("""
            QDialog { background: #f8f9fa; }
            QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { font-family: 'Poppins'; font-size: 14px; }
            QPushButton { padding: 8px 18px; border-radius: 6px; font-size: 14px; font-family: 'Poppins'; }
            QPushButton:hover { background: #3498db; color: white; }
        """)
        
        self.init_ui()
        
        if item_data:
            self.load_item_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        # Title
        title = QLabel("Add/Edit Barcode Item")
        title.setFont(QFont("Poppins", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        # Form layout
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(10)
        
        # Barcode
        self.barcode_input = QLineEdit()
        self.barcode_input.setFont(QFont("Poppins", 13))
        form_layout.addRow("Barcode:", self.barcode_input)
        
        # Item Name
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Poppins", 13))
        form_layout.addRow("Item Name:", self.name_input)
        
        # HSN Code
        self.hsn_input = QLineEdit()
        self.hsn_input.setFont(QFont("Poppins", 13))
        form_layout.addRow("HSN Code:", self.hsn_input)
        
        # Quantity
        self.quantity_input = QSpinBox()
        self.quantity_input.setFont(QFont("Poppins", 13))
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setValue(0)
        form_layout.addRow("Quantity:", self.quantity_input)
        
        # Base Price (auto-calculated, read-only, now QLabel)
        self.base_price_label = QLabel("0.00")
        self.base_price_label.setFont(QFont("Poppins", 13, QFont.Bold))
        form_layout.addRow("Base Price (₹):", self.base_price_label)
        
        # SGST %
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setFont(QFont("Poppins", 13))
        self.sgst_input.setMinimum(0.0)
        self.sgst_input.setMaximum(50.0)
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(0.0)
        self.sgst_input.valueChanged.connect(self.calculate_base_price)
        form_layout.addRow("SGST (%):", self.sgst_input)
        
        # CGST %
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setFont(QFont("Poppins", 13))
        self.cgst_input.setMinimum(0.0)
        self.cgst_input.setMaximum(50.0)
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(0.0)
        self.cgst_input.valueChanged.connect(self.calculate_base_price)
        form_layout.addRow("CGST (%):", self.cgst_input)
        
        layout.addLayout(form_layout)
        # Final Price (user input) at the bottom
        self.final_price_input = QDoubleSpinBox()
        self.final_price_input.setFont(QFont("Poppins", 13))
        self.final_price_input.setMinimum(0.01)
        self.final_price_input.setMaximum(99999.99)
        self.final_price_input.setDecimals(2)
        self.final_price_input.setValue(1.00)
        self.final_price_input.valueChanged.connect(self.calculate_base_price)
        layout.addSpacing(4)
        layout.addLayout(self._form_row("Final Price (₹):", self.final_price_input))
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setFont(QFont("Poppins", 13))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Initial calculation
        self.calculate_base_price()

    def _form_row(self, label, widget):
        row = QHBoxLayout()
        lab = QLabel(label)
        lab.setFont(QFont("Poppins", 13))
        row.addWidget(lab)
        row.addWidget(widget)
        return row
    
    def calculate_base_price(self):
        """Calculate and display total price"""
        final_price = self.final_price_input.value()
        sgst_percent = self.sgst_input.value()
        cgst_percent = self.cgst_input.value()
        
        divisor = 1 + (sgst_percent + cgst_percent) / 100
        base_price = final_price / divisor if divisor != 0 else 0
        self.base_price_label.setText(f"{base_price:.2f}")
    
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
        self.resize(400, 420)
        self.setStyleSheet("""
            QDialog { background: #f8f9fa; }
            QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { font-family: 'Poppins'; font-size: 14px; }
            QPushButton { padding: 8px 18px; border-radius: 6px; font-size: 14px; font-family: 'Poppins'; }
            QPushButton:hover { background: #3498db; color: white; }
        """)
        
        self.init_ui()
        
        if item_data:
            self.load_item_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        # Title
        title = QLabel("Add/Edit Loose Item")
        title.setFont(QFont("Poppins", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        # Form layout
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(10)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont("Poppins", 13))
        for category in self.categories:
            self.category_combo.addItem(category['name'], category['id'])
        form_layout.addRow("Category:", self.category_combo)
        
        # Item Name
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Poppins", 13))
        form_layout.addRow("Item Name:", self.name_input)
        
        # HSN Code
        self.hsn_input = QLineEdit()
        self.hsn_input.setFont(QFont("Poppins", 13))
        form_layout.addRow("HSN Code:", self.hsn_input)
        
        # Quantity
        self.quantity_input = QSpinBox()
        self.quantity_input.setFont(QFont("Poppins", 13))
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setValue(0)
        form_layout.addRow("Quantity:", self.quantity_input)
        
        # Base Price per kg (auto-calculated, read-only, now QLabel)
        self.base_price_label = QLabel("0.00")
        self.base_price_label.setFont(QFont("Poppins", 13, QFont.Bold))
        form_layout.addRow("Base Price per kg (₹):", self.base_price_label)
        
        # SGST %
        self.sgst_input = QDoubleSpinBox()
        self.sgst_input.setFont(QFont("Poppins", 13))
        self.sgst_input.setMinimum(0.0)
        self.sgst_input.setMaximum(50.0)
        self.sgst_input.setDecimals(2)
        self.sgst_input.setValue(0.0)
        self.sgst_input.valueChanged.connect(self.calculate_base_price)
        form_layout.addRow("SGST (%):", self.sgst_input)
        
        # CGST %
        self.cgst_input = QDoubleSpinBox()
        self.cgst_input.setFont(QFont("Poppins", 13))
        self.cgst_input.setMinimum(0.0)
        self.cgst_input.setMaximum(50.0)
        self.cgst_input.setDecimals(2)
        self.cgst_input.setValue(0.0)
        self.cgst_input.valueChanged.connect(self.calculate_base_price)
        form_layout.addRow("CGST (%):", self.cgst_input)
        
        # Image
        image_layout = QHBoxLayout()
        self.image_path_input = QLineEdit()
        self.image_path_input.setFont(QFont("Poppins", 13))
        self.image_path_input.setPlaceholderText("Select image file...")
        image_layout.addWidget(self.image_path_input)
        browse_btn = QPushButton("Browse")
        browse_btn.setFont(QFont("Poppins", 13))
        browse_btn.clicked.connect(self.browse_image)
        image_layout.addWidget(browse_btn)
        image_widget = QWidget()
        image_widget.setLayout(image_layout)
        form_layout.addRow("Image (optional):", image_widget)
        
        layout.addLayout(form_layout)
        # Final Price (user input) at the bottom
        self.final_price_input = QDoubleSpinBox()
        self.final_price_input.setFont(QFont("Poppins", 13))
        self.final_price_input.setMinimum(0.01)
        self.final_price_input.setMaximum(99999.99)
        self.final_price_input.setDecimals(2)
        self.final_price_input.setValue(1.00)
        self.final_price_input.valueChanged.connect(self.calculate_base_price)
        layout.addSpacing(4)
        layout.addLayout(self._form_row("Final Price per kg (₹):", self.final_price_input))
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setFont(QFont("Poppins", 13))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Initial calculation
        self.calculate_base_price()

    def _form_row(self, label, widget):
        row = QHBoxLayout()
        lab = QLabel(label)
        lab.setFont(QFont("Poppins", 13))
        row.addWidget(lab)
        row.addWidget(widget)
        return row
    
    def calculate_base_price(self):
        """Calculate and display total price"""
        final_price = self.final_price_input.value()
        sgst_percent = self.sgst_input.value()
        cgst_percent = self.cgst_input.value()
        
        divisor = 1 + (sgst_percent + cgst_percent) / 100
        base_price = final_price / divisor if divisor != 0 else 0
        self.base_price_label.setText(f"{base_price:.2f}")
    
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
        # Store original data for filtering
        self.all_barcode_items = []
        self.all_loose_items = []
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

        # Controls + Search Bar in one row
        controls_layout = QHBoxLayout()
        # Search bar (left, fills space)
        self.barcode_search_input = QLineEdit()
        self.barcode_search_input.setFont(QFont("Poppins", 12))
        self.barcode_search_input.setPlaceholderText("Search by barcode, name, or HSN code...")
        self.barcode_search_input.textChanged.connect(self.filter_barcode_items)
        self.barcode_search_input.setMinimumWidth(50)
        controls_layout.addWidget(self.barcode_search_input, 10)
        clear_search_btn = QPushButton("Clear")
        clear_search_btn.setFont(QFont("Poppins", 11))
        clear_search_btn.setFixedHeight(32)
        clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        clear_search_btn.clicked.connect(self.clear_barcode_search)
        controls_layout.addWidget(clear_search_btn, 0)
        controls_layout.addStretch(1)
        # Buttons (right)
        add_btn = QPushButton("Add Barcode Item")
        add_btn.setFont(QFont("Poppins", 11))
        add_btn.setFixedHeight(32)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_btn.clicked.connect(self.add_barcode_item)
        controls_layout.addWidget(add_btn, 0)
        upload_btn = QPushButton("Upload CSV")
        upload_btn.setFont(QFont("Poppins", 11))
        upload_btn.setFixedHeight(32)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        upload_btn.clicked.connect(self.upload_barcode_csv)
        controls_layout.addWidget(upload_btn, 0)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Poppins", 11))
        refresh_btn.setFixedHeight(32)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        refresh_btn.clicked.connect(self.load_barcode_items)
        controls_layout.addWidget(refresh_btn, 0)
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
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        self.barcode_table.setColumnWidth(9, 120)  # Actions column wider
        self.barcode_table.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.barcode_table)

    def init_loose_tab(self):
        layout = QVBoxLayout()
        self.loose_tab.setLayout(layout)

        # Controls + Search Bar in one row
        controls_layout = QHBoxLayout()
        # Search bar (left, fills space)
        self.loose_search_input = QLineEdit()
        self.loose_search_input.setFont(QFont("Poppins", 12))
        self.loose_search_input.setPlaceholderText("Search by name, HSN code, or category...")
        self.loose_search_input.textChanged.connect(self.filter_loose_items)
        self.loose_search_input.setMinimumWidth(50)
        controls_layout.addWidget(self.loose_search_input, 10)

        # Move Clear button immediately after search bar
        clear_search_btn = QPushButton("Clear")
        clear_search_btn.setFont(QFont("Poppins", 11))
        clear_search_btn.setFixedHeight(32)
        clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        clear_search_btn.clicked.connect(self.clear_loose_search)
        controls_layout.addWidget(clear_search_btn, 0)

        # Category filter beside clear button
        self.category_filter = QComboBox()
        self.category_filter.setFont(QFont("Poppins", 12))
        self.category_filter.setMinimumWidth(120)
        self.category_filter.currentIndexChanged.connect(self.filter_loose_items)
        controls_layout.addWidget(self.category_filter, 0)
        self.update_category_filter()

        # Buttons (right)
        add_cat_btn = QPushButton("Add Category")
        add_cat_btn.setFont(QFont("Poppins", 11))
        add_cat_btn.setFixedHeight(32)
        add_cat_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_cat_btn.clicked.connect(self.add_category)
        controls_layout.addWidget(add_cat_btn, 0)
        del_cat_btn = QPushButton("Delete Category")
        del_cat_btn.setFont(QFont("Poppins", 11))
        del_cat_btn.setFixedHeight(32)
        del_cat_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        del_cat_btn.clicked.connect(self.delete_category)
        controls_layout.addWidget(del_cat_btn, 0)
        add_loose_btn = QPushButton("Add Loose Item")
        add_loose_btn.setFont(QFont("Poppins", 11))
        add_loose_btn.setFixedHeight(32)
        add_loose_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_loose_btn.clicked.connect(self.add_loose_item)
        controls_layout.addWidget(add_loose_btn, 0)
        upload_btn = QPushButton("Upload CSV")
        upload_btn.setFont(QFont("Poppins", 11))
        upload_btn.setFixedHeight(32)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        upload_btn.clicked.connect(self.upload_loose_csv)
        controls_layout.addWidget(upload_btn, 0)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Poppins", 11))
        refresh_btn.setFixedHeight(32)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        refresh_btn.clicked.connect(self.load_loose_items)
        controls_layout.addWidget(refresh_btn, 0)
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
        header.setSectionResizeMode(10, QHeaderView.Fixed)
        self.loose_table.setColumnWidth(10, 120)  # Actions column wider
        self.loose_table.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.loose_table)

    # --- Barcode Items Logic ---
    def load_data(self):
        self.load_barcode_items()
        self.load_loose_items()

    def load_barcode_items(self):
        self.all_barcode_items = self.db.get_all_barcode_items()
        self.display_barcode_items(self.all_barcode_items)

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
        self.all_loose_items = all_items
        self.display_loose_items(self.all_loose_items)
        self.update_category_filter()

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
                    padding: 4px 12px;
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
                    padding: 4px 12px;
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
                self.update_category_filter()
            else:
                QMessageBox.warning(self, "Error", "Failed to add category. Category might already exist.")
    
    def delete_category(self):
        categories = self.db.get_loose_categories()
        if not categories:
            QMessageBox.information(self, "Delete Category", "No categories to delete.")
            return
        # Custom large dialog for category selection
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
        select_dialog = QDialog(self)
        select_dialog.setWindowTitle("Delete Category")
        select_dialog.resize(600, 320)
        select_dialog.setStyleSheet("""
            QDialog { background: #f8f9fa; }
            QLabel, QComboBox, QPushButton { font-family: 'Poppins'; }
            QLabel { font-size: 20px; font-weight: bold; }
            QComboBox { font-size: 18px; min-width: 260px; padding: 8px; }
            QPushButton { font-size: 16px; padding: 10px 28px; border-radius: 6px; }
            QPushButton:hover { background: #3498db; color: white; }
        """)
        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(30, 30, 30, 30)
        label = QLabel("Select category to delete:")
        vlayout.addWidget(label)
        combo = QComboBox()
        for cat in categories:
            combo.addItem(cat['name'])
        vlayout.addWidget(combo)
        hlayout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        hlayout.addWidget(ok_btn)
        hlayout.addWidget(cancel_btn)
        vlayout.addLayout(hlayout)
        select_dialog.setLayout(vlayout)
        ok_btn.clicked.connect(lambda: select_dialog.accept())
        cancel_btn.clicked.connect(lambda: select_dialog.reject())
        if select_dialog.exec_() == QDialog.Accepted:
            cat_name = combo.currentText()
            # Now show the big confirm dialog as before
            confirm_dialog = QDialog(self)
            confirm_dialog.setWindowTitle("Confirm Delete")
            confirm_dialog.resize(600, 320)
            confirm_dialog.setStyleSheet("QDialog, QLabel, QPushButton { font-family: 'Poppins'; font-size: 18px; }")
            vlayout2 = QVBoxLayout()
            vlayout2.setContentsMargins(30, 30, 30, 30)
            warning = QLabel(f"<span style='font-size:18px;font-weight:bold;color:#e74c3c;'>Are you sure you want to delete category '<b>{cat_name}</b>'?</span><br><br>This will also delete all loose items in this category.")
            warning.setWordWrap(True)
            vlayout2.addWidget(warning)
            hlayout2 = QHBoxLayout()
            yes_btn = QPushButton("Yes, Delete")
            yes_btn.setStyleSheet("background-color:#e74c3c;color:white;font-size:15px;padding:10px 24px;border-radius:6px;")
            no_btn = QPushButton("Cancel")
            no_btn.setStyleSheet("background-color:#bdc3c7;color:#2c3e50;font-size:15px;padding:10px 24px;border-radius:6px;")
            hlayout2.addWidget(yes_btn)
            hlayout2.addWidget(no_btn)
            vlayout2.addLayout(hlayout2)
            confirm_dialog.setLayout(vlayout2)
            yes_btn.clicked.connect(lambda: confirm_dialog.accept())
            no_btn.clicked.connect(lambda: confirm_dialog.reject())
            if confirm_dialog.exec_() == QDialog.Accepted:
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
                        self.update_category_filter()
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

    # --- Search Functionality ---
    def filter_barcode_items(self):
        """Filter barcode items based on search text"""
        search_text = self.barcode_search_input.text().lower().strip()
        if not search_text:
            self.display_barcode_items(self.all_barcode_items)
            return
        
        filtered_items = []
        for item in self.all_barcode_items:
            # Search in barcode, name, and HSN code
            if (search_text in item['barcode'].lower() or
                search_text in item['name'].lower() or
                search_text in item.get('hsn_code', '').lower()):
                filtered_items.append(item)
        
        self.display_barcode_items(filtered_items)
    
    def clear_barcode_search(self):
        """Clear barcode search and show all items"""
        self.barcode_search_input.clear()
        self.display_barcode_items(self.all_barcode_items)
    
    def update_category_filter(self):
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All", None)
        categories = self.db.get_loose_categories()
        for cat in categories:
            self.category_filter.addItem(cat['name'], cat['id'])
        self.category_filter.blockSignals(False)

    def filter_loose_items(self):
        """Filter loose items based on search text and category filter"""
        search_text = self.loose_search_input.text().lower().strip()
        selected_cat_id = self.category_filter.currentData()
        filtered_items = []
        for item in self.all_loose_items:
            matches_search = (
                not search_text or
                search_text in item['name'].lower() or
                search_text in item.get('hsn_code', '').lower() or
                search_text in item['category_name'].lower()
            )
            matches_category = (
                selected_cat_id is None or item['category_id'] == selected_cat_id
            )
            if matches_search and matches_category:
                filtered_items.append(item)
        self.display_loose_items(filtered_items)
    
    def clear_loose_search(self):
        """Clear loose items search and show all items (but keep category filter)"""
        self.loose_search_input.clear()
        self.filter_loose_items()

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

    def showEvent(self, event):
        screen = self.screen() if hasattr(self, 'screen') else QApplication.primaryScreen()
        if hasattr(screen, 'geometry'):
            screen_geom = screen.geometry()
            default_width, default_height = 1280, 720
            min_width, min_height = 800, 600
            # Ensure min size does not exceed screen size
            min_width = min(min_width, screen_geom.width())
            min_height = min(min_height, screen_geom.height())
            self.setMinimumSize(min_width, min_height)
            width = min(default_width, screen_geom.width())
            height = min(default_height, screen_geom.height())
            width = max(width, min_width)
            height = max(height, min_height)
            self.resize(width, height)
            frame_geom = self.frameGeometry()
            frame_geom.moveCenter(screen_geom.center())
            self.move(frame_geom.topLeft())
        super().showEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryWindow()
    window.showMaximized()
    sys.exit(app.exec_())