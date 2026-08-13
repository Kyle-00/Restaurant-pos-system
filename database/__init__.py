"""
Database package – exposes Database class and connection helpers.
"""
from .connection import get_db_connection, get_cursor
from .auth import Database as AuthDB
from .tables import Database as TablesDB
from .menu import Database as MenuDB
from .orders import Database as OrdersDB
from .payments import Database as PaymentsDB
from .reports import Database as ReportsDB
from .activity import Database as ActivityDB
from .settings import Database as SettingsDB
from .seed import Database as SeedDB

# Combine all mixins into one Database class
class Database(
    AuthDB,
    TablesDB,
    MenuDB,
    OrdersDB,
    PaymentsDB,
    ReportsDB,
    ActivityDB,
    SettingsDB,
    SeedDB,
):
    pass

# Also expose the standalone context managers
__all__ = [
    'Database',
    'get_db_connection',
    'get_cursor',
]