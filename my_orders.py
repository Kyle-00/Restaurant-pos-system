"""
Savanna Restaurant POS System - My Orders (Waiter)
===================================================
Displays orders taken by the current waiter, with status filter.
"""

import tkinter as tk
from tkinter import ttk
from database import Database
from config import Theme, CURRENCY_SYMBOL

class MyOrders:
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)
        self.build_ui()
        self.load_orders()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="My Orders",
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        # Filter dropdown
        filter_frame = tk.Frame(header, bg=Theme.BG_TERTIARY)
        filter_frame.pack(side="right", padx=20)
        tk.Label(filter_frame, text="Status:", bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY).pack(side="left")
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                    values=["All", "pending", "preparing", "ready", "served", "paid"],
                                    state="readonly", width=10)
        status_combo.pack(side="left", padx=5)
        status_combo.bind("<<ComboboxSelected>>", self.load_orders)

        refresh_btn = tk.Button(header, text="Refresh", command=self.load_orders,
                               bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                               relief="flat", cursor="hand2", padx=15, pady=5)
        refresh_btn.pack(side="right", padx=10)

        # Treeview with scrollbars
        tree_frame = tk.Frame(self.frame, bg=Theme.BG_PRIMARY)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        columns = ("id", "table", "status", "total", "created_at")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 height=12, style="Custom.Treeview",
                                 yscrollcommand=v_scroll.set,
                                 xscrollcommand=h_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        self.tree.heading("id", text="Order #")
        self.tree.heading("table", text="Table")
        self.tree.heading("status", text="Status")
        self.tree.heading("total", text="Total")
        self.tree.heading("created_at", text="Created At")

        self.tree.column("id", width=60)
        self.tree.column("table", width=60)
        self.tree.column("status", width=80)
        self.tree.column("total", width=100, anchor="e")
        self.tree.column("created_at", width=150)

    def load_orders(self, event=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        status_filter = self.status_var.get()
        if status_filter == "All":
            status_filter = None
        orders = Database.get_orders_for_waiter(self.current_user["id"], status_filter)
        for order in orders:
            self.tree.insert("", "end", values=(
                order["id"],
                order["table_number"],
                order["status"],
                f"{CURRENCY_SYMBOL} {order['total_amount']:,.2f}",
                order["created_at"][:19]
            ))

    def destroy(self):
        self.frame.destroy()