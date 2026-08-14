"""
QR Code Table Ordering Server
-----------------------------
A lightweight Flask web server that serves a customer ordering page.
Generates QR codes for each table and stores pending orders in a queue.
"""

import os
import json
import threading
import sqlite3
import socket
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
import qrcode
from config import DB_PATH, APP_NAME, QR_SERVER_PORT, QR_SERVER_HOST, QR_CODES_DIR, STATIC_DIR, TEMPLATES_DIR

# Ensure directories exist
for d in [QR_CODES_DIR, STATIC_DIR, TEMPLATES_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)
app.config['SECRET_KEY'] = 'dev-key-change-in-production'


def ensure_pending_table():
    """Create the pending_web_orders table if it doesn't exist, and add any missing columns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_web_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER,
            customer_name TEXT,
            items_json TEXT,
            special_requests TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add special_requests column if missing (for older databases)
    try:
        cursor.execute("ALTER TABLE pending_web_orders ADD COLUMN special_requests TEXT")
    except sqlite3.OperationalError:
        pass  # column already exists
    conn.commit()
    conn.close()


def get_menu():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mi.id, mi.name, mi.description, mi.price, mc.name as category, mi.image_path
        FROM menu_items mi
        JOIN menu_categories mc ON mi.category_id = mc.id
        WHERE mi.is_available = 1 AND mc.is_active = 1
        ORDER BY mc.sort_order, mi.sort_order
    """)
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items


@app.route('/')
def index():
    return "Savanna POS QR Ordering Server is running."


@app.route('/table/<int:table_id>')
def table_order(table_id):
    menu = get_menu()
    # Get unique categories from menu items
    categories = sorted(set(item['category'] for item in menu))
    return render_template('order.html', table=table_id, menu=menu, app_name=APP_NAME, categories=categories)


@app.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.get_json()
    table_id = data.get('table_id')
    items = data.get('items')
    customer_name = data.get('customer_name', 'Guest')
    special_requests = data.get('special_requests', '')

    # Ensure table exists and has the special_requests column
    ensure_pending_table()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pending_web_orders (table_id, customer_name, items_json, special_requests) VALUES (?, ?, ?, ?)",
        (table_id, customer_name, json.dumps(items), special_requests)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Order received! We'll prepare it shortly."})


@app.route('/qr_codes/<filename>')
def serve_qr(filename):
    return send_from_directory(QR_CODES_DIR, filename)


def generate_qr_for_table(table_id, host_ip):
    """Generate a QR code image for a table and save it."""
    url = f"http://{host_ip}:{QR_SERVER_PORT}/table/{table_id}"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    try:
        from PIL import Image  # noqa: F401
        img = qr.make_image(fill_color="black", back_color="white")
    except ImportError:
        # Fallback to simple text QR if Pillow not installed
        img = qr.make_image(fill_color="black", back_color="white")
    filename = f"table_{table_id}.png"
    path = os.path.join(QR_CODES_DIR, filename)
    img.save(path)
    return filename


def generate_all_qr_codes(host_ip):
    """Generate QR codes for all tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT table_number FROM tables")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    for t in tables:
        generate_qr_for_table(t, host_ip)


def sync_pending_orders():
    """Periodically process pending web orders and create real orders in the system."""
    from database import Database
    import time
    while True:
        try:
            ensure_pending_table()
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pending_web_orders WHERE status = 'pending' ORDER BY created_at")
            pending = [dict(row) for row in cursor.fetchall()]
            conn.close()

            for p in pending:
                # Create a real order in the system
                table_id = p["table_id"]
                special_requests = p.get("special_requests", "")

                # We need a waiter ID – use first active waiter or admin
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE role = 'waiter' AND is_active = 1 LIMIT 1")
                waiter = cursor.fetchone()
                if not waiter:
                    cursor.execute("SELECT id FROM users WHERE role = 'admin' AND is_active = 1 LIMIT 1")
                    waiter = cursor.fetchone()
                waiter_id = waiter["id"] if waiter else 1
                conn.close()

                # Create order with special request
                order_id = Database.create_order(table_id, waiter_id, 1, special_requests)
                if order_id:
                    items = json.loads(p["items_json"])
                    for itm in items:
                        menu_item_id = itm.get("menu_item_id")
                        qty = itm.get("quantity", 1)
                        Database.add_order_item(order_id, menu_item_id, qty)
                    # Mark processed
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE pending_web_orders SET status = 'processed' WHERE id = ?", (p["id"],))
                    conn.commit()
                    conn.close()
                    # Log activity
                    Database.log_activity(waiter_id, "WEB_ORDER", "orders", order_id, new_value=f"Table {table_id}")
        except Exception as e:
            print(f"Sync error: {e}")
        time.sleep(10)  # every 10 seconds


def start_server(host_ip=None):
    """Start the Flask server and the sync thread."""
    if host_ip is None:
        try:
            host_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            host_ip = "127.0.0.1"
    # Ensure pending_web_orders table exists
    ensure_pending_table()
    # Generate QR codes
    generate_all_qr_codes(host_ip)
    # Start sync thread
    sync_thread = threading.Thread(target=sync_pending_orders, daemon=True)
    sync_thread.start()
    # Start server
    app.run(host=QR_SERVER_HOST, port=QR_SERVER_PORT, debug=False, use_reloader=False)