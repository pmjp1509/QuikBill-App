import sys
import os
from data_base.database import Database

db = Database()
conn = db.get_connection()
try:
    cursor = conn.cursor()
    cursor.execute('DELETE FROM loose_items')
    cursor.execute('DELETE FROM barcode_items')
    cursor.execute('DELETE FROM loose_categories')
    conn.commit()
finally:
    conn.close()

db.init_database()
print("Inventory reset and re-initialized with default data.")


