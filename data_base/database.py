import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict
import sys

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            if getattr(sys, 'frozen', False):
                # Running as a PyInstaller bundle
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as a script
                base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            db_path = os.path.join(base_dir, 'data_base', 'billing.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create barcode_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS barcode_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create loose_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loose_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create loose_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loose_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price_per_kg REAL NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES loose_categories (id)
            )
        ''')
        
        # Create bills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                total_amount REAL NOT NULL,
                total_items INTEGER NOT NULL,
                total_weight REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create bill_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                item_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bills (id)
            )
        ''')
        
        # Insert default categories and items
        self._insert_default_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_data(self, cursor):
        """Insert default categories and items if they don't exist"""
        # Only insert if tables are empty
        cursor.execute('SELECT COUNT(*) FROM loose_categories')
        if cursor.fetchone()[0] == 0:
            # Insert default categories
            default_categories = ['Rice', 'Dals', 'Spices', 'Oil', 'Vegetables']
            for category in default_categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO loose_categories (name) VALUES (?)
                ''', (category,))
            # Insert some default loose items
            default_items = [
                ('Rice', 'Basmati Rice', 80.0),
                ('Rice', 'Sona Masoori Rice', 65.0),
                ('Dals', 'Toor Dal', 120.0),
                ('Dals', 'Moong Dal', 110.0),
                ('Spices', 'Turmeric Powder', 200.0),
                ('Spices', 'Red Chilli Powder', 180.0),
                ('Oil', 'Sunflower Oil', 150.0),
                ('Oil', 'Coconut Oil', 180.0),
            ]
            for category_name, item_name, price in default_items:
                cursor.execute('''
                    INSERT OR IGNORE INTO loose_items (category_id, name, price_per_kg)
                    SELECT id, ?, ? FROM loose_categories WHERE name = ?
                ''', (item_name, price, category_name))
        # Insert default barcode items if table is empty
        cursor.execute('SELECT COUNT(*) FROM barcode_items')
        if cursor.fetchone()[0] == 0:
            default_barcodes = [
                ('12345678', 'Kit Kat', 10.0),
                ('23456789', 'Dairy Milk', 20.0),
                ('34567890', '5 Star', 10.0),
                ('45678901', 'Perk', 10.0),
                ('56789012', 'Munch', 5.0),
            ]
            for barcode, name, price in default_barcodes:
                cursor.execute('''
                    INSERT OR IGNORE INTO barcode_items (barcode, name, price) VALUES (?, ?, ?)
                ''', (barcode, name, price))
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    # Barcode Items Methods
    def add_barcode_item(self, barcode: str, name: str, price: float) -> bool:
        """Add a new barcode item"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO barcode_items (barcode, name, price) VALUES (?, ?, ?)
            ''', (barcode, name, price))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_barcode_item(self, barcode: str) -> Optional[Dict]:
        """Get barcode item by barcode"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, barcode, name, price FROM barcode_items WHERE barcode = ?
        ''', (barcode,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'barcode': result[1],
                'name': result[2],
                'price': result[3]
            }
        return None
    
    def get_all_barcode_items(self) -> List[Dict]:
        """Get all barcode items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, barcode, name, price FROM barcode_items ORDER BY name
        ''')
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'barcode': row[1],
                'name': row[2],
                'price': row[3]
            }
            for row in results
        ]
    
    def update_barcode_item(self, item_id: int, barcode: str, name: str, price: float) -> bool:
        """Update barcode item"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE barcode_items SET barcode = ?, name = ?, price = ? WHERE id = ?
            ''', (barcode, name, price, item_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def delete_barcode_item(self, item_id: int) -> bool:
        """Delete barcode item"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM barcode_items WHERE id = ?', (item_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    # Loose Items Methods
    def get_loose_categories(self) -> List[Dict]:
        """Get all loose categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM loose_categories ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        
        return [{'id': row[0], 'name': row[1]} for row in results]
    
    def get_loose_items_by_category(self, category_id: int) -> List[Dict]:
        """Get loose items by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, price_per_kg, image_path FROM loose_items 
            WHERE category_id = ? ORDER BY name
        ''', (category_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'price_per_kg': row[2],
                'image_path': row[3]
            }
            for row in results
        ]
    
    def add_loose_category(self, name: str) -> bool:
        """Add a new loose category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO loose_categories (name) VALUES (?)', (name,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def add_loose_item(self, category_id: int, name: str, price_per_kg: float, image_path: str = None) -> bool:
        """Add a new loose item"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO loose_items (category_id, name, price_per_kg, image_path) 
                VALUES (?, ?, ?, ?)
            ''', (category_id, name, price_per_kg, image_path))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_loose_item(self, item_id: int, name: str, price_per_kg: float, image_path: str = None) -> bool:
        """Update loose item"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE loose_items SET name = ?, price_per_kg = ?, image_path = ? WHERE id = ?
            ''', (name, price_per_kg, image_path, item_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete_loose_item(self, item_id: int) -> bool:
        """Delete loose item"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM loose_items WHERE id = ?', (item_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    # Bills Methods
    def save_bill(self, customer_name: str, customer_phone: str, bill_items: List[Dict], 
                  total_amount: float, total_items: int, total_weight: float) -> int:
        """Save a new bill and return bill ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert bill
        cursor.execute('''
            INSERT INTO bills (customer_name, customer_phone, total_amount, total_items, total_weight)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_name, customer_phone, total_amount, total_items, total_weight))
        
        bill_id = cursor.lastrowid
        
        # Insert bill items
        for item in bill_items:
            cursor.execute('''
                INSERT INTO bill_items (bill_id, item_name, quantity, unit_price, subtotal, item_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (bill_id, item['name'], item['quantity'], item['unit_price'], 
                  item['subtotal'], item['item_type']))
        
        conn.commit()
        conn.close()
        return bill_id
    
    def get_all_bills(self) -> List[Dict]:
        """Get all bills"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, customer_name, customer_phone, total_amount, total_items, 
                   total_weight, created_at 
            FROM bills ORDER BY created_at DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'customer_name': row[1],
                'customer_phone': row[2],
                'total_amount': row[3],
                'total_items': row[4],
                'total_weight': row[5],
                'created_at': row[6]
            }
            for row in results
        ]
    
    def get_bill_by_id(self, bill_id: int) -> Optional[Dict]:
        """Get bill by ID with items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get bill details
        cursor.execute('''
            SELECT id, customer_name, customer_phone, total_amount, total_items, 
                   total_weight, created_at 
            FROM bills WHERE id = ?
        ''', (bill_id,))
        bill_result = cursor.fetchone()
        
        if not bill_result:
            conn.close()
            return None
        
        # Get bill items
        cursor.execute('''
            SELECT item_name, quantity, unit_price, subtotal, item_type
            FROM bill_items WHERE bill_id = ?
        ''', (bill_id,))
        items_results = cursor.fetchall()
        
        conn.close()
        
        return {
            'id': bill_result[0],
            'customer_name': bill_result[1],
            'customer_phone': bill_result[2],
            'total_amount': bill_result[3],
            'total_items': bill_result[4],
            'total_weight': bill_result[5],
            'created_at': bill_result[6],
            'items': [
                {
                    'name': row[0],
                    'quantity': row[1],
                    'unit_price': row[2],
                    'subtotal': row[3],
                    'item_type': row[4]
                }
                for row in items_results
            ]
        }
    
    def search_bills(self, customer_name: str) -> List[Dict]:
        """Search bills by customer name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, customer_name, customer_phone, total_amount, total_items, 
                   total_weight, created_at 
            FROM bills WHERE customer_name LIKE ? ORDER BY created_at DESC
        ''', (f'%{customer_name}%',))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'customer_name': row[1],
                'customer_phone': row[2],
                'total_amount': row[3],
                'total_items': row[4],
                'total_weight': row[5],
                'created_at': row[6]
            }
            for row in results
        ]