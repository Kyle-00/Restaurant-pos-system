"""
Savanna Restaurant POS System - Table Manager / Floor Plan
==========================================================
Interactive visual floor plan showing all tables with color-coded status.
Clicking a table opens the order window. Supports table reservation and status updates.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from database import Database
from config import Theme, CURRENCY_SYMBOL
from styles import StyleManager

class TableManager:
    """Visual floor plan manager for restaurant tables."""

    def __init__(self, parent, current_user, on_navigate):
        self.parent = parent
        self.current_user = current_user
        self.on_navigate = on_navigate

        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)

        self.table_buttons = {}
        self.build_ui()
        self.refresh_tables()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Floor Plan",
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        legend_frame = tk.Frame(header, bg=Theme.BG_TERTIARY)
        legend_frame.pack(side="right", padx=20)

        legends = [
            ("Free", Theme.TABLE_FREE),
            ("Occupied", Theme.TABLE_OCCUPIED),
            ("Reserved", Theme.TABLE_RESERVED)
        ]

        for label, color in legends:
            item = tk.Frame(legend_frame, bg=Theme.BG_TERTIARY)
            item.pack(side="left", padx=10)

            dot = tk.Label(item, text="  ", bg=color, width=2)
            dot.pack(side="left")
            tk.Label(item, text=label, bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL)).pack(side="left", padx=5)

        refresh_btn = tk.Button(header, text="Refresh",
                               command=self.refresh_tables,
                               bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                               relief="flat", cursor="hand2", padx=15, pady=5)
        refresh_btn.pack(side="right", padx=10)

        self.grid_container = tk.Frame(self.frame, bg=Theme.BG_PRIMARY)
        self.grid_container.pack(fill="both", expand=True, padx=20, pady=20)

    def refresh_tables(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        tables = Database.get_all_tables()

        for i, table in enumerate(tables):
            row = i // 6
            col = i % 6
            self.create_table_card(table, row, col)

        for i in range(6):
            self.grid_container.grid_columnconfigure(i, weight=1, uniform="table")
        for i in range((len(tables) + 5) // 6):
            self.grid_container.grid_rowconfigure(i, weight=1, uniform="table")

    def create_table_card(self, table, row, col):
        status = table["status"]
        status_colors = {
            "free": Theme.TABLE_FREE,
            "occupied": Theme.TABLE_OCCUPIED,
            "reserved": Theme.TABLE_RESERVED,
        }
        color = status_colors.get(status, Theme.TEXT_MUTED)

        card = tk.Frame(self.grid_container, bg=Theme.BG_SECONDARY, padx=10, pady=10)
        card.configure(highlightbackground=color, highlightthickness=3)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        tk.Label(card, text=f"Table {table['table_number']}",
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack()

        tk.Label(card, text=f"Seats: {table['capacity']}",
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(pady=2)

        status_label = tk.Label(card, text=status.upper(),
                               bg=color, fg=Theme.TEXT_ON_ACCENT,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                               padx=8, pady=2)
        status_label.pack(pady=5)

        btn_frame = tk.Frame(card, bg=Theme.BG_SECONDARY)
        btn_frame.pack(pady=5)

        if status == "free":
            order_btn = tk.Button(btn_frame, text="New Order",
                                 command=lambda t=table: self.new_order(t),
                                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                 relief="flat", cursor="hand2", padx=8, pady=2)
            order_btn.pack(side="left", padx=2)

            reserve_btn = tk.Button(btn_frame, text="Reserve",
                                   command=lambda t=table: self.reserve_table(t),
                                   bg=Theme.ACCENT_WARNING, fg=Theme.TEXT_ON_ACCENT,
                                   font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                                   relief="flat", cursor="hand2", padx=8, pady=2)
            reserve_btn.pack(side="left", padx=2)

        elif status == "occupied":
            view_btn = tk.Button(btn_frame, text="View Order",
                                command=lambda t=table: self.view_order(t),
                                bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                relief="flat", cursor="hand2", padx=8, pady=2)
            view_btn.pack(side="left", padx=2)

            bill_btn = tk.Button(btn_frame, text="Bill",
                                command=lambda t=table: self.go_to_billing(t),
                                bg=Theme.ACCENT_GOLD, fg=Theme.BG_PRIMARY,
                                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                relief="flat", cursor="hand2", padx=8, pady=2)
            bill_btn.pack(side="left", padx=2)

        elif status == "reserved":
            activate_btn = tk.Button(btn_frame, text="Activate",
                                    command=lambda t=table: self.activate_table(t),
                                    bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                    relief="flat", cursor="hand2", padx=8, pady=2)
            activate_btn.pack(side="left", padx=2)

            cancel_btn = tk.Button(btn_frame, text="Cancel",
                                  command=lambda t=table: self.cancel_reservation(t),
                                  bg=Theme.ACCENT_DANGER, fg=Theme.TEXT_ON_ACCENT,
                                  font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                                  relief="flat", cursor="hand2", padx=8, pady=2)
            cancel_btn.pack(side="left", padx=2)

    def new_order(self, table):
        guest_count = simpledialog.askinteger("Guest Count", 
                                             f"How many guests for Table {table['table_number']}?",
                                             minvalue=1, maxvalue=table['capacity'])
        if guest_count:
            try:
                order_id = Database.create_order(table["id"], self.current_user["id"], guest_count)
                Database.log_activity(self.current_user["id"], "CREATE_ORDER", "orders", order_id)
                messagebox.showinfo("Order Created", f"Order #{order_id} created for Table {table['table_number']}")
                self.refresh_tables()
                self.on_navigate("orders")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create order: {str(e)}")

    def view_order(self, table):
        if table.get("current_order_id"):
            self.on_navigate("orders")

    def go_to_billing(self, table):
        self.on_navigate("billing")

    def reserve_table(self, table):
        name = simpledialog.askstring("Reservation", "Enter guest name:")
        if name:
            Database.update_table_status(table["id"], "reserved", reservation_name=name)
            Database.log_activity(self.current_user["id"], "RESERVE_TABLE", "tables", table["id"])
            self.refresh_tables()

    def activate_table(self, table):
        Database.update_table_status(table["id"], "free")
        self.new_order(table)

    def cancel_reservation(self, table):
        if messagebox.askyesno("Cancel Reservation", "Cancel this reservation?"):
            Database.update_table_status(table["id"], "free")
            Database.log_activity(self.current_user["id"], "CANCEL_RESERVATION", "tables", table["id"])
            self.refresh_tables()

    def destroy(self):
        self.frame.destroy()