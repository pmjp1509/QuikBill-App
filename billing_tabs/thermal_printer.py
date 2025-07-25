from escpos.printer import Usb, Serial, Network
from escpos.exceptions import Error as EscposError
from datetime import datetime
from typing import Dict, List, Optional
import os
from data_base.database import Database

class ThermalPrinter:
    def __init__(self):
        self.printer = None
        self.is_connected = False
        self.db = Database()
        self.load_shop_details()
    
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
            # Set font and alignment
            self.printer.set(align='center', font='a', bold=True, double_height=True)
            self.printer.text(f"{self.shop_name}\n")
            self.printer.set(align='center', font='a', bold=False, double_height=False)
            self.printer.text(f"{self.shop_address}\n")
            self.printer.text(f"Phone: {self.shop_phone}\n")
            self.printer.text("-" * 32 + "\n")
            # Bill details
            self.printer.set(align='left', font='a', bold=False)
            self.printer.text(f"Bill ID: {bill_data['id']}\n")
            self.printer.text(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text("-" * 32 + "\n")
            # Items header as table
            self.printer.set(bold=True)
            self.printer.text(f"{'Name':<10}{'Qty':>5}{'Rate':>7}{'Amount':>8}\n")
            self.printer.set(bold=False)
            self.printer.text("-" * 32 + "\n")
            # Items as table rows
            total_base_amount = 0
            total_sgst_amount = 0
            total_cgst_amount = 0
            for item in bill_data['items']:
                name = item['name'][:10] if len(item['name']) > 10 else item['name']
                hsn_code = item.get('hsn_code', '')
                name_hsn = f"{name} (HSN: {hsn_code})" if hsn_code else name
                qty = f"{item['quantity']:.2f}"
                if item['item_type'] == 'loose':
                    qty += "kg"
                rate = f"{item['base_price']:.2f}"
                amount = f"{item.get('final_price', 0):.2f}"
                # Print item line with HSN code beside name
                self.printer.text(f"{name_hsn:<22}{qty:>5}{rate:>7}{amount:>8}\n")
                
                # Add to totals
                sgst_amt = item.get('sgst_amount', 0)
                cgst_amt = item.get('cgst_amount', 0)
                total_base_amount += item['quantity'] * item['base_price']
                total_sgst_amount += sgst_amt
                total_cgst_amount += cgst_amt
            self.printer.text("-" * 32 + "\n")
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
            self.printer.text("-" * 32 + "\n")
            self.printer.set(bold=True, double_height=True)
            self.printer.text(f"GRAND TOTAL: ₹{bill_data['total_amount']:.2f}\n")
            self.printer.set(bold=False, double_height=False)
            self.printer.text("-" * 32 + "\n")
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
        """Print a test page"""
        if not self.is_connected or not self.printer:
            return False
        
        try:
            self.printer.set(align='center', font='a', bold=True, double_height=True)
            self.printer.text("TEST PAGE\n")
            self.printer.set(align='center', font='a', bold=False, double_height=False)
            self.printer.text(f"{self.shop_name}\n")
            self.printer.text("-" * 32 + "\n")
            self.printer.text(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text("Printer is working correctly!\n")
            self.printer.text("GST-enabled billing system\n")
            self.printer.text("-" * 32 + "\n")
            self.printer.cut()
            return True
        except Exception as e:
            print(f"Test print failed: {e}")
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