"""
Database initialisation and seeding.
"""
import hashlib
import secrets
from .connection import get_db_connection, get_cursor
from config import DEFAULT_CATEGORIES, DEFAULT_ITEMS, DEFAULT_TABLES


class Database:
    @staticmethod
    def init_database():
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    role TEXT NOT NULL DEFAULT 'waiter',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    CHECK (role IN ('admin', 'waiter', 'chef'))
                )
            """)

            # Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER UNIQUE NOT NULL,
                    capacity INTEGER NOT NULL DEFAULT 4,
                    status TEXT NOT NULL DEFAULT 'free',
                    position_x INTEGER DEFAULT 0,
                    position_y INTEGER DEFAULT 0,
                    current_order_id INTEGER,
                    reservation_name TEXT,
                    reservation_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CHECK (status IN ('free', 'occupied', 'reserved'))
                )
            """)

            # Menu categories
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    sort_order INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Menu items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL CHECK (price >= 0),
                    is_vegan INTEGER DEFAULT 0,
                    is_gluten_free INTEGER DEFAULT 0,
                    is_available INTEGER DEFAULT 1,
                    is_featured INTEGER DEFAULT 0,
                    prep_time_minutes INTEGER DEFAULT 15,
                    image_path TEXT,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES menu_categories(id) ON DELETE CASCADE
                )
            """)

            # Orders
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    guest_count INTEGER DEFAULT 1,
                    discount_percent REAL DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
                    discount_amount REAL DEFAULT 0,
                    special_requests TEXT,
                    subtotal REAL DEFAULT 0,
                    tax_amount REAL DEFAULT 0,
                    service_charge REAL DEFAULT 0,
                    total_amount REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (table_id) REFERENCES tables(id),
                    FOREIGN KEY (employee_id) REFERENCES users(id),
                    CHECK (status IN ('pending', 'preparing', 'ready', 'served', 'paid', 'cancelled'))
                )
            """)

            # Order items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    menu_item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    unit_price REAL NOT NULL CHECK (unit_price >= 0),
                    total_price REAL NOT NULL CHECK (total_price >= 0),
                    status TEXT NOT NULL DEFAULT 'pending',
                    notes TEXT,
                    customisations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id),
                    CHECK (status IN ('pending', 'preparing', 'ready', 'served', 'cancelled'))
                )
            """)

            # Payments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    subtotal REAL NOT NULL,
                    discount_amount REAL DEFAULT 0,
                    tax_amount REAL NOT NULL,
                    service_charge REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    amount_paid REAL NOT NULL,
                    change_due REAL DEFAULT 0,
                    payment_method TEXT NOT NULL,
                    split_type TEXT DEFAULT 'none',
                    transaction_reference TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (employee_id) REFERENCES users(id),
                    CHECK (payment_method IN ('cash', 'mpesa', 'card')),
                    CHECK (split_type IN ('none', 'equal', 'by_item', 'by_person'))
                )
            """)

            # Payment splits
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_splits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_id INTEGER NOT NULL,
                    person_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE,
                    CHECK (payment_method IN ('cash', 'mpesa', 'card'))
                )
            """)

            # Pending web orders
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_web_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_id INTEGER,
                    customer_name TEXT,
                    items_json TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Activity log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    table_name TEXT,
                    record_id INTEGER,
                    old_value TEXT,
                    new_value TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_table ON orders(table_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_created ON activity_log(created_at)")

            conn.commit()
            print("Database tables created successfully.")

    @staticmethod
    def seed_demo_data():
        with get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] > 0:
                print("Data already exists. Skipping seeding.")
                return

            # Create admin user only
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256(("admin123" + salt).encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, full_name, email, role)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("admin", password_hash, salt, "System Administrator", "admin@savanna.co.ke", "admin"))

            # Tables
            for table_num, capacity, status in DEFAULT_TABLES:
                x = ((table_num - 1) % 6) * 2
                y = ((table_num - 1) // 6) * 2
                cursor.execute("""
                    INSERT INTO tables (table_number, capacity, status, position_x, position_y)
                    VALUES (?, ?, ?, ?, ?)
                """, (table_num, capacity, status, x, y))

            # Categories
            for i, (name, desc) in enumerate(DEFAULT_CATEGORIES):
                cursor.execute("""
                    INSERT INTO menu_categories (name, description, sort_order)
                    VALUES (?, ?, ?)
                """, (name, desc, i))

            # Items
            for cat_name, item_name, desc, price, vegan, gluten_free in DEFAULT_ITEMS:
                cursor.execute("SELECT id FROM menu_categories WHERE name = ?", (cat_name,))
                row = cursor.fetchone()
                if not row:
                    continue
                cat_id = row[0]
                cursor.execute("""
                    INSERT INTO menu_items (category_id, name, description, price, is_vegan, is_gluten_free)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (cat_id, item_name, desc, price, int(vegan), int(gluten_free)))

            print("Default data seeded successfully.")