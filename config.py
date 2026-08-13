"""
Savanna Restaurant POS System - Configuration
==============================================
Central configuration file.
"""

import os

# =============================================================================
# BASE PATHS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "restaurant_pos.db")
RECEIPTS_DIR = os.path.join(BASE_DIR, "receipts")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
QR_CODES_DIR = os.path.join(BASE_DIR, "qr_codes")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# =============================================================================
# CURRENCY CONFIGURATION
# =============================================================================
CURRENCY_SYMBOL = "KSh"
CURRENCY_NAME = "Kenyan Shilling"
CURRENCY_CODE = "KES"
TAX_RATE = 0.10           # 10% VAT
SERVICE_CHARGE_RATE = 0.0 # 0% service charge

# =============================================================================
# PAYMENT INSTRUCTIONS (for bills)
# =============================================================================
TILL_NUMBER = "123456"   

# =============================================================================
# THEME – Spotify‑inspired dark
# =============================================================================
class Theme:
    BG_PRIMARY = "#121212"
    BG_SECONDARY = "#1E1E1E"
    BG_TERTIARY = "#282828"
    BG_INPUT = "#333333"
    ACCENT_PRIMARY = "#1DB954"
    ACCENT_SECONDARY = "#535353"
    ACCENT_SUCCESS = "#1DB954"
    ACCENT_WARNING = "#FFB74D"
    ACCENT_DANGER = "#E74C3C"
    ACCENT_GOLD = "#1DB954"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B3B3B3"
    TEXT_MUTED = "#808080"
    TEXT_ON_ACCENT = "#FFFFFF"
    TABLE_FREE = "#1DB954"
    TABLE_OCCUPIED = "#E74C3C"
    TABLE_RESERVED = "#FFB74D"
    ORDER_PENDING = "#FFB74D"
    ORDER_PREPARING = "#4a8fe0"
    ORDER_READY = "#1DB954"
    ORDER_SERVED = "#9b6bcc"
    ORDER_PAID = "#2d6a4f"
    ORDER_CANCELLED = "#E74C3C"
    FONT_FAMILY = "Arial"
    FONT_FAMILY_MONO = "Courier New"
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 11
    FONT_SIZE_MEDIUM = 13
    FONT_SIZE_LARGE = 16
    FONT_SIZE_XL = 20
    FONT_SIZE_TITLE = 24
    PADDING_SMALL = 5
    PADDING_NORMAL = 10
    PADDING_LARGE = 15
    PADDING_XL = 20

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_NAME = "SAVANNA POS"
APP_FULL_NAME = "Savanna Restaurant POS System"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Modern. Efficient. Reliable."

WINDOW_MIN_WIDTH = 1280
WINDOW_MIN_HEIGHT = 720
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"

KITCHEN_REFRESH_INTERVAL = 5000
ORDER_ALERT_SOUND = True

QR_SERVER_PORT = 5000
QR_SERVER_HOST = "0.0.0.0"

BACKUP_INTERVAL_HOURS = 24
BACKUP_RETENTION_DAYS = 30

# Receipt settings
RECEIPT_WIDTH = 48
RECEIPT_HEADER = """
    SAVANNA RESTAURANT
    ------------------
    Nairobi, Kenya
    Tel: +254 700 000 000
    ------------------
"""
RECEIPT_FOOTER = """
    ------------------
    Thank you for dining with us!
    Karibu Tena!
"""

# =============================================================================
# USER ROLES AND PERMISSIONS
# =============================================================================
class Roles:
    ADMIN = "admin"
    WAITER = "waiter"
    CHEF = "chef"
    ALL = [ADMIN, WAITER, CHEF]

    PERMISSIONS = {
        ADMIN: ["all"],
        WAITER: ["tables", "orders", "billing", "menu_view"],
        CHEF: ["kitchen", "menu_view"],
    }

# =============================================================================
# TABLE CONFIGURATION
# =============================================================================
MAX_TABLES = 30
DEFAULT_TABLE_CAPACITY = 4
FLOOR_PLAN_GRID_COLS = 6
FLOOR_PLAN_GRID_ROWS = 5

# =============================================================================
# PAYMENT METHODS
# =============================================================================
PAYMENT_METHODS = {
    "cash": "Cash",
    "mpesa": "M-Pesa",
    "card": "Card / Bank"
}

