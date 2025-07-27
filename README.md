# QuikBill GST Billing App

A modern, offline desktop billing application with GST support, inventory management, WhatsApp bill sharing, thermal printing, and secure admin credential management. Built with Python and PyQt5 for small businesses and shops in India.

## Features
- Create GST-compliant bills (barcode and loose items)
- Inventory management (add/edit/delete items, categories)
- Bill history with search, filter, and CSV export
- WhatsApp bill sharing (send bill as image)
- Thermal printer support (USB/Serial/Network)
- Admin settings (shop details, credentials, **Gmail for password reset**)
- Customer info autocomplete
- Offline local database (SQLite)
- **Password reset via OTP to admin Gmail**
- Modern, user-friendly UI

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
   - Update shop details, credentials, and **Gmail for password reset**
   - Change password securely
   - Use "Forgot password?" to reset password via OTP sent to Gmail

## Password Reset via Gmail (OTP)
- Set your Gmail address in Admin Settings.
- Enable [2-Step Verification](https://myaccount.google.com/security) on your Google account.
- Generate a [Gmail App Password](https://support.google.com/accounts/answer/185833?hl=en) and enter it in the code (see `billing_tabs/admin_settings.py`, search for `from_email` and `password`).
- To reset your password:
  1. Click "Change Credentials" in Admin Settings.
  2. Click "Forgot password?".
  3. Click "Send OTP". Check your Gmail for the OTP.
  4. Enter the OTP, then set a new password in the next dialog.

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
- **Admin details now include Gmail for password reset**

## Project Structure
- **README.md**: Project overview, features, setup, usage, troubleshooting
- **main.py**: Main entry point
- **billing_tabs/**: All main app modules and UI logic
- **data_base/**: Database and related assets
- **requirements.txt**: Python dependencies

## Troubleshooting
- **WhatsApp not sending?** Increase wait time or focus WhatsApp Web tab
- **Printer not working?** Check drivers and connection
- **Email OTP not sending?**
  - Make sure Gmail and App Password are set up correctly
  - Check for typos in your email/app password
  - See [Google App Password Help](https://support.google.com/accounts/answer/185833?hl=en)

---

For further help, see the README or contact the maintainer.
