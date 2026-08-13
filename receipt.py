"""
Savanna Restaurant POS System - Receipt Generator
===================================================
Generates formatted thermal-style receipts for orders and bills.
"""

from datetime import datetime
from database import Database
from config import (
    CURRENCY_SYMBOL, RECEIPT_HEADER, RECEIPT_FOOTER,
    TILL_NUMBER
)

class ReceiptGenerator:
    @staticmethod
    def generate_receipt(order_id):
        order = Database.get_order_by_id(order_id)
        if not order:
            return "Order not found."
        items = Database.get_order_items(order_id)
        payment = Database.get_payment_by_order(order_id)
        lines = []
        width = 48
        lines.append(RECEIPT_HEADER)
        lines.append(f"Receipt #: {order_id}")
        lines.append(f"Table: {order['table_number']}")
        lines.append(f"Date: {order['created_at'][:19]}")
        lines.append(f"Served by: {order['employee_name']}")
        lines.append("-" * width)
        lines.append(f"{'Item':<25} {'Qty':>4} {'Price':>8} {'Total':>8}")
        lines.append("-" * width)
        for item in items:
            name = item["item_name"][:24]
            lines.append(f"{name:<25} {item['quantity']:>4} {item['unit_price']:>8.2f} {item['total_price']:>8.2f}")
        lines.append("-" * width)
        lines.append(f"{'Subtotal:':<38} {order['subtotal']:>8.2f}")
        if order['discount_amount'] > 0:
            lines.append(f"{'Discount:':<38} -{order['discount_amount']:>7.2f}")
        lines.append(f"{'VAT (10%):':<38} {order['tax_amount']:>8.2f}")
        lines.append("-" * width)
        lines.append(f"{'TOTAL:':<32} {CURRENCY_SYMBOL} {order['total_amount']:>8.2f}")
        if payment:
            lines.append("-" * width)
            method_display = {'cash': 'Cash', 'mpesa': 'M-Pesa', 'card': 'Card/Bank'}.get(payment['payment_method'], payment['payment_method'].upper())
            lines.append(f"Payment Method: {method_display}")
            lines.append(f"Amount Paid: {CURRENCY_SYMBOL} {payment['amount_paid']:.2f}")
            if payment['change_due'] > 0:
                lines.append(f"Change: {CURRENCY_SYMBOL} {payment['change_due']:.2f}")
            if payment['transaction_reference']:
                lines.append(f"Transaction Code: {payment['transaction_reference']}")
        lines.append(RECEIPT_FOOTER)
        return "\n".join(lines)

    @staticmethod
    def generate_bill(order_id, include_payment_instructions=True):
        """Generate a pre‑payment bill showing total and payment methods (Till only)."""
        order = Database.get_order_by_id(order_id)
        if not order:
            return "Order not found."
        items = Database.get_order_items(order_id)
        lines = []
        width = 48
        lines.append(RECEIPT_HEADER)
        lines.append(f"Bill #: {order_id}")
        lines.append(f"Table: {order['table_number']}")
        lines.append(f"Date: {order['created_at'][:19]}")
        lines.append(f"Served by: {order['employee_name']}")
        lines.append("-" * width)
        lines.append(f"{'Item':<25} {'Qty':>4} {'Price':>8} {'Total':>8}")
        lines.append("-" * width)
        for item in items:
            name = item["item_name"][:24]
            lines.append(f"{name:<25} {item['quantity']:>4} {item['unit_price']:>8.2f} {item['total_price']:>8.2f}")
        lines.append("-" * width)
        lines.append(f"{'Subtotal:':<38} {order['subtotal']:>8.2f}")
        if order['discount_amount'] > 0:
            lines.append(f"{'Discount:':<38} -{order['discount_amount']:>7.2f}")
        lines.append(f"{'VAT (10%):':<38} {order['tax_amount']:>8.2f}")
        lines.append("-" * width)
        lines.append(f"{'TOTAL DUE:':<32} {CURRENCY_SYMBOL} {order['total_amount']:>8.2f}")
        if include_payment_instructions:
            lines.append("-" * width)
            lines.append("    PAYMENT OPTIONS")
            lines.append(f"    M-Pesa Till Number: {TILL_NUMBER}")
        lines.append(RECEIPT_FOOTER)
        return "\n".join(lines)

    @staticmethod
    def generate_daily_report(date=None):
        from database import Database
        sales = Database.get_daily_sales(date)
        summary = sales["summary"]
        lines = []
        width = 48
        lines.append("    DAILY SALES REPORT")
        lines.append(f"    Date: {sales['date']}")
        lines.append("-" * width)
        lines.append(f"{'Total Orders:':<35} {summary['total_orders']:>10}")
        lines.append(f"{'Total Revenue:':<32} {CURRENCY_SYMBOL} {summary['total_revenue']:>10.2f}")
        lines.append(f"{'Total Tax (VAT):':<32} {CURRENCY_SYMBOL} {summary['total_tax']:>10.2f}")
        lines.append(f"{'Total Discounts:':<32} {CURRENCY_SYMBOL} {summary['total_discount']:>10.2f}")
        lines.append(f"{'Average Order:':<32} {CURRENCY_SYMBOL} {summary['avg_order_value']:>10.2f}")
        lines.append("-" * width)
        lines.append("    TOP SELLING ITEMS")
        lines.append("-" * width)
        for i, item in enumerate(sales["top_items"][:5], 1):
            lines.append(f"{i}. {item['name'][:25]:<25} {item['total_qty']:>3}  {CURRENCY_SYMBOL} {item['total_revenue']:>8.2f}")
        lines.append("-" * width)
        lines.append("    End of Report")
        return "\n".join(lines)