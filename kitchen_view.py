"""
Savanna Restaurant POS System - Kitchen Display System (KDS)
=============================================================
Live order queue for kitchen staff showing pending orders with prep timers.
Auto-refreshes to show new orders in real-time. Also displays the waiter's name.
Shows a number badge when new orders arrive.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Database
from config import Theme, KITCHEN_REFRESH_INTERVAL
from styles import StyleManager, ScrollableFrame

class KitchenView:
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)
        self.order_cards = []
        self.previous_order_count = 0
        self.build_ui()
        self.refresh_orders()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="KITCHEN DISPLAY",
                bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        # New order badge
        self.badge_frame = tk.Frame(header, bg=Theme.ACCENT_DANGER, padx=2, pady=1)
        self.badge_frame.pack(side="left", padx=10)
        self.badge_label = tk.Label(self.badge_frame, text="",
                                   bg=Theme.ACCENT_DANGER, fg=Theme.TEXT_ON_ACCENT,
                                   font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                   padx=4, pady=1)
        self.badge_label.pack()
        self.badge_frame.pack_forget()

        self.status_label = tk.Label(header, text="Live",
                                    bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                                    padx=10, pady=3)
        self.status_label.pack(side="right", padx=20)

        self.stats_label = tk.Label(header, text="",
                                   bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY,
                                   font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.stats_label.pack(side="right", padx=20)

        refresh_btn = tk.Button(header, text="Refresh Now",
                               command=self.refresh_orders,
                               bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                               relief="flat", cursor="hand2", padx=15, pady=5)
        refresh_btn.pack(side="right", padx=10)

        scroll_frame = ScrollableFrame(self.frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.orders_container = scroll_frame.scrollable_frame
        self.schedule_refresh()

    def refresh_orders(self):
        orders = Database.get_kitchen_orders()
        current_count = len(orders)

        if current_count > self.previous_order_count and self.previous_order_count > 0:
            new_orders = current_count - self.previous_order_count
            self.badge_label.config(text=str(new_orders))
            self.badge_frame.pack(side="left", padx=10)
            self.frame.after(5000, lambda: self.badge_frame.pack_forget())
        else:
            self.badge_frame.pack_forget()

        self.previous_order_count = current_count

        for widget in self.orders_container.winfo_children():
            widget.destroy()

        order_groups = {}
        for item in orders:
            order_id = item["order_id"]
            if order_id not in order_groups:
                order_groups[order_id] = {
                    "table_number": item["table_number"],
                    "order_time": item["order_time"],
                    "special_requests": item["special_requests"],
                    "waiter_name": item.get("waiter_name", "Unknown"),
                    "items": []
                }
            order_groups[order_id]["items"].append(item)

        self.stats_label.config(text=f"Pending Orders: {len(order_groups)} | Items: {len(orders)}")

        if not order_groups:
            no_orders = tk.Label(self.orders_container, text="No pending orders",
                                bg=Theme.BG_PRIMARY, fg=Theme.TEXT_MUTED,
                                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XL))
            no_orders.pack(pady=50)
            return

        for order_id, order_data in order_groups.items():
            self.create_order_card(order_id, order_data)

    def create_order_card(self, order_id, order_data):
        card = tk.Frame(self.orders_container, bg=Theme.BG_SECONDARY, padx=15, pady=15)
        card.pack(fill="x", pady=8)
        card.configure(highlightbackground=Theme.ACCENT_WARNING, highlightthickness=2)

        header_frame = tk.Frame(card, bg=Theme.BG_SECONDARY)
        header_frame.pack(fill="x", pady=(0, 10))
        tk.Label(header_frame, text=f"Order #{order_id}",
                bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left")
        tk.Label(header_frame, text=f"Table {order_data['table_number']}",
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold")).pack(side="left", padx=20)
        tk.Label(header_frame, text=f"Waiter: {order_data['waiter_name']}",
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(side="left", padx=20)

        if order_data["special_requests"]:
            req_label = tk.Label(card, text=f"Special: {order_data['special_requests']}",
                                bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_WARNING,
                                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
            req_label.pack(anchor="w", pady=(0, 10))

        for item in order_data["items"]:
            item_frame = tk.Frame(card, bg=Theme.BG_TERTIARY, padx=10, pady=8)
            item_frame.pack(fill="x", pady=2)
            status_colors = {"pending": Theme.ORDER_PENDING, "preparing": Theme.ORDER_PREPARING}
            status_color = status_colors.get(item["status"], Theme.TEXT_MUTED)

            tk.Label(item_frame, text=f"{item['quantity']}x {item['item_name']}",
                    bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold")).pack(side="left")

            # Show chef if assigned
            chef_name = item.get("assigned_chef_name") or "Unassigned"
            tk.Label(item_frame, text=f"Chef: {chef_name}",
                    bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL)).pack(side="left", padx=10)

            status_badge = tk.Label(item_frame, text=item["status"].upper(),
                                   bg=status_color, fg=Theme.TEXT_ON_ACCENT,
                                   font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                   padx=8, pady=2)
            status_badge.pack(side="right")

            # Claim: show if no chef assigned and status is pending or preparing
            if item["status"] in ("pending", "preparing") and not item.get("assigned_chef_id"):
                claim_btn = tk.Button(item_frame, text="Claim",
                                     command=lambda i=item: self.claim_item(i),
                                     bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                                     font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                     relief="flat", cursor="hand2", padx=10)
                claim_btn.pack(side="right", padx=5)
            elif item["status"] == "preparing" and item.get("assigned_chef_id"):
                ready_btn = tk.Button(item_frame, text="Ready",
                                     command=lambda i=item: self.mark_ready(i),
                                     bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                                     font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                     relief="flat", cursor="hand2", padx=10)
                ready_btn.pack(side="right", padx=5)

    def claim_item(self, item):
        try:
            Database.assign_chef_to_order_item(item["id"], self.current_user["id"])
            Database.update_order_item_status(item["id"], "preparing")
            # Update overall order status if still pending
            order = Database.get_order_by_id(item["order_id"])
            if order["status"] == "pending":
                Database.update_order_status(item["order_id"], "preparing")
            Database.log_activity(self.current_user["id"], "CLAIM_ITEM", "order_items", item["id"])
            self.refresh_orders()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_ready(self, item):
        try:
            Database.update_order_item_status(item["id"], "ready")
            Database.log_activity(self.current_user["id"], "ITEM_READY", "order_items", item["id"])
            self.refresh_orders()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def schedule_refresh(self):
        self.refresh_orders()
        self.frame.after(KITCHEN_REFRESH_INTERVAL, self.schedule_refresh)

    def destroy(self):
        self.frame.destroy()