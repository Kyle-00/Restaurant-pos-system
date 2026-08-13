"""
Sales analytics and waiter statistics.
"""
from datetime import datetime, timedelta
from .connection import get_db_connection


class Database:
    @staticmethod
    def get_daily_sales(date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COALESCE(SUM(total_amount), 0) as total_revenue,
                    COALESCE(SUM(tax_amount), 0) as total_tax,
                    COALESCE(SUM(service_charge), 0) as total_service,
                    COALESCE(SUM(discount_amount), 0) as total_discount,
                    COALESCE(AVG(total_amount), 0) as avg_order_value
                FROM orders
                WHERE DATE(created_at) = ? AND status = 'paid'
            """, (date,))
            summary = dict(cursor.fetchone())
            cursor.execute("""
                SELECT 
                    strftime('%H', created_at) as hour,
                    COUNT(*) as orders,
                    COALESCE(SUM(total_amount), 0) as revenue
                FROM orders
                WHERE DATE(created_at) = ? AND status = 'paid'
                GROUP BY hour
                ORDER BY hour
            """, (date,))
            hourly = [dict(row) for row in cursor.fetchall()]
            cursor.execute("""
                SELECT 
                    mi.name,
                    SUM(oi.quantity) as total_qty,
                    SUM(oi.total_price) as total_revenue
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                JOIN orders o ON oi.order_id = o.id
                WHERE DATE(o.created_at) = ? AND o.status = 'paid'
                GROUP BY mi.id
                ORDER BY total_qty DESC
                LIMIT 10
            """, (date,))
            top_items = [dict(row) for row in cursor.fetchall()]
            cursor.execute("""
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    COALESCE(SUM(total_amount), 0) as amount
                FROM payments
                WHERE DATE(created_at) = ?
                GROUP BY payment_method
            """, (date,))
            payment_methods = [dict(row) for row in cursor.fetchall()]
            return {
                "summary": summary,
                "hourly": hourly,
                "top_items": top_items,
                "payment_methods": payment_methods,
                "date": date
            }

    @staticmethod
    def get_daily_sales_for_waiter(waiter_id, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    COALESCE(SUM(total_amount), 0) as total_revenue,
                    COALESCE(SUM(tax_amount), 0) as total_tax,
                    COALESCE(SUM(service_charge), 0) as total_service,
                    COALESCE(SUM(discount_amount), 0) as total_discount,
                    COALESCE(AVG(total_amount), 0) as avg_order_value
                FROM orders
                WHERE DATE(created_at) = ? AND status = 'paid' AND employee_id = ?
            """, (date, waiter_id))
            summary = dict(cursor.fetchone())
            return {"summary": summary, "date": date}

    @staticmethod
    def get_sales_by_period(period_type, num_periods, end_date=None):
        if end_date is None:
            end_date = datetime.now().date()
        results = []
        for i in range(num_periods - 1, -1, -1):
            if period_type == 'week':
                start = end_date - timedelta(days=end_date.weekday() + 1 + i*7)
                end = start + timedelta(days=6)
                label = f"Week of {start.strftime('%b %d')} – {end.strftime('%b %d')}"
            else:  # month
                year = end_date.year
                month = end_date.month - i
                while month <= 0:
                    month += 12
                    year -= 1
                start = datetime(year, month, 1).date()
                if month == 12:
                    end = datetime(year+1, 1, 1).date() - timedelta(days=1)
                else:
                    end = datetime(year, month+1, 1).date() - timedelta(days=1)
                label = start.strftime("%b %Y")
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0) as revenue
                    FROM orders
                    WHERE DATE(created_at) BETWEEN ? AND ? AND status = 'paid'
                """, (start, end))
                revenue = cursor.fetchone()[0]
            results.append({"label": label, "revenue": revenue})
        return results

    @staticmethod
    def get_sales_range(start_date, end_date):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as orders,
                    COALESCE(SUM(total_amount), 0) as revenue
                FROM orders
                WHERE DATE(created_at) BETWEEN ? AND ? AND status = 'paid'
                GROUP BY DATE(created_at)
                ORDER BY date
            """, (start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_top_items_all_time(limit=20):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    mi.name,
                    mc.name as category,
                    SUM(oi.quantity) as total_sold,
                    SUM(oi.total_price) as total_revenue,
                    COUNT(DISTINCT oi.order_id) as times_ordered
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                JOIN menu_categories mc ON mi.category_id = mc.id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.status = 'paid'
                GROUP BY mi.id
                ORDER BY total_sold DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_waiter_stats():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    u.id,
                    u.full_name,
                    u.username,
                    COUNT(o.id) as order_count,
                    COALESCE(SUM(o.total_amount), 0) as total_revenue
                FROM users u
                LEFT JOIN orders o ON u.id = o.employee_id AND o.status = 'paid'
                WHERE u.role = 'waiter'
                GROUP BY u.id
                ORDER BY order_count DESC
            """)
            return [dict(row) for row in cursor.fetchall()]