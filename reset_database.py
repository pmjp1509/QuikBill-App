import os
from data_base.database import Database

DB_PATH = os.path.join(os.path.dirname(__file__), 'data_base', 'billing.db')

def main():
    print('WARNING: This will delete all billing data and reset the database!')
    confirm = input('Type YES to continue: ')
    if confirm.strip().upper() != 'YES':
        print('Aborted.')
        return
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print('Deleted existing billing.db.')
    else:
        print('No existing billing.db found.')
    # Recreate the database
    db = Database()
    print('Database has been reset and initialized.')

if __name__ == '__main__':
    main()


