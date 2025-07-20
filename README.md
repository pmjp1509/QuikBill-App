# Enhanced Desktop Billing Application with GST Support

A complete, production-ready Python desktop application for offline billing with GST support, barcode scanning, thermal printing, and advanced inventory management.

## 🆕 New Features in Version 2.0

### 🎯 Responsive UI Design
- **DPI Awareness**: Automatic scaling for different screen resolutions
- **Resizable Windows**: All windows are fully resizable with adaptive layouts
- **Dynamic Font Scaling**: UI elements scale based on window size
- **Responsive Tables**: Column widths adjust automatically

### 🧺 Enhanced Inventory Management
- **HSN Code Support**: Track HSN codes for all items
- **GST Integration**: SGST and CGST percentage configuration per item
- **Quantity Tracking**: Monitor stock levels for all items
- **Auto-calculated Total Price**: Base Price + SGST + CGST
- **Improved UI**: Better forms with real-time calculations

### 🧾 GST-Aware Billing System
- **Complete GST Breakdown**: Shows base price, SGST, CGST, and final price
- **Real-time Tax Calculations**: Automatic GST computation during billing
- **Enhanced Bill Display**: Shows all tax components in the bill table
- **GST Summary**: Total SGST and CGST amounts displayed

### 🖨️ Enhanced Thermal Printing
- **GST Receipt Format**: Professional receipts with complete tax breakdown
- **HSN Code Printing**: HSN codes printed for each item
- **Tax Summary**: Separate section showing total SGST and CGST
- **Compact Design**: Optimized for 58mm thermal printers

### 📤 Advanced Export Features
- **Date Range Export**: Export bills for specific date ranges
- **Filtered Export**: Export currently filtered/searched bills
- **Enhanced CSV Format**: Includes GST details in exports
- **Multiple Export Options**: All bills or filtered results

### 🔍 Customer Name Autocomplete
- **Smart Suggestions**: Auto-complete from previous customer names
- **Dynamic Filtering**: Suggestions update as you type
- **Case-insensitive Search**: Flexible matching

## Core Features

### 🏠 Home Dashboard
- Clean, responsive interface with large navigation buttons
- Four main sections: Create Bill, Bill History, Inventory, and Settings
- GST-enabled system branding
- Optional admin authentication for enhanced security

### 🧾 Create Bill
- **Barcode Items**: Keyboard-wedge scanner support with auto-add functionality
- **Loose Items**: Category-based selection with visual tiles and GST details
- **Live Bill Panel**: Real-time bill calculation with GST breakdown
- **Customer Information**: Autocomplete customer names, optional phone number
- **Thermal Printing**: Direct ESC/POS printer support for 58mm receipts with GST

### 📜 Bill History
- Complete bill history with advanced search functionality
- Date range filtering for targeted bill searches
- Bill details view with itemized GST breakdown
- Reprint functionality for any previous bill
- Enhanced CSV export with multiple filter options

### 🧺 Inventory Management
- **Barcode Items**: Add/Edit/Delete with barcode, name, HSN code, quantity, base price, SGST%, CGST%
- **Loose Items**: Category-based organization with images and GST details
- **Categories**: Manage loose item categories with delete functionality
- **GST Management**: Configure tax rates per item with auto-calculation
- **Responsive Tables**: Adaptive column widths and font sizes

### ⚙️ Admin Settings
- **Shop Details Management**: Edit shop name, address, and phone number
- **Security Configuration**: Enable/disable admin authentication requirement
- **Credential Management**: Default credentials (admin/admin123) with secure verification
- **Access Control**: Optional login screen before accessing the dashboard

### 🖨️ Thermal Printing
- ESC/POS 58mm thermal printer support
- Professional receipt formatting with GST breakdown
- Shop branding with name, address, and phone
- Itemized billing with base price, taxes, and totals
- HSN code display for compliance

## Tech Stack

- **GUI**: PyQt5 with responsive design
- **Database**: SQLite (offline) with GST schema
- **Printing**: python-escpos, pyusb (for USB printer support)
- **Image Handling**: Pillow
- **CSV Export**: Python csv module with enhanced filtering
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

## Database Schema Updates

The enhanced version includes new database fields:

### Barcode Items
- `hsn_code`: HSN code for the item
- `quantity`: Stock quantity
- `base_price`: Price before tax
- `sgst_percent`: SGST percentage
- `cgst_percent`: CGST percentage
- `total_price`: Auto-calculated final price

