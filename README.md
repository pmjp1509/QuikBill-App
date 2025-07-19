# Desktop Billing Application

A complete, production-ready Python desktop application for offline billing with barcode scanning, thermal printing, and inventory management.

## Features

### 🏠 Home Dashboard
- Clean, user-friendly interface with large navigation buttons
- Three main sections: Create Bill, Bill History, and Inventory
- Non-technical shopkeeper-friendly design

### 🧾 Create Bill
- **Barcode Items**: Keyboard-wedge scanner support with auto-add functionality
- **Loose Items**: Category-based selection with visual tiles
- **Live Bill Panel**: Real-time bill calculation with quantity controls
- **Customer Information**: Mandatory customer name, optional phone number
- **Thermal Printing**: Direct ESC/POS printer support for 58mm receipts

### 📜 Bill History
- Complete bill history with search functionality
- Bill details view with itemized breakdown
- Reprint functionality for any previous bill
- CSV export for all bills

### 🧺 Inventory Management
- **Barcode Items**: Add/Edit/Delete with barcode, name, and price (5 sample items auto-initialized if empty)
- **Loose Items**: Category-based organization with images
- **Categories**: Manage loose item categories
- **Price Management**: Remember last-used prices

### 🖨️ Thermal Printing
- ESC/POS 58mm thermal printer support
- Professional receipt formatting
- Shop branding with name, address, and phone
- Itemized billing with totals
- No browser or Ctrl+P dependencies

## Tech Stack

- **GUI**: PyQt5
- **Database**: SQLite (offline)
- **Printing**: python-escpos, pyusb (for USB printer support)
- **Image Handling**: Pillow
- **CSV Export**: Python csv module
- **Packaging**: PyInstaller

## Installation

1. **Clone/Download** the application files
2. **Install Python 3.7+** if not already installed
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # For USB printer support, ensure pyusb and libusb are installed
   ```
4. **Run the application**:
   ```bash
   python main.py
   ```

## Building Executable

Create a standalone Windows executable:

```bash
# Simple build
pyinstaller --onefile --windowed main.py

# Advanced build with custom settings
pyinstaller billing_app.spec
```

## Printer Setup

### Supported Printers
- Epson TM-T20, TM-T82, TM-T88 series
- Star TSP100, TSP650, TSP700 series
- Citizen CT-S310, CT-S2000 series
- Generic ESC/POS compatible printers

### Connection Types
- **USB**: Direct USB connection (most common)
- **Serial**: RS-232 serial connection
- **Network**: Ethernet/WiFi network connection

### Setup Steps
1. Install printer drivers
2. Connect printer via USB/Serial/Network
3. Test printer connection in the application
4. Configure printer settings if needed

## Database

The application uses SQLite for local data storage:
- **data_base/billing.db**: Auto-created on first run in the data_base folder
- **Tables**: barcode_items, loose_categories, loose_items, bills, bill_items
- **Default Data**: On first run, 5 sample barcode items (Kit Kat, Dairy Milk, 5 Star, Perk, Munch) and several loose categories/items are added if the tables are empty.
- **Backup**: Regular database backups recommended

## File Structure

```
main.py                       # Application entry point
billing_tabs/
├── home_dashboard.py         # Main dashboard window
├── create_bill.py            # Bill creation interface
├── bill_history.py           # Bill history and search
├── inventory.py              # Inventory management
├── thermal_printer.py        # Thermal printing logic

data_base/
├── database.py               # Database operations
├── billing.db                # SQLite database (auto-created)

requirements.txt              # Python dependencies
billing_app.spec              # PyInstaller configuration
build_instructions.txt        # Build and deployment instructions
README.md                     # This file
```

## Usage

### Creating a Bill
1. Click "Create Bill" from the home dashboard
2. Scan barcodes or add loose items
3. Adjust quantities using +/- buttons
4. Click "Finish & Print Bill"
5. Enter customer information
6. Bill is saved and printed automatically

### Managing Inventory
1. Click "Inventory" from the home dashboard
2. **Barcode Items**: Add items with barcode, name, and price
3. **Loose Items**: Add categories and items with images
4. Edit or delete items as needed

### Viewing Bill History
1. Click "Bill History" from the home dashboard
2. Search bills by customer name
3. View detailed bill information
4. Reprint any previous bill
5. Export all bills to CSV

## Customization

### Shop Information
Edit the shop details in `thermal_printer.py`:
```python
self.shop_name = "Your Shop Name"
self.shop_address = "Your Shop Address"
self.shop_phone = "Your Phone Number"
```

### Default Categories
Modify default categories in `data_base/database.py`:
```python
default_categories = ['Rice', 'Dals', 'Spices', 'Oil', 'Vegetables']
```

### Thermal Receipt Format
Customize receipt layout in `thermal_printer.py` method `print_bill()`.

## Troubleshooting

### Common Issues
- **Printer not detected**: Check USB connection, install pyusb and libusb, and drivers
- **Database errors**: Delete billing.db to reset (make sure you are editing the correct database file; see below)
- **Permission issues**: Run as Administrator
- **Barcode scanner**: Ensure keyboard-wedge mode

#### Multiple Database Files
If you see unexpected data, you may have multiple `billing.db` files (e.g., in both your project root and `dist/data_base/`). Always check which one your app is using. You can add a print statement in `database.py` to confirm the path.

#### Resetting Inventory
To reset all inventory data and re-initialize with default items, run the provided reset script (if available) or delete `billing.db` and restart the app.

### Support
For technical support or customization requests, contact the development team.

## License

This application is provided as-is for educational and commercial use. Modify and distribute according to your needs.