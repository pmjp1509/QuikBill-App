import sys
import csv
from datetime import datetime, date
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QFileDialog,
                             QHeaderView, QAbstractItemView, QComboBox,
                             QDateEdit, QGroupBox, QRadioButton, QSizePolicy,
                             QApplication)
from PyQt5.QtCore import Qt, QDate, QEvent
from PyQt5.QtGui import QFont
from data_base.database import Database
from billing_tabs.thermal_printer import ThermalPrinter

class BillHistoryWindow(QMainWindow):
    def __init__(self, printer_instance=None):
        super().__init__()
        self.setWindowTitle("Bill History")
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
        
        self.init_ui()
        self.load_bills()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_label = QLabel("Bill History")
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
        
        # Search and controls
        controls_layout = QVBoxLayout()
        
        # Search section
        search_group = QGroupBox("Search & Filter")
        search_layout = QVBoxLayout()
        
        # Customer name search
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Search Customer:"))
        self.search_input = QLineEdit()
        self.search_input.setFont(QFont("Arial", 12))
        self.search_input.setPlaceholderText("Enter customer name...")
        self.search_input.textChanged.connect(self.search_bills)
        customer_layout.addWidget(self.search_input)
        search_layout.addLayout(customer_layout)
        
        # Date range filter
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("to"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        
        filter_date_btn = QPushButton("Filter by Date")
        filter_date_btn.clicked.connect(self.filter_by_date)
        filter_date_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        date_layout.addWidget(filter_date_btn)
        search_layout.addLayout(date_layout)
        
        search_group.setLayout(search_layout)
        controls_layout.addWidget(search_group)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QHBoxLayout()
        
        export_all_btn = QPushButton("Export All Bills")
        export_all_btn.setFont(QFont("Arial", 12))
        export_all_btn.clicked.connect(self.export_all_to_csv)
        export_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_layout.addWidget(export_all_btn)
        
        export_filtered_btn = QPushButton("Export Filtered Bills")
        export_filtered_btn.setFont(QFont("Arial", 12))
        export_filtered_btn.clicked.connect(self.export_filtered_to_csv)
        export_filtered_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        export_layout.addWidget(export_filtered_btn)
        
        export_group.setLayout(export_layout)
        buttons_layout.addWidget(export_group)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Arial", 12))
        refresh_btn.clicked.connect(self.load_bills)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        buttons_layout.addWidget(refresh_btn)
        
        controls_layout.addLayout(buttons_layout)
        main_layout.addLayout(controls_layout)
        
        # Bills table
        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(9)
        self.bills_table.setHorizontalHeaderLabels([
            "Bill ID", "Customer Name", "Phone", "Date/Time", 
            "Total Amount", "SGST", "CGST", "Actions", "Reprint"
        ])
        
        # Table settings
        self.bills_table.setAlternatingRowColors(True)
        self.bills_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Set proper row height for buttons
        self.bills_table.verticalHeader().setDefaultSectionSize(40)
        self.bills_table.horizontalHeader().setStretchLastSection(True)
        
        # Set column widths
        header = self.bills_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Bill ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Customer Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Phone
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date/Time
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Total Amount
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # SGST
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # CGST
        header.setSectionResizeMode(7, QHeaderView.Stretch)  # Actions (was ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Reprint
        
        main_layout.addWidget(self.bills_table)
        
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
        
        # Store current bills for filtering
        self.current_bills = []
    
    def load_bills(self):
        """Load all bills from database"""
        try:
            bills = self.db.get_all_bills()
            self.current_bills = bills
            self.display_bills(bills)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bills: {str(e)}")
    
    def display_bills(self, bills):
        """Display bills in the table"""
        self.bills_table.setRowCount(len(bills))
        
        for row, bill in enumerate(bills):
            # Bill ID
            self.bills_table.setItem(row, 0, QTableWidgetItem(str(bill['id'])))
            
            # Customer Name
            self.bills_table.setItem(row, 1, QTableWidgetItem(bill['customer_name']))
            
            # Phone
            phone = bill['customer_phone'] if bill['customer_phone'] else "N/A"
            self.bills_table.setItem(row, 2, QTableWidgetItem(phone))
            
            # Date/Time
            try:
                date_time = datetime.strptime(bill['created_at'], '%Y-%m-%d %H:%M:%S')
                formatted_date = date_time.strftime('%d/%m/%Y %H:%M')
            except:
                formatted_date = bill['created_at']
            self.bills_table.setItem(row, 3, QTableWidgetItem(formatted_date))
            
            # Total Amount
            self.bills_table.setItem(row, 4, QTableWidgetItem(f"₹{bill['total_amount']:.2f}"))
            
            # SGST
            sgst = bill.get('total_sgst', 0)
            self.bills_table.setItem(row, 5, QTableWidgetItem(f"₹{sgst:.2f}"))
            
            # CGST
            cgst = bill.get('total_cgst', 0)
            self.bills_table.setItem(row, 6, QTableWidgetItem(f"₹{cgst:.2f}"))
            
            # Actions button (View Details)
            view_btn = QPushButton("View Details")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 0px 0px;
                    font-size: 11px;
                    min-width: 80px;
                    min-height: 30px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            view_btn.setMinimumHeight(30)
            view_btn.setMaximumHeight(30)
            view_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            view_btn.clicked.connect(lambda checked, bill_id=bill['id']: self.view_bill_details(bill_id))
            self.bills_table.setCellWidget(row, 7, view_btn)
            self.bills_table.setRowHeight(row, 40)
            
            # Reprint button
            reprint_btn = QPushButton("Reprint")
            reprint_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 0px 0px;
                    font-size: 11px;
                    min-width: 60px;
                    min-height: 30px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            reprint_btn.setMinimumHeight(30)
            reprint_btn.setMaximumHeight(30)
            reprint_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            reprint_btn.clicked.connect(lambda checked, bill_id=bill['id']: self.reprint_bill(bill_id))
            self.bills_table.setCellWidget(row, 8, reprint_btn)
    
    def search_bills(self):
        """Search bills by customer name"""
        search_text = self.search_input.text().strip()
        
        if search_text:
            try:
                bills = self.db.search_bills(search_text)
                self.current_bills = bills
                self.display_bills(bills)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
        else:
            self.load_bills()
    
    def filter_by_date(self):
        """Filter bills by date range"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        try:
            bills = self.db.get_bills_by_date_range(start_date, end_date)
            self.current_bills = bills
            self.display_bills(bills)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Date filter failed: {str(e)}")
    
    def view_bill_details(self, bill_id):
        """View detailed bill information"""
        try:
            bill = self.db.get_bill_by_id(bill_id)
            if not bill:
                QMessageBox.warning(self, "Error", "Bill not found!")
                return
            # Create detail message with GST breakdown
            details = ""
            details += f"Customer: {bill['customer_name']}\n"
            if bill.get('customer_phone'):
                details += f"Phone: {bill['customer_phone']}\n"
            details += f"Date: {bill['created_at']}\n"
            details += f"Total Items: {bill['total_items']}\n"
            if bill.get('total_weight', 0) > 0:
                details += f"Total Weight: {bill['total_weight']:.2f} kg\n"
            details += "\nItems:\n"
            details += f"{'Name':<10}{'Qty':>5}{'Base':>7}{'SGST':>6}{'CGST':>6}{'Total':>8}\n"
            details += "-" * 48 + "\n"
            sgst_percent_sum = 0
            cgst_percent_sum = 0
            sgst_count = 0
            cgst_count = 0
            for item in bill['items']:
                name = item['name'][:10] if len(item['name']) > 10 else item['name']
                qty = f"{item['quantity']:.2f}"
                if item['item_type'] == 'loose':
                    qty += "kg"
                base = f"{item['base_price']:.2f}"
                sgst_amt = item.get('sgst_amount', 0)
                cgst_amt = item.get('cgst_amount', 0)
                sgst = f"{sgst_amt:.2f}" if sgst_amt > 0 else "-"
                cgst = f"{cgst_amt:.2f}" if cgst_amt > 0 else "-"
                total = f"{item.get('final_price', 0):.2f}"
                details += f"{name:<10}{qty:>5}{base:>7}{sgst:>6}{cgst:>6}{total:>8}\n"
                if item.get('sgst_percent', 0) > 0:
                    sgst_percent_sum += item['sgst_percent']
                    sgst_count += 1
                if item.get('cgst_percent', 0) > 0:
                    cgst_percent_sum += item['cgst_percent']
                    cgst_count += 1
            details += "-" * 48 + "\n"
            # Summary at end
            avg_sgst = (sgst_percent_sum / sgst_count) if sgst_count else 0
            avg_cgst = (cgst_percent_sum / cgst_count) if cgst_count else 0
            details += f"Avg SGST%: {avg_sgst:.2f}%\n"
            details += f"Avg CGST%: {avg_cgst:.2f}%\n"
            details += f"Total Amount: ₹{bill['total_amount']:.2f}\n"
            QMessageBox.information(self, f"Bill Details", details)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bill details: {str(e)}")
    
    def reprint_bill(self, bill_id):
        """Reprint a bill"""
        try:
            bill = self.db.get_bill_by_id(bill_id)
            if not bill:
                QMessageBox.warning(self, "Error", "Bill not found!")
                return
            
            # Try to connect to printer and print
            if self.thermal_printer.connect_usb_printer():
                if self.thermal_printer.print_bill(bill):
                    QMessageBox.information(self, "Success", f"Bill #{bill_id} reprinted successfully!")
                else:
                    QMessageBox.warning(self, "Print Error", "Failed to print the bill!")
            else:
                QMessageBox.warning(self, "Printer Error", "Printer not connected!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reprint bill: {str(e)}")
    
    def export_all_to_csv(self):
        """Export all bills to CSV file"""
        try:
            bills = self.db.get_all_bills()
            self._export_bills_to_csv(bills, "all_bills")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export all bills: {str(e)}")
    
    def export_filtered_to_csv(self):
        """Export currently filtered bills to CSV file"""
        try:
            self._export_bills_to_csv(self.current_bills, "filtered_bills")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export filtered bills: {str(e)}")
    
    def _export_bills_to_csv(self, bills, filename_prefix):
        """Export bills to CSV file"""
        if not bills:
            QMessageBox.warning(self, "No Data", "No bills to export!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Bills to CSV", 
            f"{filename_prefix}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Bill ID', 'Customer Name', 'Mobile Number', 'Date', 'Time', 
                'Total Items', 'Items', 'Total Amount'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for bill in bills:
                # Get bill details
                detailed_bill = self.db.get_bill_by_id(bill['id'])
                
                # Format date and time separately
                try:
                    date_time = datetime.strptime(bill['created_at'], '%Y-%m-%d %H:%M')
                    date_str = date_time.strftime('%d/%m/%Y')
                    time_str = date_time.strftime('%H:%M')
                except:
                    date_str = bill['created_at']
                    time_str = "N/A"
                
                # Get all item names separated by comma
                item_names = ", ".join([item['name'] for item in detailed_bill['items']])
                
                writer.writerow({
                    'Bill ID': bill['id'],
                    'Customer Name': bill['customer_name'],
                    'Mobile Number': bill['customer_phone'] or 'N/A',
                    'Date': date_str,
                    'Time': time_str,
                    'Total Items': bill['total_items'],
                    'Items': item_names,
                    'Total Amount': bill['total_amount']
                })
        
        QMessageBox.information(self, "Success", f"Bills exported successfully to:\n{file_path}")

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
        self.bills_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                gridline-color: #dee2e6;
                font-size: {font_size}px;
            }}
            QTableWidget::item {{
                padding: 8px;
                font-size: {font_size}px;
            }}
            QHeaderView::section {{
                background-color: #e9ecef;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #dee2e6;
                font-size: {font_size}px;
            }}
        """)

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
    window = BillHistoryWindow()
    window.showMaximized()
    sys.exit(app.exec_())