"""
Savanna Restaurant POS System - Activity Log
=============================================
Displays recent system activity with full timestamps and descriptions.
Accessible only to Admin/Manager.
"""

import tkinter as tk
from tkinter import ttk
from database import Database
from config import Theme


class ActivityLog:
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user

        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_activity()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Activity Log",
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        refresh_btn = tk.Button(header, text="Refresh",
                               command=self.load_activity,
                               bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                               relief="flat", cursor="hand2", padx=15, pady=5)
        refresh_btn.pack(side="right", padx=20)

        # Treeview with scrollbar
        tree_frame = tk.Frame(self.frame, bg=Theme.BG_PRIMARY)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        columns = ("time", "user", "action", "details")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 height=15, style="Custom.Treeview",
                                 yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("time", text="Timestamp")
        self.tree.heading("user", text="User")
        self.tree.heading("action", text="Action")
        self.tree.heading("details", text="Details")

        self.tree.column("time", width=160)
        self.tree.column("user", width=150)
        self.tree.column("action", width=120)
        self.tree.column("details", width=350)

    def load_activity(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        activities = Database.get_recent_activity(100)
        for act in activities:
            time_str = act["created_at"][:19] if act["created_at"] else ""
            action = act["action"]
            record = act.get("record_id", "")
            table = act.get("table_name", "")
            if action == "LOGIN":
                desc = "User logged in"
            elif action == "LOGOUT":
                desc = "User logged out"
            elif action == "CREATE_ORDER":
                desc = f"Created order #{record}"
            elif action == "ADD_ITEM":
                desc = f"Added item to order #{record}"
            elif action == "PAYMENT":
                desc = f"Payment processed for order #{record}"
            elif action == "SEND_KITCHEN":
                desc = f"Order #{record} sent to kitchen"
            elif action == "ITEM_READY":
                desc = f"Item #{record} marked ready"
            elif action == "START_PREP":
                desc = f"Started preparing item #{record}"
            elif action == "WEB_ORDER":
                desc = f"Web order from {act.get('new_value', '')}"
            elif action == "ITEM_SERVED":
                desc = f"Item #{record} served"
            elif action == "ORDER_SERVED":
                desc = f"Order #{record} fully served"
            else:
                desc = f"{action} on {table} #{record}"
            self.tree.insert("", "end", values=(
                time_str,
                act.get("user_name", "System"),
                action,
                desc
            ))

    def destroy(self):
        self.frame.destroy()