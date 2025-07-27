import os
from data_base.database import Database

def reset_database(db_path='data_base/billing.db'):
    if os.path.exists(db_path):
        os.remove(db_path)
        print('Deleted existing billing.db.')
    else:
        print('No existing billing.db found.')
    # Recreate the database using the Database class, which handles all initialization
    db = Database(db_path)
    print('Database has been reset and initialized.')

if __name__ == '__main__':
    reset_database()


