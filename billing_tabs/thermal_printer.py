from escpos.printer import Usb, Serial, Network
from escpos.exceptions import Error as EscposError
from datetime import datetime
from typing import Dict, List, Optional
import os
from data_base.database import Database

class ThermalPrinter:
    # Paper width configurations
    PAPER_WIDTHS = {
        '58mm': {
            'width': 24,
            'name_width': 12,
            'qty_width': 4,
            'rate_width': 4,
            'amount_width': 4
        },
        '80mm': {
            'width': 32,
            'name_width': 22,
            'qty_width': 5,
            'rate_width': 7,
            'amount_width': 8
        },
        '112mm': {
            'width': 48,
            'name_width': 30,
            'qty_width': 6,
            'rate_width': 8,
            'amount_width': 10
        }
    }
    
    def __init__(self):
        self.printer = None
        self.is_connected = False
        self.db = Database()
        self.paper_width = '80mm'  # Default paper width
        self.load_shop_details()
        self.load_printer_settings()
    
    def load_printer_settings(self):
        """Load printer settings from database"""
        try:
            admin_details = self.db.get_admin_details()
            if admin_details and admin_details.get('paper_width'):
                self.paper_width = admin_details.get('paper_width', '80mm')
            else:
                self.paper_width = '80mm'
        except Exception as e:
            print(f"Error loading printer settings: {e}")
            self.paper_width = '80mm'
    
    def get_paper_config(self):
        """Get current paper width configuration"""
        return self.PAPER_WIDTHS.get(self.paper_width, self.PAPER_WIDTHS['80mm'])
    
    def set_paper_width(self, width: str):
        """Set paper width (58mm, 80mm, 112mm)"""
        if width in self.PAPER_WIDTHS:
            self.paper_width = width
            # Save to database
            try:
                self.db.update_admin_setting('paper_width', width)
            except Exception as e:
                print(f"Error saving paper width setting: {e}")
            return True
        return False
    
    def load_shop_details(self):
        """Load shop details from database"""
        try:
            admin_details = self.db.get_admin_details()
            if admin_details:
                self.shop_name = admin_details.get('shop_name', 'Your Shop Name')
                self.shop_address = admin_details.get('address', 'Your Shop Address')
                self.shop_phone = admin_details.get('phone_number', 'Your Phone Number')
            else:
                # Fallback to defaults if no admin details found
                self.shop_name = "Your Shop Name"
                self.shop_address = "Your Shop Address"
                self.shop_phone = "Your Phone Number"
        except Exception as e:
            print(f"Error loading shop details: {e}")
            # Fallback to defaults
            self.shop_name = "Your Shop Name"
            self.shop_address = "Your Shop Address"
            self.shop_phone = "Your Phone Number"
        
    def connect_usb_printer(self, vendor_id: int = 0x04b8, product_id: int = 0x0202):
        """Connect to USB thermal printer"""
        try:
            self.printer = Usb(vendor_id, product_id)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"USB connection failed: {e}")
            return False
    
    def connect_serial_printer(self, port: str = "COM1", baudrate: int = 9600):
        """Connect to Serial thermal printer"""
        try:
            self.printer = Serial(port, baudrate)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Serial connection failed: {e}")
            return False
    
    def connect_network_printer(self, host: str, port: int = 9100):
        """Connect to Network thermal printer"""
        try:
            self.printer = Network(host, port)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Network connection failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test printer connection"""
        if not self.is_connected or not self.printer:
            return False
        
        try:
            self.printer.text("Test\n")
            self.printer.cut()
            return True
        except Exception as e:
            print(f"Test failed: {e}")
            return False
    
    def print_bill(self, bill_data: Dict) -> bool:
        """Print a formatted bill with GST details"""
        if not self.is_connected or not self.printer:
            return False
        try:
            config = self.get_paper_config()
            separator = "-" * config['width']
            
            # Set font and alignment
            self.printer.set(align='center', font='a', bold=True, double_height=True)
            self.printer.text(f"{self.shop_name}\n")
            self.printer.set(align='center', font='a', bold=False, double_height=False)
            self.printer.text(f"{self.shop_address}\n")
            self.printer.text(f"Phone: {self.shop_phone}\n")
            self.printer.text(separator + "\n")
            
            # Bill details
            self.printer.set(align='left', font='a', bold=False)
            self.printer.text(f"Bill ID: {bill_data['id']}\n")
            self.printer.text(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text(separator + "\n")
            
            # Items header as table
            self.printer.set(bold=True)
            header_format = f"{{:<{config['name_width']}}}{{:>{config['qty_width']}}}{{:>{config['rate_width']}}}{{:>{config['amount_width']}}}\n"
            self.printer.text(header_format.format("Name", "Qty", "Rate", "Amount"))
            self.printer.set(bold=False)
            self.printer.text(separator + "\n")
            
            # Items as table rows
            total_base_amount = 0
            total_sgst_amount = 0
            total_cgst_amount = 0
            
            for item in bill_data['items']:
                name = item['name'][:config['name_width']-8] if len(item['name']) > config['name_width']-8 else item['name']
                hsn_code = item.get('hsn_code', '')
                
                # Adjust name format based on paper width
                if self.paper_width == '58mm':
                    name_hsn = name  # No HSN for 58mm
                elif self.paper_width == '80mm':
                    name_hsn = f"{name} (HSN: {hsn_code})" if hsn_code else name
                else:  # 112mm
                    name_hsn = f"{name} (HSN: {hsn_code})" if hsn_code else name
                
                # Truncate if still too long
                name_hsn = name_hsn[:config['name_width']] if len(name_hsn) > config['name_width'] else name_hsn
                
                qty = f"{item['quantity']:.2f}"
                if item['item_type'] == 'loose':
                    qty += "kg"
                
                rate = f"{item['base_price']:.2f}"
                amount = f"{item.get('final_price', 0):.2f}"
                
                # Print item line
                item_format = f"{{:<{config['name_width']}}}{{:>{config['qty_width']}}}{{:>{config['rate_width']}}}{{:>{config['amount_width']}}}\n"
                self.printer.text(item_format.format(name_hsn, qty, rate, amount))
                
                # Add to totals
                sgst_amt = item.get('sgst_amount', 0)
                cgst_amt = item.get('cgst_amount', 0)
                total_base_amount += item['quantity'] * item['base_price']
                total_sgst_amount += sgst_amt
                total_cgst_amount += cgst_amt
            
            self.printer.text(separator + "\n")
            
            # Bill summary
            self.printer.set(bold=True)
            self.printer.text("BILL SUMMARY\n")
            self.printer.set(bold=False)
            self.printer.text(f"Total Items: {bill_data['total_items']}\n")
            
            if bill_data.get('total_weight', 0) > 0:
                self.printer.text(f"Total Weight: {bill_data['total_weight']:.2f}kg\n")
            
            self.printer.text(f"Base Amount: ₹{total_base_amount:.2f}\n")
            
            if total_sgst_amount > 0:
                self.printer.text(f"Total SGST: ₹{total_sgst_amount:.2f}\n")
            if total_cgst_amount > 0:
                self.printer.text(f"Total CGST: ₹{total_cgst_amount:.2f}\n")
            
            self.printer.text(separator + "\n")
            self.printer.set(bold=True, double_height=True)
            self.printer.text(f"GRAND TOTAL: ₹{bill_data['total_amount']:.2f}\n")
            self.printer.set(bold=False, double_height=False)
            self.printer.text(separator + "\n")
            self.printer.set(align='center')
            self.printer.text("Thank you for shopping!\n")
            self.printer.text("Visit us again!\n")
            
            # Cut paper
            self.printer.cut()
            return True
        except Exception as e:
            print(f"Print failed: {e}")
            return False
    
    def print_test_page(self) -> bool:
        """Print a test page with current paper width configuration"""
        if not self.is_connected or not self.printer:
            return False
        
        try:
            config = self.get_paper_config()
            separator = "-" * config['width']
            
            self.printer.set(align='center', font='a', bold=True, double_height=True)
            self.printer.text("TEST PAGE\n")
            self.printer.set(align='center', font='a', bold=False, double_height=False)
            self.printer.text(f"{self.shop_name}\n")
            self.printer.text(separator + "\n")
            self.printer.text(f"Paper Width: {self.paper_width}\n")
            self.printer.text(f"Print Width: {config['width']} characters\n")
            self.printer.text(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text("Printer is working correctly!\n")
            self.printer.text("GST-enabled billing system\n")
            self.printer.text(separator + "\n")
            
            # Show sample format
            self.printer.set(bold=True)
            header_format = f"{{:<{config['name_width']}}}{{:>{config['qty_width']}}}{{:>{config['rate_width']}}}{{:>{config['amount_width']}}}\n"
            self.printer.text(header_format.format("Name", "Qty", "Rate", "Amount"))
            self.printer.set(bold=False)
            self.printer.text(separator + "\n")
            
            # Sample items
            sample_items = [
                ("Rice", "2.0kg", "50.00", "100.00"),
                ("Sugar", "1.5kg", "40.00", "60.00"),
                ("Dal", "1.0kg", "80.00", "80.00")
            ]
            
            for name, qty, rate, amount in sample_items:
                item_format = f"{{:<{config['name_width']}}}{{:>{config['qty_width']}}}{{:>{config['rate_width']}}}{{:>{config['amount_width']}}}\n"
                self.printer.text(item_format.format(name, qty, rate, amount))
            
            self.printer.text(separator + "\n")
            self.printer.set(bold=True)
            self.printer.text("GRAND TOTAL: ₹240.00\n")
            self.printer.set(bold=False)
            self.printer.text(separator + "\n")
            self.printer.cut()
            return True
        except Exception as e:
            print(f"Test print failed: {e}")
            return False
    
    def print_format_demo(self) -> bool:
        """Print a demo showing how bills will look with current settings"""
        if not self.is_connected or not self.printer:
            return False
        
        try:
            config = self.get_paper_config()
            separator = "-" * config['width']
            
            # Header
            self.printer.set(align='center', font='a', bold=True, double_height=True)
            self.printer.text(f"{self.shop_name}\n")
            self.printer.set(align='center', font='a', bold=False, double_height=False)
            self.printer.text(f"{self.shop_address}\n")
            self.printer.text(f"Phone: {self.shop_phone}\n")
            self.printer.text(separator + "\n")
            
            # Bill details
            self.printer.set(align='left', font='a', bold=False)
            self.printer.text(f"Bill ID: 12345\n")
            self.printer.text(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text(separator + "\n")
            
            # Items header
            self.printer.set(bold=True)
            header_format = f"{{:<{config['name_width']}}}{{:>{config['qty_width']}}}{{:>{config['rate_width']}}}{{:>{config['amount_width']}}}\n"
            self.printer.text(header_format.format("Name", "Qty", "Rate", "Amount"))
            self.printer.set(bold=False)
            self.printer.text(separator + "\n")
            
            # Sample items with HSN codes
            sample_items = [
                ("Rice", "HSN: 1006", "2.0kg", "50.00", "100.00"),
                ("Sugar", "HSN: 1701", "1.5kg", "40.00", "60.00"),
                ("Dal", "HSN: 0713", "1.0kg", "80.00", "80.00")
            ]
            
            for name, hsn, qty, rate, amount in sample_items:
                if self.paper_width == '58mm':
                    name_hsn = name  # No HSN for 58mm
                else:
                    name_hsn = f"{name} ({hsn})"
                
                name_hsn = name_hsn[:config['name_width']] if len(name_hsn) > config['name_width'] else name_hsn
                
                item_format = f"{{:<{config['name_width']}}}{{:>{config['qty_width']}}}{{:>{config['rate_width']}}}{{:>{config['amount_width']}}}\n"
                self.printer.text(item_format.format(name_hsn, qty, rate, amount))
            
            self.printer.text(separator + "\n")
            
            # Summary
            self.printer.set(bold=True)
            self.printer.text("BILL SUMMARY\n")
            self.printer.set(bold=False)
            self.printer.text(f"Total Items: 3\n")
            self.printer.text(f"Total Weight: 4.50kg\n")
            self.printer.text(f"Base Amount: ₹240.00\n")
            self.printer.text(f"Total SGST: ₹12.00\n")
            self.printer.text(f"Total CGST: ₹12.00\n")
            self.printer.text(separator + "\n")
            self.printer.set(bold=True, double_height=True)
            self.printer.text(f"GRAND TOTAL: ₹264.00\n")
            self.printer.set(bold=False, double_height=False)
            self.printer.text(separator + "\n")
            self.printer.set(align='center')
            self.printer.text("Thank you for shopping!\n")
            self.printer.text("Visit us again!\n")
            self.printer.cut()
            return True
        except Exception as e:
            print(f"Format demo failed: {e}")
            return False
    
    def refresh_shop_details(self):
        """Refresh shop details from database (useful after admin settings changes)"""
        self.load_shop_details()
    
    def close_connection(self):
        """Close printer connection"""
        if self.printer:
            try:
                self.printer.close()
            except:
                pass
        self.is_connected = False
        self.printer = None