### Loose Items
- Similar GST fields as barcode items
- Enhanced with quantity tracking

### Bills
- `total_sgst`: Total SGST amount
- `total_cgst`: Total CGST amount

### Bill Items
- Complete GST breakdown per item
- HSN code tracking
- Base price and tax amounts

### Admin Details
- `shop_name`: Name of the shop/business
- `address`: Shop address
- `phone_number`: Contact phone number
- `use_credentials`: Boolean flag for authentication requirement
- `username`: Admin username (default: admin)
- `password`: Admin password (default: admin123)

## GST Calculations

### Formula
```
Base Amount = Quantity × Base Price
SGST Amount = Base Amount × SGST%
CGST Amount = Base Amount × CGST%
Final Price = Base Amount + SGST Amount + CGST Amount
```

### Tax Display
- **Inventory**: Shows total price (including tax) to users
- **Billing**: Shows complete breakdown (base + SGST + CGST = final)
- **Receipts**: Professional format with tax summary

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

## Export Features

### Available Export Options
1. **Export All Bills**: Complete bill history
2. **Export Filtered Bills**: Currently displayed bills only
3. **Date Range Export**: Bills within specific date range
4. **Customer-specific Export**: Bills for specific customers

### CSV Format
Enhanced CSV includes:
- Basic bill information
- GST breakdown (SGST, CGST amounts)
- Detailed item information with tax components

## Responsive Design Features

### DPI Scaling
- Automatic detection of screen DPI
- Proportional scaling of all UI elements
- High-resolution display support

### Adaptive Layouts
- QVBoxLayout, QHBoxLayout, QGridLayout for flexibility
- QSizePolicy for proper widget expansion
- Dynamic font and button sizing

### Window Management
- All windows are resizable
- Proper minimum and maximum size constraints
- Centered window positioning

## Migration from Version 1.0

The application automatically migrates existing databases:
- Adds new GST-related columns
- Preserves existing data
- Sets default GST values for existing items
- No manual intervention required

## Customization

### Shop Information
Edit the shop details in `thermal_printer.py`:
```python
self.shop_name = "Your Shop Name"
self.shop_address = "Your Shop Address"
self.shop_phone = "Your Phone Number"
```

### Default GST Rates
Modify default GST rates in `data_base/database.py`:
```python
# Example: 12% GST (6% SGST + 6% CGST)
sgst_percent = 6.0
cgst_percent = 6.0
```

### UI Scaling
Adjust responsive breakpoints in individual window files:
```python
if width < 1200:
    font_size = 10
elif width < 1600:
    font_size = 12
else:
    font_size = 14
```

## Important Notes (v2.1+)

- **Final Price Workflow**: When adding or editing inventory items, you always enter the final price (including GST). The base price is automatically calculated and stored in the database.
- **No setGeometry Warnings**: All windows now use `resize(width, height)` with safe defaults. No more geometry warnings on startup.
- **No Unsupported CSS**: All unsupported Qt stylesheet properties (like `transform`) have been removed. If you see 'Unknown property transform', update your code or dependencies.
- **Bill Print/History Table**: Bills and bill history now show items in a compact table format (Name, Qty, Base, SGST, CGST, Total) matching the printed receipt.
- **Average GST in Summary**: Bill summary now shows average SGST% and CGST% instead of totals.

## Troubleshooting (New)
- **Unknown property transform**: All `transform:` properties have been removed from stylesheets. If you still see this warning, check for dynamic or runtime stylesheet updates in your code.
- **QWindowsWindow::setGeometry warnings**: All `setGeometry` calls have been replaced with `resize`. If you still see this warning, ensure you are not setting window sizes larger than your screen.

## File Structure

```
main.py                       # Enhanced application entry point
billing_tabs/
├── home_dashboard.py         # Responsive main dashboard
├── create_bill.py            # GST-aware bill creation
├── bill_history.py           # Enhanced history with filtering
├── inventory.py              # Complete inventory management
├── thermal_printer.py        # GST receipt printing

data_base/
├── database.py               # Enhanced database with GST schema
├── billing.db                # SQLite database (auto-created/migrated)

requirements.txt              # Updated Python dependencies
billing_app.spec              # PyInstaller configuration
README.md                     # This enhanced documentation
```

## License

This enhanced application is provided as-is for educational and commercial use. Modify and distribute according to your needs.

## Support

For technical support, customization requests, or GST compliance questions, contact the development team.

---

**Version 2.0** - Enhanced with GST support, responsive design, and advanced features for modern billing requirements.