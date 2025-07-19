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
            self.printer.text(f"Customer: {bill_data['customer_name']}\n")
            if bill_data.get('customer_phone'):
                self.printer.text(f"Phone: {bill_data['customer_phone']}\n")
            self.printer.text("-" * 32 + "\n")
            
            # Items header
            self.printer.set(bold=True)
            self.printer.text("Item Details\n")
            self.printer.set(bold=False)
            self.printer.text("-" * 32 + "\n")
            
            # Items with GST breakdown
            total_base_amount = 0
            total_sgst_amount = 0
            total_cgst_amount = 0
            
            for item in bill_data['items']:
                name = item['name']
                if len(name) > 30:
                    name = name[:27] + "..."
                
                # Item name and HSN
                self.printer.text(f"{name}\n")
                if item.get('hsn_code'):
                    self.printer.text(f"HSN: {item['hsn_code']}\n")
                
                # Quantity and base price
                qty_text = f"{item['quantity']:.2f}"
                if item['item_type'] == 'loose':
                    qty_text += "kg"
                
                base_amount = item['quantity'] * item['base_price']
                sgst_amount = item.get('sgst_amount', 0)
                cgst_amount = item.get('cgst_amount', 0)
                final_price = item.get('final_price', base_amount + sgst_amount + cgst_amount)
                
                self.printer.text(f"Qty: {qty_text} x ₹{item['base_price']:.2f} = ₹{base_amount:.2f}\n")
                
                # GST details if applicable
                if item.get('sgst_percent', 0) > 0 or item.get('cgst_percent', 0) > 0:
                    if sgst_amount > 0:
                        self.printer.text(f"SGST ({item['sgst_percent']:.1f}%): ₹{sgst_amount:.2f}\n")
                    if cgst_amount > 0:
                        self.printer.text(f"CGST ({item['cgst_percent']:.1f}%): ₹{cgst_amount:.2f}\n")
                
                self.printer.text(f"Total: ₹{final_price:.2f}\n")
                self.printer.text("-" * 16 + "\n")
                
                # Add to totals
                total_base_amount += base_amount
                total_sgst_amount += sgst_amount
                total_cgst_amount += cgst_amount
            
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
    
    def close_connection(self):
        """Close printer connection"""
        if self.printer:
            try:
                self.printer.close()
            except:
                pass
        self.is_connected = False
        self.printer = None