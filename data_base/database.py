import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict
import sys
import csv

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
        
        # Create barcode_items table with new GST fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS barcode_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                hsn_code TEXT DEFAULT '',
                quantity INTEGER DEFAULT 1,
                base_price REAL NOT NULL,
                sgst_percent REAL DEFAULT 0,
                cgst_percent REAL DEFAULT 0,
                total_price REAL NOT NULL,
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
        
        # Create loose_items table with new GST fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loose_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                hsn_code TEXT DEFAULT '',
                quantity INTEGER DEFAULT 1,
                base_price REAL NOT NULL,
                sgst_percent REAL DEFAULT 0,
                cgst_percent REAL DEFAULT 0,
                total_price REAL NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES loose_categories (id)
            )
        ''')
        # Add unique index for loose_items
        cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_loose_items_unique ON loose_items (category_id, name, hsn_code)''')
        
        # Create bills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                total_amount REAL NOT NULL,
                total_items INTEGER NOT NULL,
                total_weight REAL DEFAULT 0,
                total_sgst REAL DEFAULT 0,
                total_cgst REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create bill_items table with GST fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                hsn_code TEXT DEFAULT '',
                quantity REAL NOT NULL,
                base_price REAL NOT NULL,
                sgst_percent REAL DEFAULT 0,
                cgst_percent REAL DEFAULT 0,
                sgst_amount REAL DEFAULT 0,
                cgst_amount REAL DEFAULT 0,
                final_price REAL NOT NULL,
                item_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bills (id)
            )
        ''')
        
        # Create admin_details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_name TEXT NOT NULL DEFAULT 'My Shop',
                address TEXT NOT NULL DEFAULT 'Shop Address',
                phone_number TEXT NOT NULL DEFAULT '1234567890',
                use_credentials BOOLEAN NOT NULL DEFAULT 0,
                username TEXT NOT NULL DEFAULT 'admin',
                password TEXT NOT NULL DEFAULT 'admin123',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migrate existing data if needed
        self._migrate_existing_data(cursor)
        
        # Insert default categories and items
        self._insert_default_data(cursor)
        
        # Insert default admin details if not exists
        self._insert_default_admin_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _migrate_existing_data(self, cursor):
        """Migrate existing data to new schema"""
        # Check if old columns exist and migrate
        cursor.execute("PRAGMA table_info(barcode_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'hsn_code' not in columns:
            # Add new columns to barcode_items
            cursor.execute('ALTER TABLE barcode_items ADD COLUMN hsn_code TEXT DEFAULT ""')
            cursor.execute('ALTER TABLE barcode_items ADD COLUMN quantity INTEGER DEFAULT 0')
            cursor.execute('ALTER TABLE barcode_items ADD COLUMN sgst_percent REAL DEFAULT 0')
            cursor.execute('ALTER TABLE barcode_items ADD COLUMN cgst_percent REAL DEFAULT 0')
            
            # Rename price to base_price and add total_price
            try:
                cursor.execute('ALTER TABLE barcode_items RENAME COLUMN price TO base_price')
            except:
                pass
            
            try:
                cursor.execute('ALTER TABLE barcode_items ADD COLUMN total_price REAL')
                cursor.execute('UPDATE barcode_items SET total_price = base_price WHERE total_price IS NULL')
            except:
                pass
        
        # Similar migration for loose_items
        cursor.execute("PRAGMA table_info(loose_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'hsn_code' not in columns:
            cursor.execute('ALTER TABLE loose_items ADD COLUMN hsn_code TEXT DEFAULT ""')
            cursor.execute('ALTER TABLE loose_items ADD COLUMN quantity INTEGER DEFAULT 0')
            cursor.execute('ALTER TABLE loose_items ADD COLUMN sgst_percent REAL DEFAULT 0')
            cursor.execute('ALTER TABLE loose_items ADD COLUMN cgst_percent REAL DEFAULT 0')
            
            try:
                cursor.execute('ALTER TABLE loose_items RENAME COLUMN price_per_kg TO base_price')
            except:
                pass
            
            try:
                cursor.execute('ALTER TABLE loose_items ADD COLUMN total_price REAL')
                cursor.execute('UPDATE loose_items SET total_price = base_price WHERE total_price IS NULL')
            except:
                pass
        
        # Migrate bills table
        cursor.execute("PRAGMA table_info(bills)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'total_sgst' not in columns:
            cursor.execute('ALTER TABLE bills ADD COLUMN total_sgst REAL DEFAULT 0')
            cursor.execute('ALTER TABLE bills ADD COLUMN total_cgst REAL DEFAULT 0')
        
        # Migrate bill_items table
        cursor.execute("PRAGMA table_info(bill_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'hsn_code' not in columns:
            cursor.execute('ALTER TABLE bill_items ADD COLUMN hsn_code TEXT DEFAULT ""')
            cursor.execute('ALTER TABLE bill_items ADD COLUMN base_price REAL DEFAULT 0')
            cursor.execute('ALTER TABLE bill_items ADD COLUMN sgst_percent REAL DEFAULT 0')
            cursor.execute('ALTER TABLE bill_items ADD COLUMN cgst_percent REAL DEFAULT 0')
            cursor.execute('ALTER TABLE bill_items ADD COLUMN sgst_amount REAL DEFAULT 0')
            cursor.execute('ALTER TABLE bill_items ADD COLUMN cgst_amount REAL DEFAULT 0')
            cursor.execute('ALTER TABLE bill_items ADD COLUMN final_price REAL DEFAULT 0')
            
            # Update existing records
            cursor.execute('UPDATE bill_items SET base_price = unit_price, final_price = subtotal WHERE base_price = 0')
    
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
            
            # Insert some default loose items with GST
            default_items = [
                ('Rice', 'Basmati Rice', '1006', 80.0, 2.5, 2.5),
                ('Rice', 'Sona Masoori Rice', '1006', 65.0, 2.5, 2.5),
                ('Dals', 'Toor Dal', '0713', 120.0, 2.5, 2.5),
                ('Dals', 'Moong Dal', '0713', 110.0, 2.5, 2.5),
                ('Spices', 'Turmeric Powder', '0910', 200.0, 2.5, 2.5),
                ('Spices', 'Red Chilli Powder', '0904', 180.0, 2.5, 2.5),
                ('Oil', 'Sunflower Oil', '1512', 150.0, 2.5, 2.5),
                ('Oil', 'Coconut Oil', '1513', 180.0, 2.5, 2.5),
            ]
            for category_name, item_name, hsn, total_price, sgst, cgst in default_items:
                base_price = total_price / (1 + (sgst + cgst) / 100)
                cursor.execute('''
                    INSERT OR IGNORE INTO loose_items (category_id, name, hsn_code, base_price, sgst_percent, cgst_percent, total_price)
                    SELECT id, ?, ?, ?, ?, ?, ? FROM loose_categories WHERE name = ?
                ''', (item_name, hsn, base_price, sgst, cgst, total_price, category_name))
        
        # Insert default barcode items if table is empty
        cursor.execute('SELECT COUNT(*) FROM barcode_items')
        if cursor.fetchone()[0] == 0:
            default_barcodes = [
                ('12345678', 'Kit Kat', '1704', 10.0, 6.0, 6.0),
                ('23456789', 'Dairy Milk', '1704', 20.0, 6.0, 6.0),
                ('34567890', '5 Star', '1704', 10.0, 6.0, 6.0),
                ('45678901', 'Perk', '1704', 10.0, 6.0, 6.0),
                ('56789012', 'Munch', '1704', 5.0, 6.0, 6.0),
            ]
            for barcode, name, hsn, total_price, sgst, cgst in default_barcodes:
                base_price = total_price / (1 + (sgst + cgst) / 100)
                cursor.execute('''
                    INSERT OR IGNORE INTO barcode_items (barcode, name, hsn_code, base_price, sgst_percent, cgst_percent, total_price) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (barcode, name, hsn, base_price, sgst, cgst, total_price))
    
    def _insert_default_admin_data(self, cursor):
        """Insert default admin details if they don't exist"""
        cursor.execute('SELECT COUNT(*) FROM admin_details')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO admin_details (shop_name, address, phone_number, use_credentials, username, password) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('My Shop', 'Shop Address', '1234567890', False, 'admin', 'admin123'))
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    # Barcode Items Methods
    def add_barcode_item(self, barcode: str, name: str, hsn_code: str, quantity: int, 
                        total_price: float, sgst_percent: float, cgst_percent: float) -> bool:
        """Add a new barcode item (user supplies final price)"""
        try:
            base_price = total_price / (1 + (sgst_percent + cgst_percent) / 100)
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO barcode_items (barcode, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (barcode, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price))
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
            SELECT id, barcode, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price 
            FROM barcode_items WHERE barcode = ?
        ''', (barcode,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'barcode': result[1],
                'name': result[2],
                'hsn_code': result[3],
                'quantity': result[4],
                'base_price': result[5],
                'sgst_percent': result[6],
                'cgst_percent': result[7],
                'total_price': result[8]
            }
        return None
    
    def get_all_barcode_items(self) -> List[Dict]:
        """Get all barcode items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, barcode, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price 
            FROM barcode_items ORDER BY name
        ''')
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'barcode': row[1],
                'name': row[2],
                'hsn_code': row[3],
                'quantity': row[4],
                'base_price': row[5],
                'sgst_percent': row[6],
                'cgst_percent': row[7],
                'total_price': row[8]
            }
            for row in results
        ]
    
    def update_barcode_item(self, item_id: int, barcode: str, name: str, hsn_code: str, 
                           quantity: int, total_price: float, sgst_percent: float, cgst_percent: float) -> bool:
        """Update barcode item (user supplies final price)"""
        try:
            base_price = total_price / (1 + (sgst_percent + cgst_percent) / 100)
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE barcode_items SET barcode = ?, name = ?, hsn_code = ?, quantity = ?, 
                base_price = ?, sgst_percent = ?, cgst_percent = ?, total_price = ? WHERE id = ?
            ''', (barcode, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price, item_id))
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
            SELECT id, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price, image_path 
            FROM loose_items WHERE category_id = ? ORDER BY name
        ''', (category_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'hsn_code': row[2],
                'quantity': row[3],
                'base_price': row[4],
                'sgst_percent': row[5],
                'cgst_percent': row[6],
                'total_price': row[7],
                'image_path': row[8]
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
    
    def add_loose_item(self, category_id: int, name: str, hsn_code: str, quantity: int,
                      total_price: float, sgst_percent: float, cgst_percent: float, image_path: str = None) -> bool:
        """Add a new loose item (user supplies final price)"""
        try:
            base_price = total_price / (1 + (sgst_percent + cgst_percent) / 100)
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO loose_items (category_id, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price, image_path) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (category_id, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price, image_path))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_loose_item(self, item_id: int, name: str, hsn_code: str, quantity: int,
                         total_price: float, sgst_percent: float, cgst_percent: float, image_path: str = None) -> bool:
        """Update loose item (user supplies final price)"""
        try:
            base_price = total_price / (1 + (sgst_percent + cgst_percent) / 100)
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE loose_items SET name = ?, hsn_code = ?, quantity = ?, base_price = ?, sgst_percent = ?, cgst_percent = ?, total_price = ?, image_path = ? WHERE id = ?
            ''', (name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price, image_path, item_id))
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
                  total_amount: float, total_items: int, total_weight: float, 
                  total_sgst: float, total_cgst: float) -> int:
        """Save a new bill and return bill ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert bill
        cursor.execute('''
            INSERT INTO bills (customer_name, customer_phone, total_amount, total_items, total_weight, total_sgst, total_cgst)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_name, customer_phone, total_amount, total_items, total_weight, total_sgst, total_cgst))
        
        bill_id = cursor.lastrowid
        
        # Insert bill items
        for item in bill_items:
            cursor.execute('''
                INSERT INTO bill_items (bill_id, item_name, hsn_code, quantity, base_price, 
                sgst_percent, cgst_percent, sgst_amount, cgst_amount, final_price, item_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bill_id, item['name'], item['hsn_code'], item['quantity'], item['base_price'],
                  item['sgst_percent'], item['cgst_percent'], item['sgst_amount'], 
                  item['cgst_amount'], item['final_price'], item['item_type']))
        
        conn.commit()
        conn.close()
        return bill_id
    
    def get_all_bills(self) -> List[Dict]:
        """Get all bills"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, customer_name, customer_phone, total_amount, total_items, 
                   total_weight, total_sgst, total_cgst, created_at 
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
                'total_sgst': row[6],
                'total_cgst': row[7],
                'created_at': row[8]
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
                   total_weight, total_sgst, total_cgst, created_at 
            FROM bills WHERE id = ?
        ''', (bill_id,))
        bill_result = cursor.fetchone()
        
        if not bill_result:
            conn.close()
            return None
        
        # Get bill items
        cursor.execute('''
            SELECT item_name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, 
            sgst_amount, cgst_amount, final_price, item_type
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
            'total_sgst': bill_result[6],
            'total_cgst': bill_result[7],
            'created_at': bill_result[8],
            'items': [
                {
                    'name': row[0],
                    'hsn_code': row[1],
                    'quantity': row[2],
                    'base_price': row[3],
                    'sgst_percent': row[4],
                    'cgst_percent': row[5],
                    'sgst_amount': row[6],
                    'cgst_amount': row[7],
                    'final_price': row[8],
                    'item_type': row[9]
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
                   total_weight, total_sgst, total_cgst, created_at 
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
                'total_sgst': row[6],
                'total_cgst': row[7],
                'created_at': row[8]
            }
            for row in results
        ]
    
    def get_bills_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get bills by date range"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, customer_name, customer_phone, total_amount, total_items, 
                   total_weight, total_sgst, total_cgst, created_at 
            FROM bills WHERE DATE(created_at) BETWEEN ? AND ? ORDER BY created_at DESC
        ''', (start_date, end_date))
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
                'total_sgst': row[6],
                'total_cgst': row[7],
                'created_at': row[8]
            }
            for row in results
        ]
    
    def get_customer_names(self) -> List[str]:
        """Get all unique customer names for autocomplete"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT customer_name FROM bills ORDER BY customer_name')
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    # Admin Details Methods
    def get_admin_details(self) -> Optional[Dict]:
        """Get admin details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT shop_name, address, phone_number, use_credentials, username, password 
            FROM admin_details ORDER BY id LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'shop_name': result[0],
                'address': result[1],
                'phone_number': result[2],
                'use_credentials': bool(result[3]),
                'username': result[4],
                'password': result[5]
            }
        return None
    
    def update_admin_details(self, shop_name: str, address: str, phone_number: str, 
                           use_credentials: bool, username: str, password: str) -> bool:
        """Update admin details"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE admin_details SET shop_name = ?, address = ?, phone_number = ?, 
                use_credentials = ?, username = ?, password = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM admin_details ORDER BY id LIMIT 1)
            ''', (shop_name, address, phone_number, use_credentials, username, password))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def verify_admin_credentials(self, username: str, password: str) -> bool:
        """Verify admin credentials"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM admin_details 
            WHERE username = ? AND password = ?
        ''', (username, password))
        result = cursor.fetchone()[0]
        conn.close()
        
        return result > 0

    def import_barcode_items_from_csv(self, file_path: str):
        """Import barcode items from a CSV file. Returns (success_count, fail_count, fail_rows)"""
        required_fields = ["barcode", "name", "hsn_code", "quantity", "sgst", "cgst", "total_price"]
        success_count = 0
        fail_count = 0
        fail_rows = []
        # Pre-fetch all existing barcodes
        existing_barcodes = set()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT barcode FROM barcode_items')
        for row in cursor.fetchall():
            existing_barcodes.add(row[0])
        conn.close()
        to_insert = []
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader, start=2):  # start=2 for header row
                # Validate required fields
                if not all(field in row and row[field].strip() for field in required_fields):
                    fail_count += 1
                    fail_rows.append((idx, "Missing required fields"))
                    continue
                try:
                    barcode = row["barcode"].strip()
                    if barcode in existing_barcodes:
                        fail_count += 1
                        fail_rows.append((idx, "Duplicate barcode"))
                        continue
                    name = row["name"].strip()
                    hsn_code = row["hsn_code"].strip()
                    quantity = int(row["quantity"])
                    sgst = float(row["sgst"])
                    cgst = float(row["cgst"])
                    total_price = float(row["total_price"])
                    to_insert.append((barcode, name, hsn_code, quantity, total_price, sgst, cgst))
                    existing_barcodes.add(barcode)
                except Exception as e:
                    fail_count += 1
                    fail_rows.append((idx, str(e)))
        # Bulk insert
        conn = self.get_connection()
        cursor = conn.cursor()
        for barcode, name, hsn_code, quantity, total_price, sgst, cgst in to_insert:
            base_price = total_price / (1 + (sgst + cgst) / 100)
            cursor.execute('''INSERT OR IGNORE INTO barcode_items (barcode, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (barcode, name, hsn_code, quantity, base_price, sgst, cgst, total_price))
            success_count += 1
        conn.commit()
        conn.close()
        return success_count, fail_count, fail_rows

    def import_loose_items_from_csv(self, file_path: str):
        """Import loose items from a CSV file. Returns (success_count, fail_count, fail_rows)"""
        required_fields = ["category", "name", "hsn_code", "quantity", "sgst", "cgst", "total_price"]
        success_count = 0
        fail_count = 0
        fail_rows = []
        # Build category name to id map
        categories = {cat['name']: cat['id'] for cat in self.get_loose_categories()}
        # Pre-fetch all existing (category_id, name, hsn_code)
        existing_keys = set()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT category_id, name, hsn_code FROM loose_items')
        for row in cursor.fetchall():
            existing_keys.add((row[0], row[1], row[2]))
        conn.close()
        to_insert = []
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader, start=2):
                if not all(field in row and row[field].strip() for field in required_fields):
                    fail_count += 1
                    fail_rows.append((idx, "Missing required fields"))
                    continue
                try:
                    category_name = row["category"].strip()
                    if category_name not in categories:
                        fail_count += 1
                        fail_rows.append((idx, f"Category '{category_name}' not found"))
                        continue
                    category_id = categories[category_name]
                    name = row["name"].strip()
                    hsn_code = row["hsn_code"].strip()
                    key = (category_id, name, hsn_code)
                    if key in existing_keys:
                        fail_count += 1
                        fail_rows.append((idx, "Duplicate item (category, name, hsn_code)"))
                        continue
                    quantity = int(row["quantity"])
                    sgst = float(row["sgst"])
                    cgst = float(row["cgst"])
                    total_price = float(row["total_price"])
                    to_insert.append((category_id, name, hsn_code, quantity, total_price, sgst, cgst))
                    existing_keys.add(key)
                except Exception as e:
                    fail_count += 1
                    fail_rows.append((idx, str(e)))
        # Bulk insert
        conn = self.get_connection()
        cursor = conn.cursor()
        for category_id, name, hsn_code, quantity, total_price, sgst, cgst in to_insert:
            base_price = total_price / (1 + (sgst + cgst) / 100)
            cursor.execute('''INSERT OR IGNORE INTO loose_items (category_id, name, hsn_code, quantity, base_price, sgst_percent, cgst_percent, total_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (category_id, name, hsn_code, quantity, base_price, sgst, cgst, total_price))
            success_count += 1
        conn.commit()
        conn.close()
        return success_count, fail_count, fail_rows