SPLIT_TYPES = {
    "none": "No Split",
    "equal": "Split Equally",
    "by_item": "Split by Item",
    "by_person": "Split by Person"
}

# =============================================================================
# DEFAULT DATA (real menu)
# =============================================================================
DEFAULT_CATEGORIES = [
    ("Starters", "Appetizers and small plates"),
    ("Main Course - African", "Hearty Kenyan and East African meals"),
    ("Main Course - International", "Global cuisines"),
    ("Seafood", "Fresh fish, prawns, lobster, and more"),
    ("Pasta", "Italian pasta dishes"),
    ("Pizza", "Wood‑fired pizzas with various toppings"),
    ("Sides", "Accompaniments and extras"),
    ("Desserts", "Sweet treats and pastries"),
    ("Beverages - Hot", "Coffee, tea, and hot drinks"),
    ("Beverages - Cold", "Juices, sodas, and cold refreshments"),
    ("Cocktails & Mocktails", "Signature cocktails and non‑alcoholic mocktails"),
    ("Alcoholic Drinks", "Whisky, tequila, cognac, and other spirits"),
    ("Wines", "Red, white, and rosé wines"),
    ("Specials", "Chef's seasonal specials")
]

DEFAULT_ITEMS = [
    # Starters
    ("Starters", "Samosa (1 pc)", "Crispy Kenyan samosa with chutney", 70, False, True),
    ("Starters", "Samosa (3 pcs)", "Crispy Kenyan samosas with chutney", 200, False, True),
    ("Starters", "Soup of the Day (Bowl)", "Chef's fresh seasonal soup", 350, True, True),
    ("Starters", "Bruschetta (2 pcs)", "Grilled bread with tomato and basil", 550, True, False),
    ("Starters", "Chicken Wings (6 pcs)", "Spicy buffalo wings with dip", 650, False, True),
    ("Starters", "Spring Rolls (4 pcs)", "Vegetable spring rolls with sweet chilli", 480, True, True),

    # Main Course - African
    ("Main Course - African", "Nyama Choma (Half Kg)", "Grilled goat meat with kachumbari", 1200, False, True),
    ("Main Course - African", "Nyama Choma (Full Kg)", "Grilled goat meat with kachumbari", 2200, False, True),
    ("Main Course - African", "Grilled Tilapia (Whole)", "Whole tilapia with ugali and sukuma", 1100, False, True),
    ("Main Course - African", "Chicken Stew", "Tender chicken in tomato sauce with rice", 950, False, False),
    ("Main Course - African", "Beef Stir Fry", "Tender beef with vegetables and rice", 1050, False, False),
    ("Main Course - African", "Vegetable Curry", "Mixed vegetable curry with rice", 750, True, True),
    ("Main Course - African", "Pilau Rice (with meat)", "Aromatic Kenyan pilau with beef", 850, False, False),
    ("Main Course - African", "Ugali & Fish", "Ugali with fried tilapia and sukuma", 1000, False, True),
    ("Main Course - African", "Mukimo", "Traditional mashed potatoes, maize, and beans", 600, True, True),

    # Main Course - International
    ("Main Course - International", "Chef's Special Steak", "Premium beef with truffle sauce", 2500, False, True),
    ("Main Course - International", "Grilled Salmon", "Atlantic salmon with lemon butter", 1800, False, True),
    ("Main Course - International", "Chicken Tikka Masala", "Tandoori chicken with naan and rice", 950, False, False),
    ("Main Course - International", "Spaghetti Bolognese", "Classic Italian pasta with meat sauce", 850, False, True),
    ("Main Course - International", "Vegetable Lasagna", "Layered pasta with vegetables and cheese", 750, True, True),

    # Seafood
    ("Seafood", "Grilled Lobster", "Whole lobster with garlic butter", 3500, False, True),
    ("Seafood", "Prawns Thermidor", "King prawns in creamy sauce", 2800, False, True),
    ("Seafood", "Calamari Fritti", "Crispy fried calamari with marinara", 1200, False, True),
    ("Seafood", "Seafood Platter", "Lobster, prawns, calamari, and fish", 4500, False, True),

    # Pasta
    ("Pasta", "Spaghetti Carbonara", "Classic carbonara with pancetta", 950, False, True),
    ("Pasta", "Fettuccine Alfredo", "Creamy parmesan sauce", 850, True, True),
    ("Pasta", "Penne Arrabbiata", "Spicy tomato sauce with chilli", 750, True, True),
    ("Pasta", "Lasagna", "Layered pasta with meat sauce and cheese", 950, False, True),
    ("Pasta", "Seafood Linguine", "Linguine with mixed seafood", 1200, False, True),

    # Pizza
    ("Pizza", "Margherita", "Tomato, mozzarella, basil", 850, True, True),
    ("Pizza", "Pepperoni", "Tomato, mozzarella, pepperoni", 950, False, True),
    ("Pizza", "Hawaiian", "Tomato, mozzarella, ham, pineapple", 950, False, True),
    ("Pizza", "Seafood Pizza", "Tomato, mozzarella, prawns, calamari", 1200, False, True),
    ("Pizza", "Vegetarian Supreme", "Tomato, mozzarella, mixed vegetables", 850, True, True),

    # Sides
    ("Sides", "Ugali (Plate)", "Traditional Kenyan maize meal", 150, True, True),
    ("Sides", "Sukuma Wiki", "Collard greens with tomatoes", 200, True, True),
    ("Sides", "Chapati (1 pc)", "Soft layered flatbread", 100, True, False),
    ("Sides", "Chips", "Crispy French fries", 250, True, True),
    ("Sides", "Mashed Potatoes", "Creamy mashed potatoes", 250, True, True),
    ("Sides", "Coleslaw", "Fresh cabbage and carrot salad", 180, True, True),
    ("Sides", "Garlic Bread", "Toasted bread with garlic butter", 150, True, True),

    # Desserts
    ("Desserts", "Mandazi (2 pcs)", "Sweet fried dough", 150, True, False),
    ("Desserts", "Fruit Salad", "Seasonal fresh fruits", 400, True, True),
    ("Desserts", "Chocolate Cake", "Rich chocolate layer cake", 550, True, False),
    ("Desserts", "Ice Cream (Scoop)", "Vanilla, chocolate, or strawberry", 300, True, True),
    ("Desserts", "Brownie with Ice Cream", "Warm brownie with vanilla ice cream", 500, True, False),

    # Beverages - Hot
    ("Beverages - Hot", "Kenyan Tea (Pot)", "Authentic chai masala – serves 2", 200, True, True),
    ("Beverages - Hot", "Coffee (Regular)", "Freshly brewed Kenyan coffee", 200, True, True),
    ("Beverages - Hot", "Espresso", "Single shot of espresso", 150, True, True),
    ("Beverages - Hot", "Cappuccino", "Espresso with steamed milk", 250, True, True),
    ("Beverages - Hot", "Hot Chocolate", "Rich hot chocolate with cream", 250, True, True),

    # Beverages - Cold
    ("Beverages - Cold", "Fresh Juice (500ml)", "Orange, mango, or passion", 250, True, True),
    ("Beverages - Cold", "Fresh Juice (1 L)", "Orange, mango, or passion", 450, True, True),
    ("Beverages - Cold", "Soda (Can)", "Coca-Cola, Fanta, Sprite", 150, True, True),
    ("Beverages - Cold", "Soda (Bottle 500ml)", "Coca-Cola, Fanta, Sprite", 200, True, True),
    ("Beverages - Cold", "Bottled Water (500ml)", "Mineral water", 100, True, True),
    ("Beverages - Cold", "Bottled Water (1.5 L)", "Mineral water", 200, True, True),
    ("Beverages - Cold", "Milkshake", "Chocolate, vanilla, or strawberry", 350, True, True),
    ("Beverages - Cold", "Smoothie", "Mixed fruit smoothie", 300, True, True),

    # Cocktails & Mocktails
    ("Cocktails & Mocktails", "Mojito", "White rum, lime, mint, soda water", 550, True, False),
    ("Cocktails & Mocktails", "Virgin Mojito", "Lime, mint, soda water, sugar", 350, True, True),
    ("Cocktails & Mocktails", "Margarita", "Tequila, Cointreau, lime juice", 600, True, False),
    ("Cocktails & Mocktails", "Virgin Mary", "Tomato juice, spices, celery", 350, True, True),
    ("Cocktails & Mocktails", "Pina Colada", "Rum, coconut cream, pineapple juice", 550, True, False),
    ("Cocktails & Mocktails", "Virgin Pina Colada", "Coconut cream, pineapple juice", 350, True, True),
    ("Cocktails & Mocktails", "Cosmopolitan", "Vodka, Cointreau, cranberry, lime", 600, True, False),
    ("Cocktails & Mocktails", "Cucumber Cooler", "Cucumber, lime, mint, soda", 300, True, True),

    # Alcoholic Drinks
    ("Alcoholic Drinks", "Johnnie Walker Black Label (Shot)", "Blended Scotch whisky", 700, False, True),
    ("Alcoholic Drinks", "Johnnie Walker Black Label (Bottle)", "Blended Scotch whisky", 5500, False, True),
    ("Alcoholic Drinks", "Hennessy VS (Shot)", "Cognac", 800, False, True),
    ("Alcoholic Drinks", "Hennessy VS (Bottle)", "Cognac", 6500, False, True),
    ("Alcoholic Drinks", "Don Julio Blanco (Shot)", "Tequila", 650, False, True),
    ("Alcoholic Drinks", "Don Julio Blanco (Bottle)", "Tequila", 5200, False, True),
    ("Alcoholic Drinks", "Jose Cuervo (Shot)", "Tequila", 500, False, True),
    ("Alcoholic Drinks", "Jose Cuervo (Bottle)", "Tequila", 4000, False, True),
    ("Alcoholic Drinks", "Grants Whisky (Shot)", "Blended Scotch whisky", 550, False, True),
    ("Alcoholic Drinks", "Grants Whisky (Bottle)", "Blended Scotch whisky", 4200, False, True),
    ("Alcoholic Drinks", "St. Remy VSOP (Shot)", "French brandy", 600, False, True),
    ("Alcoholic Drinks", "St. Remy VSOP (Bottle)", "French brandy", 4800, False, True),
    ("Alcoholic Drinks", "Gilbeys Gin (Shot)", "London dry gin", 500, False, True),
    ("Alcoholic Drinks", "Gilbeys Gin (Bottle)", "London dry gin", 3800, False, True),

    # Wines
    ("Wines", "Sauvignon Blanc (Glass)", "Crisp white wine – New Zealand", 500, True, True),
    ("Wines", "Sauvignon Blanc (Bottle)", "Crisp white wine – New Zealand", 2500, True, True),
    ("Wines", "Chardonnay (Glass)", "Rich white wine – California", 550, True, True),
    ("Wines", "Chardonnay (Bottle)", "Rich white wine – California", 2800, True, True),
    ("Wines", "Cabernet Sauvignon (Glass)", "Full-bodied red wine – Napa", 600, True, True),
    ("Wines", "Cabernet Sauvignon (Bottle)", "Full-bodied red wine – Napa", 3200, True, True),
    ("Wines", "Merlot (Glass)", "Smooth red wine – Chile", 500, True, True),
    ("Wines", "Merlot (Bottle)", "Smooth red wine – Chile", 2400, True, True),
    ("Wines", "Pinot Noir (Glass)", "Light red wine – Burgundy", 550, True, True),
    ("Wines", "Pinot Noir (Bottle)", "Light red wine – Burgundy", 2800, True, True),
    ("Wines", "Rose (Glass)", "Dry rose – Provence", 500, True, True),
    ("Wines", "Rose (Bottle)", "Dry rose – Provence", 2400, True, True),

    # Specials
    ("Specials", "Lobster Thermidor", "Grilled lobster with creamy sauce", 3500, False, True),
    ("Specials", "Seafood Platter (Large)", "Lobster, prawns, calamari, fish", 4500, False, True),
    ("Specials", "Duck Confit", "Slow-cooked duck leg with vegetables", 2800, False, True),
    ("Specials", "Truffle Risotto", "Creamy risotto with truffle oil", 2200, True, True),
]

DEFAULT_TABLES = [
    (1, 2, "free"), (2, 2, "free"), (3, 4, "free"), (4, 4, "free"),
    (5, 4, "free"), (6, 6, "free"), (7, 6, "free"), (8, 8, "free"),
    (9, 2, "free"), (10, 4, "free"), (11, 4, "free"), (12, 6, "free"),
    (13, 2, "free"), (14, 4, "free"), (15, 8, "free"), (16, 2, "free"),
    (17, 4, "free"), (18, 6, "free"), (19, 4, "free"), (20, 2, "free"),
]