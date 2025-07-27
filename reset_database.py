import sqlite3
import os

def reset_database(db_path='data_base/billing.db'):
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create tables (including Gmail in admin_details)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT NOT NULL DEFAULT 'My Shop',
            address TEXT NOT NULL DEFAULT 'Shop Address',
            phone_number TEXT NOT NULL DEFAULT '1234567890',
            gmail TEXT NOT NULL DEFAULT '',
            use_credentials BOOLEAN NOT NULL DEFAULT 0,
            username TEXT NOT NULL DEFAULT 'admin',
            password TEXT NOT NULL DEFAULT 'admin123',
            location TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        INSERT INTO admin_details (shop_name, address, phone_number, gmail, use_credentials, username, password, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('My Shop', 'Shop Address', '1234567890', '', False, 'admin', 'admin123', ''))
    # (Re)create other tables as needed...
    conn.commit()
    conn.close()
    print('Database reset complete.')

if __name__ == '__main__':
    reset_database()


