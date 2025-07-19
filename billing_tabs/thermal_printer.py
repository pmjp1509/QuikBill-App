from escpos.printer import Usb, Serial, Network
from escpos.exceptions import Error as EscposError
from datetime import datetime
from typing import Dict, List, Optional
import os

class ThermalPrinter:
    def __init__(self):
        self.printer = None
        self.is_connected = False
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
    
    def format_bill_receipt(self, bill_data: Dict) -> str:
        """Format bill data for thermal printer"""
        receipt = ""
        
        # Header
        receipt += f"{self.shop_name}\n"
        receipt += f"{self.shop_address}\n"
        receipt += f"Phone: {self.shop_phone}\n"
        receipt += "-" * 32 + "\n"
        
        # Bill details
        receipt += f"Bill ID: {bill_data['id']}\n"
        receipt += f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        receipt += f"Customer: {bill_data['customer_name']}\n"
        if bill_data.get('customer_phone'):
            receipt += f"Phone: {bill_data['customer_phone']}\n"
        receipt += "-" * 32 + "\n"
        
        # Items header
        receipt += "Item               Qty  Price\n"
        receipt += "-" * 32 + "\n"
        
        # Items
        for item in bill_data['items']:
            name = item['name']
            if len(name) > 18:
                name = name[:15] + "..."
            
            qty = f"{item['quantity']:.2f}"
            if item['item_type'] == 'loose':
                qty += "kg"
            
            price = f"₹{item['subtotal']:.2f}"
            
            # Format line with proper spacing
            receipt += f"{name:<18} {qty:<4} {price:>8}\n"
        
        receipt += "-" * 32 + "\n"
        
        # Totals
        receipt += f"Total Items: {bill_data['total_items']}\n"
        if bill_data.get('total_weight', 0) > 0:
            receipt += f"Total Weight: {bill_data['total_weight']:.2f}kg\n"
        receipt += f"TOTAL: ₹{bill_data['total_amount']:.2f}\n"
        
        receipt += "-" * 32 + "\n"
        receipt += "Thank you for shopping!\n"
        receipt += "Visit us again!\n"
        
        return receipt
    
    def print_bill(self, bill_data: Dict) -> bool:
        """Print a formatted bill"""
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
            self.printer.text(f"Customer: {bill_data['customer_name']}\n")
            if bill_data.get('customer_phone'):
                self.printer.text(f"Phone: {bill_data['customer_phone']}\n")
            self.printer.text("-" * 32 + "\n")
            
            # Items header
            self.printer.set(bold=True)
            self.printer.text("Item               Qty  Price\n")
            self.printer.set(bold=False)
            self.printer.text("-" * 32 + "\n")
            
            # Items
            for item in bill_data['items']:
                name = item['name']
                if len(name) > 18:
                    name = name[:15] + "..."
                
                qty = f"{item['quantity']:.2f}"
                if item['item_type'] == 'loose':
                    qty += "kg"
                
                price = f"₹{item['subtotal']:.2f}"
                
                # Format line with proper spacing
                self.printer.text(f"{name:<18} {qty:<4} {price:>8}\n")
            
            self.printer.text("-" * 32 + "\n")
            
            # Totals
            self.printer.set(bold=True)
            self.printer.text(f"Total Items: {bill_data['total_items']}\n")
            if bill_data.get('total_weight', 0) > 0:
                self.printer.text(f"Total Weight: {bill_data['total_weight']:.2f}kg\n")
            self.printer.text(f"TOTAL: ₹{bill_data['total_amount']:.2f}\n")
            self.printer.set(bold=False)
            
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
            self.printer.text("-" * 32 + "\n")
            self.printer.cut()
            return True
        except Exception as e:
            print(f"Test print failed: {e}")
            return False
    
    def close_connection(self):
        """Close printer connection"""
        if self.printer:
            try:
                self.printer.close()
            except:
                pass
        self.is_connected = False
        self.printer = None