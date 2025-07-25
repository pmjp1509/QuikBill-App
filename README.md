# GST Billing App

A modern, offline desktop billing application with GST support, inventory management, WhatsApp bill sharing, and thermal printing. Built with Python and PyQt5 for small businesses and shops in India.

## Features
- Create GST-compliant bills (barcode and loose items)
- Inventory management (add/edit/delete items, categories)
- Bill history with search, filter, and CSV export
- WhatsApp bill sharing (send bill as image)
- Thermal printer support (USB/Serial/Network)
- Admin settings (shop details, credentials)
- Customer info autocomplete
- Offline local database (SQLite)

## Installation
1. **Clone the repository:**
   ```
   git clone <your-repo-url>
   cd <project-folder>
   ```
2. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
4. **(Optional) Install system dependencies:**
   - For WhatsApp sharing: Google Chrome browser, WhatsApp Web account
   - For printing: Supported thermal printer drivers

## Usage
1. **Run the app:**
   ```
   python main.py
   ```
2. **Create bills:**
   - Add barcode or loose items
   - Enter/select customer info
   - Print or share via WhatsApp
3. **Manage inventory:**
   - Add/edit/delete items and categories
4. **View bill history:**
   - Search, filter, export, and reprint bills
5. **Admin settings:**
   - Update shop details, credentials

## WhatsApp Bill Sharing
- Requires Google Chrome and WhatsApp Web login
- Bill image is generated and sent automatically
- If automation fails, press Enter manually in WhatsApp Web

## Printing
- Supports USB, Serial, and Network thermal printers
- Configure printer in Admin Settings

## Database
- Uses SQLite (`data_base/billing.db`)
- All data is stored locally and offline

## Project Structure Explained

- **README.md**  
  Project overview, features, setup instructions, usage guide, and troubleshooting tips.

- **build_instructions.txt**  
  Step-by-step instructions for building and packaging the application, especially for Windows users.

- **main.py**  
  The main entry point for the application. Run this file to start the billing app.

- **billing_app.spec**  
  (Optional) PyInstaller specification file for building a standalone executable.

- **requirements.txt**  
  Lists all Python dependencies required to run the application.

- **bills/**  
  Folder where all generated bill images are saved. These images are used for WhatsApp sharing and can be referenced or archived.

- **billing_tabs/**  
  Contains all the main application modules and user interface logic:
  - `admin_settings.py`: Admin and shop settings management.
  - `bill_history.py`: Bill history, search, export, and reprint functionality.
  - `create_bill.py`: Bill creation logic and UI.
  - `home_dashboard.py`: Main dashboard and navigation.
  - `inventory.py`: Inventory and item/category management.
  - `login_dialog.py`: Admin login and authentication dialog.
  - `thermal_printer.py`: Thermal printer integration and printing logic.
  - `whatsapp_dialog.py`: WhatsApp bill sharing dialog and logic.

- **data_base/**  
  Contains the database and related assets:
  - `billing.db`: The main SQLite database file (auto-created on first run).
  - `database.py`: All database logic and schema management.
  - `images/`: Folder for item/category images used in the inventory.

- **pywhatkit_db.txt**  
  Auto-generated by the `pywhatkit` library for WhatsApp automation. Safe to ignore or delete.

- **Other files**  
  May include icons, `.gitignore`, or other configuration files as needed for your project.

## Troubleshooting
- **WhatsApp not sending?** Increase wait time or focus WhatsApp Web tab
- **Printer not working?** Check drivers and connection
- **pywhatkit_db.txt?** Safe to ignore or delete
