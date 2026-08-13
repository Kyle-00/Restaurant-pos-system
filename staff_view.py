"""
Savanna Restaurant POS System - Staff Performance View
=======================================================
Displays waiter statistics: order count and total revenue per waiter.
Separate from Reports – accessible only by Admin.
"""

import tkinter as tk
from tkinter import ttk
from database import Database
from config import Theme, CURRENCY_SYMBOL

class StaffView:
    """Staff performance dashboard showing waiter stats."""

    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user

        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_data()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Staff Performance",
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        refresh_btn = tk.Button(header, text="Refresh",
                               command=self.load_data,
                               bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                               relief="flat", cursor="hand2", padx=15, pady=5)
        refresh_btn.pack(side="right", padx=20)

        # Treeview for waiter stats with scrollbar
        frame = tk.Frame(self.frame, bg=Theme.BG_PRIMARY)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tree_frame = tk.Frame(frame, bg=Theme.BG_PRIMARY)
        tree_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        columns = ("name", "username", "orders", "revenue")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 height=15, style="Custom.Treeview",
                                 yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("name", text="Waiter Name")
        self.tree.heading("username", text="Username")
        self.tree.heading("orders", text="Orders Completed")
        self.tree.heading("revenue", text="Total Revenue")

        self.tree.column("name", width=200)
        self.tree.column("username", width=120)
        self.tree.column("orders", width=120, anchor="center")
        self.tree.column("revenue", width=150, anchor="e")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        stats = Database.get_waiter_stats()
        for row in stats:
            self.tree.insert("", "end", values=(
                row["full_name"],
                row["username"],
                row["order_count"],
                f"{CURRENCY_SYMBOL} {row['total_revenue']:,.2f}"
            ))

    def destroy(self):
        self.frame.destroy()