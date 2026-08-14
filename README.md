# Savanna POS – Restaurant Point of Sale System

Savanna POS is a complete, offline-first restaurant management system built with Python and Tkinter. It handles everything from table management and order taking to kitchen display, billing, QR code self-ordering, staff tracking, and detailed sales reporting – all in one integrated package.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Installation & Setup](#installation--setup)
- [First Use & Configuration](#first-use--configuration)
- [User Roles & Permissions](#user-roles--permissions)
- [How It Works](#how-it-works)
- [Customization & Configuration](#customization--configuration)
- [Deployment (Production)](#deployment-production)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Development & Contributing](#development--contributing)
- [License](#license)

## Overview

Savanna POS is designed for restaurants that want a modern, efficient, and reliable point-of-sale system without recurring monthly fees. It runs entirely on your own hardware, stores data locally (or on a central server), and gives you full control over your menu, staff, and sales data.

**Who is it for?**

- Small to medium-sized restaurants, cafes, and bars
- Restaurant owners who prefer a one-time setup with no subscriptions
- Developers who want to customise or extend a POS system

## Key Features

### Staff & Roles

- Role-based access – Admins, waiters, and chefs each see only the modules they need.
- Staff management – Add, edit, delete users; change passwords (admin only).
- Clock-in / Clock-out – Track employee working hours (optional).

### Table Management

- Interactive floor plan – Visual layout of all tables with colour-coded status (free, occupied, reserved).
- Click a table to start a new order, view the current order, or proceed to billing.
- Reservations – Reserve a table for a guest.

### Order Taking

- Rich menu browser – Browse categories and items with descriptions and prices.
- Quantity controls – Increase/decrease quantity per item.
- Special requests – Add notes to any item.
- Item customisation – Add extras (e.g., extra cheese, spice level) with additional cost.
- Combo discounts – Automatically apply a discount when a predefined bundle is ordered.
- Discounts – Apply a percentage discount to the entire order.

### Kitchen Display (KDS)

- Live order queue – Shows all pending and preparing orders.
- Chef claiming – A chef can claim an item, assigning it to themselves and automatically setting its status to "preparing".
- Ready notifications – Chefs mark items as ready; waiters see a badge with the count of ready items.
- Prep timer (optional) – Displays expected vs. elapsed time (can be disabled).

### Billing & Payment

- Split bills – Split equally, by item, or by person.
- Payment methods – Cash, M-Pesa, Card/Bank (with transaction code entry).
- Pre-payment bill – Print a detailed invoice showing total due and payment instructions (till number).
- Final receipt – Print a receipt after payment with a full breakdown.
- Any waiter can process payment – No restriction to the original order taker.

### QR Code Table Ordering

- Dynamic QR codes – Each table has a unique QR code linking to a mobile-friendly ordering page.
- Customer self-ordering – Guests scan the code, browse the menu, and place orders directly from their phone.
- Offline queue – Orders are stored locally if the network is down and synced automatically when connectivity returns.
- Two-column responsive layout – Works on phones, tablets, and desktops.

### Reporting & Analytics

- Daily summary – Revenue, order count, average order value, top items, payment methods breakdown.
- Period reports – Weekly or monthly revenue for the last 3, 6, or 12 periods.
- Staff performance – View each waiter's order count and total revenue.
- Activity log – Complete audit trail of all actions (logins, order creation, payments, etc.).

### Administration

- Menu editor – Add, edit, delete categories and items; toggle availability.
- Theme customisation – Change colours via the database (no code changes required).
- Automated backups – Daily database backups (retention: 30 days).
- Migrations – Update the database schema without losing data.

## Technology Stack

| Component | Technology | Purpose |
| --- | --- | --- |
| GUI Framework | Python Tkinter & ttk | Desktop interface |
| Backend Logic | Python 3.14 | Business logic |
| Database | SQLite (embedded) | Local data storage |
| Database Migration | Custom versioned system | Schema upgrades |
| Web Server | Flask | QR ordering pages |
| QR Code Generation | qrcode + Pillow | Generate QR images |
| Dependencies | flask, qrcode, Pillow | All others are standard library |

## Installation & Setup

### 1. Prerequisites

- Python 3.14 or higher – [Download](https://www.python.org/downloads/)
- Git (optional) – to clone the repository
- Internet connection (for initial package installation)

### 2. Get the Source Code

**Option A – Clone with Git:**

```bash
git clone https://github.com/Kyle-00/Restaurant-pos-system.git
cd Restaurant-pos-system
```

**Option B – Download ZIP:**
Download the ZIP from GitHub and extract it.

### 3. Create a Virtual Environment

This isolates the project dependencies from your system Python.

```bash
python -m venv venv
```

Activate the environment:

- Windows (CMD): `venv\Scripts\activate`
- Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
- Linux / macOS: `source venv/bin/activate`

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing, install the core packages manually:

```bash
pip install flask qrcode Pillow
```

### 5. Run the Application

```bash
python main.py
```

The first run will:

- Create the SQLite database file (`restaurant_pos.db`) in the project root.
- Apply all schema migrations.
- Seed the database with a default admin user, 20 tables, and a full menu (if no users exist).

### 6. First Login

- Username: `admin`
- Password: `admin123`

**Important:** Change the admin password immediately after login. Go to Reports → Manage Staff, select the admin user, and click Change Password.

## First Use & Configuration

Once logged in, follow these steps to set up your restaurant:

1. **Customise the Menu**
   - Go to Menu Editor.
   - Edit, add, or delete categories and items.
   - Toggle availability (items become unavailable in the ordering interface).

2. **Add Staff Members**
   - On the login screen, click "Register here" to create new users (waiters, chefs, managers).
   - Or use Reports → Manage Staff to add/edit users (admin only).

3. **Adjust Tax & Till Number**
   - Edit `config.py` to change `TAX_RATE` (default 10%) and `TILL_NUMBER` (appears on bills).

4. **Generate QR Codes for Tables**
   - If you plan to use QR ordering, go to Reports → Settings (if present) or run the QR generation script manually:

     ```python
     from qr_server import generate_all_qr_codes
     import socket
     generate_all_qr_codes(socket.gethostbyname(socket.gethostname()))
     ```

   - Print the QR images from the `qr_codes/` folder and place them on tables.

5. **Test the System**
   - Create a test order, send it to the kitchen, and complete the full payment workflow.
   - Verify the activity log and reports.

## User Roles & Permissions

| Role | Accessible Modules |
| --- | --- |
| Admin | Dashboard, Floor Plan, Orders, Kitchen, Menu, Billing, Reports, Staff, Activity Log |
| Waiter | Dashboard, Floor Plan, Orders, Billing, Menu (view only), My Orders |
| Chef | Dashboard, Kitchen, Menu (view only) |

Permissions are defined in `config.py` and can be extended.

## How It Works

### Order Flow

1. Waiter selects a free table on the floor plan → creates an order.
2. Waiter browses the menu, adds items with quantities, special requests, and optional customisations.
3. Waiter sends the order to the kitchen (status becomes preparing).
4. Chef sees the order on the kitchen display, claims items (optional), and prepares them.
5. Chef marks items as ready when done.
6. Waiter receives a badge notification (count of ready items) on the order management screen.
7. Waiter serves the items (marks them as served).
8. When all items are served, the order status becomes served.
9. Waiter (or any waiter) proceeds to billing, prints a bill, processes payment, and prints a receipt.
10. The order disappears from the active list after the receipt is printed.

### QR Ordering Flow

1. Customer scans the QR code on their table.
2. They see the menu on their phone, add items to cart, and submit the order.
3. The order is stored in the `pending_web_orders` queue.
4. The QR server's sync thread automatically converts pending orders into real POS orders (with a dedicated waiter account).
5. The order appears in the Kitchen Display and Order Management, just like a waiter-created order.

### Payment & Billing

- **Bill:** Printed before payment – shows items, totals, and M-Pesa Till Number.
- **Receipt:** Printed after payment – includes payment method, amount paid, and change.

## Customization & Configuration

### Environment Variables (optional)

You can set the following environment variables to override default paths:

- `DB_PATH` – full path to the database file
- `BACKUPS_DIR` – where backups are stored
- `QR_SERVER_PORT` – port for the QR server (default 5000)

### Changing the Theme

Colours are stored in the `settings` table. You can modify them via a SQLite browser or implement a settings UI (the code includes a Settings tab that can be enabled).

### Adding New Features

The system is modular. To add a new module:

1. Create a new Python file (e.g., `new_module.py`) with a class that takes `(parent, current_user)`.
2. Add a sidebar entry in `main.py` under `build_sidebar()` and a navigation case in `navigate_to()`.
3. Import the new class and handle its destruction.

## Deployment (Production)

### Single-Machine Deployment (Recommended)

This is the simplest setup – the POS runs on one PC that all staff share.

1. Install Python and the project as described in the Installation section.
2. Create a desktop shortcut (Windows):
   - Create `start_pos.bat`:

     ```batch
     @echo off
     cd /d "C:\path\to\your\project"
     call venv\Scripts\activate
     python main.py
     pause
     ```

   - Place it in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` to auto-start on boot.
3. Set the PC to never sleep and lock the screen to prevent unauthorized access.

### Multi-Terminal Setup

For multiple waiters using separate PCs, you need a central database server (PostgreSQL). Contact the developer for migration instructions.

### QR Server in Production

The QR server uses Flask's development server, which is fine for small restaurants. For high traffic, use a production WSGI server like Waitress:

```python
from waitress import serve
serve(app, host='0.0.0.0', port=5000)
```

Replace the `app.run()` call in `qr_server.py` with the above.

## Troubleshooting

| Issue | Solution |
| --- | --- |
| `ModuleNotFoundError: No module named 'flask'` | Activate your virtual environment and run `pip install flask qrcode Pillow`. |
| Database schema errors | Run `python migrations.py` manually (if the auto-migration fails). If all else fails, delete `restaurant_pos.db` and restart – this will erase all data. |
| QR codes not generating | Install Pillow: `pip install Pillow`. Ensure the `qr_codes/` folder exists. |
| QR ordering page shows no menu | The database is empty – seed it via the Menu Editor or run `Database.seed_demo_data()` from a Python shell. |
| Application doesn't start | Check that Python is in your PATH and you are in the correct virtual environment. |
| Receipt printer not working | The system saves receipts as `.txt` files in the `receipts/` folder. You can print them manually or integrate a thermal printer using the `win32print` library. |
| Performance issues | The system is lightweight. If you experience slowness, consider migrating to PostgreSQL and using a faster machine. |

## Project Structure

```text
POS-system/
├── main.py                 # Application entry point
├── config.py               # Constants, default data, payment instructions
├── migrations.py           # Database migration manager
├── auth.py                 # Login/registration UI
├── landing_page.py         # Dashboard and quick navigation
├── table_manager.py        # Floor plan
├── order_system.py         # Order taking
├── kitchen_view.py         # Kitchen display
├── menu_manager.py         # Menu editor
├── billing.py              # Billing & payment
├── receipt.py              # Receipt/bill generation
├── admin_panel.py          # Reports, staff management, period reports
├── staff_view.py           # Staff performance
├── activity_log.py         # Activity log view
├── my_orders.py            # Waiter's order history
├── combo_manager.py        # Combo meal logic
├── employee_scheduler.py   # Shift & clock management
├── settings_manager.py     # Theme settings loader
├── backup_manager.py       # Automated backups
├── qr_server.py            # QR ordering web server
├── styles.py                # Tkinter styling
├── requirements.txt        # Python dependencies
├── database/                # Modular database layer
│   ├── __init__.py
│   ├── connection.py
│   ├── auth.py
│   ├── tables.py
│   ├── menu.py
│   ├── orders.py
│   ├── payments.py
│   ├── reports.py
│   ├── activity.py
│   ├── settings.py
│   └── seed.py
├── templates/
│   └── order.html           # QR ordering page
├── backups/                 # Auto-generated backups
├── qr_codes/                # Generated QR images
├── receipts/                # Saved receipts
└── reports/                 # Exported daily reports
```

## Development & Contributing

### Setting Up for Development

1. Fork the repository on GitHub.
2. Clone your fork and create a new branch for your feature.
3. Make your changes, test thoroughly.
4. Submit a pull request with a clear description of the changes.

### Code Style

- Use PEP 8 for Python code.
- Document new methods with docstrings.
- Keep the UI consistent with the existing Tkinter patterns.

### Development Workflow

- Follow the modular design: add new modules in separate files.
- Extend the Database class with new methods in the appropriate submodule.
- Update the sidebar and navigation in `main.py`.
- Write migration scripts if you add new tables/columns.

### Testing

- Test all workflows manually: order creation, kitchen, billing, QR ordering.
- Test role-based access by logging in as different users.

## License

Licensed by MIT License
