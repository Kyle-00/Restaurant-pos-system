"""
Savanna Restaurant POS System - Landing Page / Dashboard
=========================================================
Modern landing dashboard showing system overview, quick stats, and navigation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from database import Database
from config import Theme, APP_NAME, CURRENCY_SYMBOL, Roles, DB_PATH
from styles import StyleManager, ScrollableFrame

class LandingPage:
    def __init__(self, parent, current_user, on_navigate):
        self.parent = parent
        self.current_user = current_user
        self.on_navigate = on_navigate

        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()

    def update_greeting(self):
        self.greeting_label.config(text=f"Welcome, {self.current_user['full_name']} | Role: {self.current_user['role'].title()}")

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        self.time_label = tk.Label(header, text="",
                                  bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY,
                                  font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.time_label.pack(side="right", padx=20, pady=15)
        self.update_time()

        self.greeting_label = tk.Label(header,
                                       text=f"Welcome, {self.current_user['full_name']} | Role: {self.current_user['role'].title()}",
                                       bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                                       font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.greeting_label.pack(side="right", padx=20, pady=15)

        scroll_frame = ScrollableFrame(self.frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        content = scroll_frame.scrollable_frame

        # Stats Row
        stats_frame = tk.Frame(content, bg=Theme.BG_PRIMARY)
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_data = self.get_today_stats()
        stat_configs = [
            ("Today's Revenue", f"{CURRENCY_SYMBOL} {stats_data['revenue']:,.2f}", Theme.ACCENT_SUCCESS),
            ("Active Orders", str(stats_data['active_orders']), Theme.ACCENT_PRIMARY),
            ("Tables Occupied", f"{stats_data['occupied']}/{stats_data['total_tables']}", Theme.ACCENT_WARNING),
            ("Orders Completed", str(stats_data['completed']), Theme.ACCENT_SECONDARY)
        ]
        for title, value, color in stat_configs:
            card = self.create_stat_card(stats_frame, title, value, color)
            card.pack(side="left", fill="both", expand=True, padx=5)

        # Clock‑in/out section for waiters and chefs
        role = self.current_user["role"]
        if role in [Roles.WAITER, Roles.CHEF]:
            clock_frame = tk.Frame(content, bg=Theme.BG_SECONDARY, padx=15, pady=10)
            clock_frame.pack(fill="x", pady=(0, 20))

            tk.Label(clock_frame, text="Shift Management", bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_GOLD,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold")).pack(anchor="w")

            self.clock_status_label = tk.Label(clock_frame, text="Status: Not clocked in", bg=Theme.BG_SECONDARY,
                                               fg=Theme.TEXT_SECONDARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
            self.clock_status_label.pack(anchor="w", pady=(5, 5))

            self.clock_btn = tk.Button(clock_frame, text="Clock In", command=self.toggle_clock,
                                      bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                                      font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                                      relief="flat", cursor="hand2", padx=10, pady=3)
            self.clock_btn.pack(anchor="w")

            self.update_clock_status()

        # Navigation Modules
        modules_frame = tk.Frame(content, bg=Theme.BG_PRIMARY)
        modules_frame.pack(fill="x", pady=20)
        tk.Label(modules_frame, text="Quick Navigation",
                bg=Theme.BG_PRIMARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", pady=(0, 15))
        modules_grid = tk.Frame(modules_frame, bg=Theme.BG_PRIMARY)
        modules_grid.pack(fill="x")

        modules = []
        if role in [Roles.ADMIN, Roles.WAITER]:
            modules.append(("Table Floor Plan", "Manage tables and take orders", "tables", Theme.TABLE_FREE))
            modules.append(("Order Management", "View and manage active orders", "orders", Theme.ACCENT_PRIMARY))
            modules.append(("Billing & Payment", "Process payments and split bills", "billing", Theme.ACCENT_SUCCESS))
            if role == Roles.WAITER:
                modules.append(("My Orders", "View your order history", "my_orders", Theme.ACCENT_SECONDARY))
        if role in [Roles.ADMIN, Roles.CHEF]:
            modules.append(("Kitchen Display", "Live order queue for chefs", "kitchen", Theme.ACCENT_SUCCESS))
        if role in [Roles.ADMIN, Roles.WAITER, Roles.CHEF]:
            modules.append(("Menu Editor", "Add and edit menu items", "menu", Theme.ACCENT_GOLD))
        if role == Roles.ADMIN:
            modules.append(("Sales Reports", "Daily analytics and charts", "reports", Theme.ACCENT_SECONDARY))
            modules.append(("Staff Performance", "Monitor waiter stats", "staff", Theme.ACCENT_PRIMARY))

        for i, (title, desc, nav_key, color) in enumerate(modules):
            btn = self.create_module_button(modules_grid, title, desc, nav_key, color)
            btn.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")
        for i in range(3):
            modules_grid.grid_columnconfigure(i, weight=1)

    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=Theme.BG_SECONDARY, padx=20, pady=15)
        card.configure(highlightbackground=color, highlightthickness=2)
        tk.Label(card, text=title, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w")
        tk.Label(card, text=value, bg=Theme.BG_SECONDARY, fg=color,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XL, "bold")).pack(anchor="w", pady=(5, 0))
        return card

    def create_module_button(self, parent, title, description, nav_key, color):
        btn_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY, padx=20, pady=20)
        btn_frame.configure(highlightbackground=color, highlightthickness=2)
        bar = tk.Frame(btn_frame, bg=color, height=4)
        bar.pack(fill="x", pady=(0, 15))
        tk.Label(btn_frame, text=title, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w")
        tk.Label(btn_frame, text=description, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                wraplength=180, justify="left").pack(anchor="w", pady=(5, 15))
        open_btn = tk.Button(btn_frame, text="Open",
                            command=lambda: self.on_navigate(nav_key),
                            bg=color, fg=Theme.TEXT_ON_ACCENT,
                            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                            relief="flat", cursor="hand2", padx=15, pady=5)
        open_btn.pack(anchor="e")
        return btn_frame

    def get_today_stats(self):
        try:
            tables = Database.get_all_tables()
            occupied = sum(1 for t in tables if t["status"] == "occupied")
            user_id = self.current_user["id"]
            role = self.current_user["role"]
            if role == "waiter":
                sales = Database.get_daily_sales_for_waiter(user_id)
            else:
                sales = Database.get_daily_sales()
            summary = sales["summary"]
            active_orders = len(Database.get_active_orders())
            return {
                "revenue": summary.get("total_revenue", 0),
                "active_orders": active_orders,
                "occupied": occupied,
                "total_tables": len(tables),
                "completed": summary.get("total_orders", 0)
            }
        except Exception:
            return {"revenue": 0, "active_orders": 0, "occupied": 0, "total_tables": 20, "completed": 0}

    def update_clock_status(self):
        """Check if user is currently clocked in (no clock‑out since last clock‑in)."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_type FROM clock_events
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (self.current_user["id"],))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == "clock_in":
            self.clock_status_label.config(text="Status: Clocked in", fg=Theme.ACCENT_SUCCESS)
            self.clock_btn.config(text="Clock Out", bg=Theme.ACCENT_DANGER)
        else:
            self.clock_status_label.config(text="Status: Not clocked in", fg=Theme.TEXT_SECONDARY)
            self.clock_btn.config(text="Clock In", bg=Theme.ACCENT_SUCCESS)

    def toggle_clock(self):
        if self.clock_btn.cget("text") == "Clock In":
            Database.clock_in(self.current_user["id"])
            messagebox.showinfo("Clocked In", "You have clocked in.")
        else:
            Database.clock_out(self.current_user["id"])
            messagebox.showinfo("Clocked Out", "You have clocked out.")
        self.update_clock_status()

    def update_time(self):
        now = datetime.now().strftime("%A, %d %B %Y | %I:%M %p")
        self.time_label.config(text=now)
        self.frame.after(1000, self.update_time)

    def destroy(self):
        self.frame.destroy()