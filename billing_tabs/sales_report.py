import sys
import csv
from datetime import datetime, date, timedelta
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QDateEdit, QGroupBox,
                             QGridLayout, QMessageBox, QFileDialog, QScrollArea,
                             QFrame, QSizePolicy, QApplication, QProgressBar)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPainter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from data_base.database import Database
import numpy as np

class ReportGeneratorThread(QThread):
    """Thread for generating reports to avoid blocking UI"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, report_data, file_path, format_type):
        super().__init__()
        self.report_data = report_data
        self.file_path = file_path
        self.format_type = format_type
    
    def run(self):
        try:
            if self.format_type == 'csv':
                self._export_csv()
            elif self.format_type == 'pdf':
                self._export_pdf()
            self.finished.emit(True, f"Report exported successfully to {self.file_path}")
        except Exception as e:
            self.finished.emit(False, f"Failed to export report: {str(e)}")
    
    def _export_csv(self):
        """Export sales report data to CSV"""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write summary data
            writer.writerow(['Sales Report Summary'])
            writer.writerow(['Date Range', f"{self.report_data['start_date']} to {self.report_data['end_date']}"])
            writer.writerow(['Total Revenue', f"₹{self.report_data['total_revenue']:.2f}"])
            writer.writerow(['Total Bills', self.report_data['total_bills']])
            writer.writerow(['Total Items Sold', self.report_data['total_items']])
            writer.writerow(['Average Bill Value', f"₹{self.report_data['avg_bill_value']:.2f}"])
            writer.writerow([])
            
            # Write top selling items
            writer.writerow(['Top Selling Items'])
            writer.writerow(['Item Name', 'Quantity Sold', 'Revenue'])
            for item in self.report_data['top_items']:
                writer.writerow([item['name'], item['quantity'], f"₹{item['revenue']:.2f}"])
            writer.writerow([])
            
            # Write category-wise sales
            writer.writerow(['Category-wise Sales'])
            writer.writerow(['Category', 'Revenue', 'Percentage'])
            for category in self.report_data['category_sales']:
                writer.writerow([category['name'], f"₹{category['revenue']:.2f}", f"{category['percentage']:.1f}%"])
    
    def _export_pdf(self):
        """Export sales report data to PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(self.file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("Sales Report", title_style))
            story.append(Spacer(1, 20))
            
            # Summary section
            summary_data = [
                ['Date Range', f"{self.report_data['start_date']} to {self.report_data['end_date']}"],
                ['Total Revenue', f"₹{self.report_data['total_revenue']:.2f}"],
                ['Total Bills', str(self.report_data['total_bills'])],
                ['Total Items Sold', str(self.report_data['total_items'])],
                ['Average Bill Value', f"₹{self.report_data['avg_bill_value']:.2f}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Top Loose Items Table
            if self.report_data.get('top_loose_items'):
                story.append(Paragraph("Top Loose Items (by Weight Sold)", styles['Heading2']))
                loose_items_data = [['Item Name', 'Weight Sold', 'Revenue']]
                for item in self.report_data['top_loose_items'][:10]:
                    loose_items_data.append([
                        item['name'], str(item['weight']), f"₹{item['revenue']:.2f}"
                    ])
                loose_items_table = Table(loose_items_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                loose_items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(loose_items_table)
                story.append(Spacer(1, 16))
            
            # Top Barcode Items Table
            if self.report_data.get('top_barcode_items'):
                story.append(Paragraph("Top Barcode Items (by Quantity Sold)", styles['Heading2']))
                barcode_items_data = [['Item Name', 'Quantity Sold', 'Revenue']]
                for item in self.report_data['top_barcode_items'][:10]:
                    barcode_items_data.append([
                        item['name'], str(item['quantity']), f"₹{item['revenue']:.2f}"
                    ])
                barcode_items_table = Table(barcode_items_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                barcode_items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(barcode_items_table)
                story.append(Spacer(1, 16))
            
            doc.build(story)
            
        except ImportError:
            # Fallback to simple text-based PDF if reportlab is not available
            with open(self.file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("SALES REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Date Range: {self.report_data['start_date']} to {self.report_data['end_date']}\n")
                f.write(f"Total Revenue: ₹{self.report_data['total_revenue']:.2f}\n")
                f.write(f"Total Bills: {self.report_data['total_bills']}\n")
                f.write(f"Total Items Sold: {self.report_data['total_items']}\n")
                f.write(f"Average Bill Value: ₹{self.report_data['avg_bill_value']:.2f}\n\n")
                
                f.write("TOP LOOSE ITEMS:\n")
                f.write("-" * 30 + "\n")
                for item in self.report_data.get('top_loose_items', [])[:10]:
                    f.write(f"{item['name']}: {item['weight']} weight, ₹{item['revenue']:.2f}\n")
                f.write("\nTOP BARCODE ITEMS:\n")
                f.write("-" * 30 + "\n")
                for item in self.report_data.get('top_barcode_items', [])[:10]:
                    f.write(f"{item['name']}: {item['quantity']} units, ₹{item['revenue']:.2f}\n")

class ChartWidget(QWidget):
    """Custom widget for displaying matplotlib charts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Set background color to match application theme
        self.figure.patch.set_facecolor('#f8f9fa')
    
    def clear_chart(self):
        """Clear the current chart"""
        self.figure.clear()
        self.canvas.draw()
    
    def create_pie_chart(self, data, title, colors=None):
        """Create a pie chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        labels = [item['name'] for item in data]
        sizes = [item['value'] for item in data]
        
        if colors is None:
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        self.figure.tight_layout(rect=[0.08, 0.08, 0.98, 0.92])
        self.canvas.draw()
    
    def create_bar_chart(self, data, title, xlabel, ylabel, fixed_num_bars=None, fixed_labels=None):
        """Create a bar chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        if fixed_num_bars and fixed_labels:
            # Fill missing bars with 0
            label_to_value = {item['name']: item['value'] for item in data}
            labels = fixed_labels
            values = [label_to_value.get(label, 0) for label in labels]
        else:
            labels = [item['name'][:15] + '...' if len(item['name']) > 15 else item['name'] 
                     for item in data]
            values = [item['value'] for item in data]
        
        bars = ax.bar(labels, values, color='#3498db', alpha=0.8)
        
        # Add value labels on bars
        ax.margins(y=0.15)
        ylim = ax.get_ylim()
        for bar, value in zip(bars, values):
            height = bar.get_height()
            # If the bar is too close to the top, put label inside the bar
            if height > 0.95 * ylim[1]:
                ax.text(bar.get_x() + bar.get_width()/2., height*0.95,
                        f'{int(value)}', ha='center', va='top', fontweight='bold', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(value)}', ha='center', va='bottom', fontweight='bold')
        
        # Center x-axis label and add extra padding
        try:
            ax.set_xlabel(xlabel, fontsize=12, labelpad=28, loc='center')
        except TypeError:
            ax.set_xlabel(xlabel, fontsize=12, labelpad=28)
        ax.set_ylabel(ylabel, fontsize=12)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout(rect=[0.08, 0.28, 0.98, 0.92])
        self.figure.subplots_adjust(bottom=0.45)
        self.canvas.draw()
    
    def create_line_chart(self, data, title, xlabel, ylabel):
        """Create a line chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        # Check if data contains dates or hours
        first_item = data[0]
        if isinstance(first_item['date'], str) and '-' in first_item['date']:
            # Date-based data
            dates = [datetime.strptime(item['date'], '%Y-%m-%d').date() for item in data]
            values = [item['value'] for item in data]
            
            ax.plot(dates, values, marker='o', linewidth=2, markersize=6, color='#e74c3c')
            ax.fill_between(dates, values, alpha=0.3, color='#e74c3c')
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        else:
            # Hour-based data
            hours = [item['date'] for item in data]
            values = [item['value'] for item in data]
            
            ax.plot(hours, values, marker='o', linewidth=2, markersize=6, color='#3498db')
            ax.fill_between(hours, values, alpha=0.3, color='#3498db')
            
            # Format x-axis for hours
            ax.set_xticks(hours)
            ax.set_xticklabels([f'{h:02d}:00' for h in hours])
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout(rect=[0.08, 0.18, 0.98, 0.92])
        self.canvas.draw()

class SalesReportWindow(QMainWindow):
    """Sales Report Window with comprehensive analytics"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sales Report")
        self.setMinimumSize(1200, 800)
        self.db = Database()
        
        # Initialize date range
        self.start_date = date.today() - timedelta(days=30)  # Default: Last 30 days
        self.end_date = date.today()
        
        self.init_ui()
        self.load_report_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create scroll area for the entire content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.addWidget(scroll_area)
        
        content_layout = QVBoxLayout()
        scroll_content.setLayout(content_layout)
        
        # Header
        header_label = QLabel("Sales Report & Analytics")
        header_label.setFont(QFont("Poppins", 24, QFont.Bold))
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
        content_layout.addWidget(header_label)
        
        # Date Range Controls
        self.create_date_controls(content_layout)
        
        # Export Controls (moved up)
        self.create_export_controls(content_layout)
        
        # Summary Cards
        self.create_summary_cards(content_layout)
        
        # Charts Section
        self.create_charts_section(content_layout)
        
        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def create_date_controls(self, layout):
        """Create date range selection controls"""
        date_group = QGroupBox("Date Range Selection")
        date_group.setFont(QFont("Poppins", 14, QFont.Bold))
        date_layout = QHBoxLayout()
        
        label_font = QFont("Poppins", 12)
        widget_font = QFont("Poppins", 12)
        
        # Quick date range buttons
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(lambda: self.set_date_range('today'))
        today_btn.setStyleSheet(self.get_button_style('#3498db'))
        today_btn.setFont(widget_font)
        
        week_btn = QPushButton("This Week")
        week_btn.clicked.connect(lambda: self.set_date_range('week'))
        week_btn.setStyleSheet(self.get_button_style('#2ecc71'))
        week_btn.setFont(widget_font)
        
        month_btn = QPushButton("This Month")
        month_btn.clicked.connect(lambda: self.set_date_range('month'))
        month_btn.setStyleSheet(self.get_button_style('#9b59b6'))
        month_btn.setFont(widget_font)
        
        # Custom date range
        from_label = QLabel("From:")
        from_label.setFont(label_font)
        date_layout.addWidget(from_label)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setFont(widget_font)
        self.start_date_edit.setDate(QDate.fromString(self.start_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setFixedHeight(28)
        self.start_date_edit.setFixedWidth(150)
        self.start_date_edit.setStyleSheet("QDateEdit { font-family: 'Poppins'; font-size: 12pt; }")
        self.start_date_edit.setMaximumDate(QDate.currentDate())
        date_layout.addWidget(self.start_date_edit)
        
        to_label = QLabel("To:")
        to_label.setFont(label_font)
        date_layout.addWidget(to_label)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setFont(widget_font)
        self.end_date_edit.setDate(QDate.fromString(self.end_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setFixedHeight(28)
        self.end_date_edit.setFixedWidth(150)
        self.end_date_edit.setStyleSheet("QDateEdit { font-family: 'Poppins'; font-size: 12pt; }")
        self.end_date_edit.setMaximumDate(QDate.currentDate())
        date_layout.addWidget(self.end_date_edit)
        
        # Quick select
        quick_label = QLabel("Quick Select:")
        quick_label.setFont(label_font)
        date_layout.insertWidget(0, quick_label)
        date_layout.insertWidget(1, today_btn)
        date_layout.insertWidget(2, week_btn)
        date_layout.insertWidget(3, month_btn)
        date_layout.insertStretch(4)
        
        # Update button
        update_btn = QPushButton("Update Report")
        update_btn.clicked.connect(self.update_date_range)
        update_btn.setStyleSheet(self.get_button_style('#e74c3c'))
        update_btn.setFont(widget_font)
        date_layout.addWidget(update_btn)
        
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
    
    def create_summary_cards(self, layout):
        """Create summary statistics cards"""
        summary_group = QGroupBox("Sales Summary")
        summary_group.setFont(QFont("Poppins", 14, QFont.Bold))
        summary_layout = QGridLayout()
        
        # Create summary labels
        self.total_revenue_label = QLabel("₹0.00")
        self.total_bills_label = QLabel("0")
        self.total_items_label = QLabel("0")
        self.avg_bill_label = QLabel("₹0.00")
        
        # Style summary labels
        summary_style = """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
        """
        
        self.total_revenue_label.setStyleSheet(summary_style)
        self.total_bills_label.setStyleSheet(summary_style)
        self.total_items_label.setStyleSheet(summary_style)
        self.avg_bill_label.setStyleSheet(summary_style)
        
        # Add labels with titles
        summary_layout.addWidget(QLabel("Total Revenue"), 0, 0)
        summary_layout.addWidget(self.total_revenue_label, 1, 0)
        
        summary_layout.addWidget(QLabel("Total Bills"), 0, 1)
        summary_layout.addWidget(self.total_bills_label, 1, 1)
        
        summary_layout.addWidget(QLabel("Items Sold"), 0, 2)
        summary_layout.addWidget(self.total_items_label, 1, 2)
        
        summary_layout.addWidget(QLabel("Avg Bill Value"), 0, 3)
        summary_layout.addWidget(self.avg_bill_label, 1, 3)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
    
    def create_charts_section(self, layout):
        """Create charts section with each chart in its own group box and clear titles"""
        charts_layout = QVBoxLayout()
        charts_layout.setSpacing(24)

        # Top Selling Items (Separate for Loose and Barcode)
        top_items_group = QGroupBox("Top Selling Items")
        top_items_group.setFont(QFont("Poppins", 13, QFont.Bold))
        top_items_layout = QVBoxLayout()
        # Add two separate charts
        self.top_loose_items_chart = ChartWidget()
        self.top_loose_items_chart.setMinimumSize(500, 320)
        self.top_barcode_items_chart = ChartWidget()
        self.top_barcode_items_chart.setMinimumSize(500, 320)
        top_items_layout.addWidget(QLabel("Loose Items (by Weight Sold)"))
        top_items_layout.addWidget(self.top_loose_items_chart)
        top_items_layout.addWidget(QLabel("Barcode Items (by Quantity Sold)"))
        top_items_layout.addWidget(self.top_barcode_items_chart)
        top_items_group.setLayout(top_items_layout)
        charts_layout.addWidget(top_items_group)

        # Category-wise Sales
        category_group = QGroupBox("Category-wise Sales")
        category_group.setFont(QFont("Poppins", 13, QFont.Bold))
        category_layout = QVBoxLayout()
        self.category_chart = ChartWidget()
        self.category_chart.setMinimumSize(500, 320)
        category_layout.addWidget(self.category_chart)
        category_group.setLayout(category_layout)
        charts_layout.addWidget(category_group)

        # Top Categories Pie Chart
        top_categories_group = QGroupBox("Top Categories by Revenue")
        top_categories_group.setFont(QFont("Poppins", 13, QFont.Bold))
        top_categories_layout = QVBoxLayout()
        self.top_categories_chart = ChartWidget()
        self.top_categories_chart.setMinimumSize(500, 320)
        top_categories_layout.addWidget(self.top_categories_chart)
        top_categories_group.setLayout(top_categories_layout)
        charts_layout.addWidget(top_categories_group)

        # Monthly Sales Comparison
        monthly_group = QGroupBox("Monthly Sales Comparison")
        monthly_group.setFont(QFont("Poppins", 13, QFont.Bold))
        monthly_layout = QVBoxLayout()
        self.monthly_comparison_chart = ChartWidget()
        self.monthly_comparison_chart.setMinimumSize(500, 320)
        monthly_layout.addWidget(self.monthly_comparison_chart)
        monthly_group.setLayout(monthly_layout)
        charts_layout.addWidget(monthly_group)

        # Daily Sales Trend (full width)
        daily_trend_group = QGroupBox("Daily Sales Trend")
        daily_trend_group.setFont(QFont("Poppins", 13, QFont.Bold))
        daily_trend_layout = QVBoxLayout()
        self.daily_trend_chart = ChartWidget()
        self.daily_trend_chart.setMinimumSize(900, 320)
        daily_trend_layout.addWidget(self.daily_trend_chart)
        daily_trend_group.setLayout(daily_trend_layout)
        charts_layout.addWidget(daily_trend_group)

        layout.addLayout(charts_layout)
    
    def create_export_controls(self, layout):
        """Create export controls"""
        export_group = QGroupBox("Export Options")
        export_group.setFont(QFont("Poppins", 14, QFont.Bold))
        export_layout = QHBoxLayout()
        
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
        
        export_pdf_btn = QPushButton("Export as PDF")
        export_pdf_btn.clicked.connect(lambda: self.export_report('pdf'))
        export_pdf_btn.setStyleSheet(self.get_button_style('#f39c12'))
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.load_report_data)
        refresh_btn.setStyleSheet(self.get_button_style('#17a2b8'))
        
        export_layout.addWidget(export_pdf_btn)
        export_layout.addStretch()
        export_layout.addWidget(self.progress_bar)
        export_layout.addStretch()
        export_layout.addWidget(refresh_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
    
    def get_button_style(self, color):
        """Get consistent button styling"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """
    
    def set_date_range(self, range_type):
        """Set predefined date ranges"""
        today = date.today()
        
        if range_type == 'today':
            self.start_date = today
            self.end_date = today
        elif range_type == 'week':
            self.start_date = today - timedelta(days=today.weekday())
            self.end_date = today
        elif range_type == 'month':
            self.start_date = today.replace(day=1)
            self.end_date = today
        
        # Update date edit widgets
        self.start_date_edit.setDate(QDate.fromString(self.start_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.end_date_edit.setDate(QDate.fromString(self.end_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        
        # Reload data
        self.load_report_data()
    
    def update_date_range(self):
        """Update date range from custom inputs"""
        self.start_date = self.start_date_edit.date().toPyDate()
        self.end_date = self.end_date_edit.date().toPyDate()
        
        if self.start_date > self.end_date:
            QMessageBox.warning(self, "Invalid Date Range", "Start date cannot be after end date!")
            return
        
        self.load_report_data()
    
    def load_report_data(self):
        """Load and display sales report data"""
        try:
            # Get bills data for the selected date range
            start_date_str = self.start_date.strftime('%Y-%m-%d')
            end_date_str = self.end_date.strftime('%Y-%m-%d')
            
            bills = self.db.get_bills_by_date_range(start_date_str, end_date_str)
            
            if not bills:
                self.show_no_data_message()
                return
            
            # Calculate summary statistics
            total_revenue = sum(bill['total_amount'] for bill in bills)
            total_bills = len(bills)
            total_items = sum(bill['total_items'] for bill in bills)
            avg_bill_value = total_revenue / total_bills if total_bills > 0 else 0
            
            # Update summary labels
            self.total_revenue_label.setText(f"₹{total_revenue:.2f}")
            self.total_bills_label.setText(str(total_bills))
            self.total_items_label.setText(str(total_items))
            self.avg_bill_label.setText(f"₹{avg_bill_value:.2f}")
            
            # Generate charts data
            self.generate_top_items_charts_separate()
            self.generate_category_chart()
            self.generate_daily_trend_chart(bills)
            self.generate_top_categories_chart()
            self.generate_monthly_comparison_chart(bills)
            
            # Store data for export
            self.current_report_data = {
                'start_date': start_date_str,
                'end_date': end_date_str,
                'total_revenue': total_revenue,
                'total_bills': total_bills,
                'total_items': total_items,
                'avg_bill_value': avg_bill_value,
                'top_loose_items': self.get_top_loose_items_data(),
                'top_barcode_items': self.get_top_barcode_items_data(),
                'category_sales': self.get_category_sales_data()
            }
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load report data: {str(e)}")

    def show_no_data_message(self):
        """Show message when no data is available"""
        # Clear all charts and show no data message
        self.total_revenue_label.setText("₹0.00")
        self.total_bills_label.setText("0")
        self.total_items_label.setText("0")
        self.avg_bill_label.setText("₹0.00")
        
        # Clear all charts
        self.top_loose_items_chart.clear_chart()
        self.top_barcode_items_chart.clear_chart()
        self.category_chart.clear_chart()
        self.daily_trend_chart.clear_chart()
        self.top_categories_chart.clear_chart()
        self.monthly_comparison_chart.clear_chart()
        
        QMessageBox.information(self, "No Data", "No sales data for this period.")

    def generate_top_items_charts_separate(self):
        """Generate separate bar charts for top loose and barcode items"""
        # Loose items (by weight sold)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bi.item_name, SUM(bi.quantity) as total_weight
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'loose'
            GROUP BY bi.item_name
            ORDER BY total_weight DESC
            LIMIT 10
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        loose_results = cursor.fetchall()
        loose_data = [{'name': row[0], 'value': row[1]} for row in loose_results]
        self.top_loose_items_chart.create_bar_chart(loose_data, "Top Loose Items", "Items", "Weight Sold (kg)")

        # Barcode items (by quantity sold)
        cursor.execute('''
            SELECT bi.item_name, SUM(bi.quantity) as total_quantity
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'barcode'
            GROUP BY bi.item_name
            ORDER BY total_quantity DESC
            LIMIT 10
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        barcode_results = cursor.fetchall()
        barcode_data = [{'name': row[0], 'value': row[1]} for row in barcode_results]
        self.top_barcode_items_chart.create_bar_chart(barcode_data, "Top Barcode Items", "Items", "Quantity Sold")
        conn.close()

    def generate_category_chart(self):
        """Generate bar chart for category-wise sales"""
        # Get category sales data
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get loose items category sales
        cursor.execute('''
            SELECT lc.name, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            JOIN loose_items li ON bi.item_name = li.name
            JOIN loose_categories lc ON li.category_id = lc.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'loose'
            GROUP BY lc.name
            ORDER BY total_revenue DESC
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        loose_results = cursor.fetchall()
        
        # Get barcode items sales (as one category)
        cursor.execute('''
            SELECT SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'barcode'
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        barcode_result = cursor.fetchone()
        conn.close()
        
        data = [{'name': row[0], 'value': row[1]} for row in loose_results]
        if barcode_result and barcode_result[0]:
            data.append({'name': 'Barcode Items', 'value': barcode_result[0]})
        
        self.category_chart.create_bar_chart(data, "Category-wise Sales", "Categories", "Revenue (₹)")
    
    def generate_daily_trend_chart(self, bills):
        """Generate line chart for daily sales trend"""
        # Group bills by date
        daily_sales = {}
        for bill in bills:
            bill_date = bill['created_at'][:10]  # Extract date part
            if bill_date in daily_sales:
                daily_sales[bill_date] += bill['total_amount']
            else:
                daily_sales[bill_date] = bill['total_amount']
        
        # Fill missing dates with 0
        current_date = self.start_date
        while current_date <= self.end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in daily_sales:
                daily_sales[date_str] = 0
            current_date += timedelta(days=1)
        
        # Sort by date
        sorted_sales = sorted(daily_sales.items())
        data = [{'date': date_str, 'value': amount} for date_str, amount in sorted_sales]
        
        self.daily_trend_chart.create_line_chart(data, "Daily Sales Trend", "Date", "Revenue (₹)")
    
    def generate_top_categories_chart(self):
        """Generate pie chart for top categories by revenue"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get total revenue for percentage calculation
        total_revenue = float(self.total_revenue_label.text().replace('₹', '').replace(',', ''))
        
        # Get loose items category sales
        cursor.execute('''
            SELECT lc.name, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            JOIN loose_items li ON bi.item_name = li.name
            JOIN loose_categories lc ON li.category_id = lc.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'loose'
            GROUP BY lc.name
            ORDER BY total_revenue DESC
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        loose_results = cursor.fetchall()
        
        # Get barcode items sales (as one category)
        cursor.execute('''
            SELECT SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'barcode'
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        barcode_result = cursor.fetchone()
        conn.close()
        
        data = []
        for row in loose_results:
            data.append({'name': row[0], 'value': row[1]})
        
        if barcode_result and barcode_result[0]:
            data.append({'name': 'Barcode Items', 'value': barcode_result[0]})
        
        self.top_categories_chart.create_pie_chart(data, "Top Categories by Revenue")
    
    def generate_monthly_comparison_chart(self, bills):
        """Generate bar chart for monthly sales comparison (last 12 months, always show 12 bars)"""
        # Group bills by month
        monthly_sales = {}
        for bill in bills:
            bill_date = bill['created_at'][:7] # YYYY-MM
            if bill_date in monthly_sales:
                monthly_sales[bill_date] += bill['total_amount']
            else:
                monthly_sales[bill_date] = bill['total_amount']
        # Find the latest month in the data or use today
        if monthly_sales:
            latest_month = max(monthly_sales.keys())
            latest_dt = datetime.strptime(latest_month, '%Y-%m')
        else:
            latest_dt = datetime.today()
        # Build last 12 months labels
        months = []
        for i in range(11, -1, -1):
            dt = latest_dt - timedelta(days=30*i)  # Approximate month
            label = dt.strftime('%b %Y')
            key = dt.strftime('%Y-%m')
            months.append((key, label))
        # Prepare data for 12 months
        data = []
        fixed_labels = []
        for key, label in months:
            value = monthly_sales.get(key, 0)
            data.append({'name': label, 'value': value})
            fixed_labels.append(label)
        self.monthly_comparison_chart.create_bar_chart(
            data,
            "",  # No title inside chart
            "Month", "Revenue (₹)",
            fixed_num_bars=12,
            fixed_labels=fixed_labels
        )
    
    def get_top_loose_items_data(self):
        """Get top loose items data for export"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bi.item_name, SUM(bi.quantity) as total_weight, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'loose'
            GROUP BY bi.item_name
            ORDER BY total_weight DESC
            LIMIT 20
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        results = cursor.fetchall()
        conn.close()
        return [{'name': row[0], 'weight': row[1], 'revenue': row[2]} for row in results]

    def get_top_barcode_items_data(self):
        """Get top barcode items data for export"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bi.item_name, SUM(bi.quantity) as total_quantity, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'barcode'
            GROUP BY bi.item_name
            ORDER BY total_quantity DESC
            LIMIT 20
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        results = cursor.fetchall()
        conn.close()
        return [{'name': row[0], 'quantity': row[1], 'revenue': row[2]} for row in results]
    
    def get_category_sales_data(self):
        """Get category sales data for export"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get total revenue for percentage calculation
        total_revenue = float(self.total_revenue_label.text().replace('₹', '').replace(',', ''))
        
        # Get loose items category sales
        cursor.execute('''
            SELECT lc.name, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            JOIN loose_items li ON bi.item_name = li.name
            JOIN loose_categories lc ON li.category_id = lc.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'loose'
            GROUP BY lc.name
            ORDER BY total_revenue DESC
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        loose_results = cursor.fetchall()
        
        # Get barcode items sales
        cursor.execute('''
            SELECT SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'barcode'
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        barcode_result = cursor.fetchone()
        conn.close()
        
        data = []
        for row in loose_results:
            percentage = (row[1] / total_revenue * 100) if total_revenue > 0 else 0
            data.append({'name': row[0], 'revenue': row[1], 'percentage': percentage})
        
        if barcode_result and barcode_result[0]:
            percentage = (barcode_result[0] / total_revenue * 100) if total_revenue > 0 else 0
            data.append({'name': 'Barcode Items', 'revenue': barcode_result[0], 'percentage': percentage})
        
        return data
    
    def export_report(self, format_type):
        """Export sales report"""
        if not hasattr(self, 'current_report_data'):
            QMessageBox.warning(self, "No Data", "No report data to export. Please generate a report first.")
            return
        
        # Get file path
        if format_type == 'csv':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Sales Report as CSV",
                f"sales_report_{self.start_date}_{self.end_date}.csv",
                "CSV Files (*.csv)"
            )
        else:  # PDF
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Sales Report as PDF",
                f"sales_report_{self.start_date}_{self.end_date}.pdf",
                "PDF Files (*.pdf)"
            )
        
        if not file_path:
            return
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start export thread
        self.export_thread = ReportGeneratorThread(self.current_report_data, file_path, format_type)
        self.export_thread.finished.connect(self.on_export_finished)
        self.export_thread.start()
    
    def on_export_finished(self, success, message):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Export Complete", message)
        else:
            QMessageBox.critical(self, "Export Failed", message)
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Adjust chart sizes based on window size
        if hasattr(self, 'top_loose_items_chart'):
            width = self.width()
            if width < 1400:
                chart_size = (350, 250)
            else:
                chart_size = (400, 300)
            
            self.top_loose_items_chart.setMinimumSize(*chart_size)
            self.top_barcode_items_chart.setMinimumSize(*chart_size)
            self.category_chart.setMinimumSize(*chart_size)
            self.top_categories_chart.setMinimumSize(*chart_size)
            self.monthly_comparison_chart.setMinimumSize(*chart_size)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesReportWindow()
    window.showMaximized()
    sys.exit(app.exec_())