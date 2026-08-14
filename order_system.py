"""
Savanna Restaurant POS System - Order Management
=================================================
Complete order taking interface with menu browsing, quantity management,
discount application, special requests, and order status tracking.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime
from database import Database
from config import Theme, CURRENCY_SYMBOL
from styles import StyleManager, ScrollableFrame
from combo_manager import ComboManager


class OrderSystem:
    def __init__(self, parent, current_user, on_navigate=None):
        self.parent = parent
        self.current_user = current_user
        self.on_navigate = on_navigate
        self.current_order = None
        self.current_order_items = []

        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_active_orders()
        self.schedule_refresh()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Order Management",
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        # Ready badge
        self.badge_frame = tk.Frame(header, bg=Theme.ACCENT_SUCCESS, padx=2, pady=1)
        self.badge_frame.pack(side="left", padx=10)
        self.badge_label = tk.Label(self.badge_frame, text="",
                                   bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                                   font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                                   padx=4, pady=1)
        self.badge_label.pack()
        self.badge_frame.pack_forget()

        self.order_var = tk.StringVar()
        self.order_combo = ttk.Combobox(header, textvariable=self.order_var, state="readonly",
                                         width=30, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.order_combo.pack(side="left", padx=20)
        self.order_combo.bind("<<ComboboxSelected>>", self.on_order_selected)

        refresh_btn = tk.Button(header, text="Refresh",
                               command=self.load_active_orders,
                               bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                               relief="flat", cursor="hand2", padx=15, pady=5)
        refresh_btn.pack(side="right", padx=10)

        content = tk.Frame(self.frame, bg=Theme.BG_PRIMARY)
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Menu (2-column grid)
        menu_frame = tk.Frame(content, bg=Theme.BG_SECONDARY, width=450)
        menu_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        menu_frame.pack_propagate(False)

        tk.Label(menu_frame, text="Menu",
                bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=10, pady=10)

        self.cat_var = tk.StringVar(value="All")
        cat_frame = tk.Frame(menu_frame, bg=Theme.BG_SECONDARY)
        cat_frame.pack(fill="x", padx=10, pady=(0, 10))
        categories = ["All"] + [c["name"] for c in Database.get_all_categories()]
        cat_combo = ttk.Combobox(cat_frame, textvariable=self.cat_var, values=categories,
                                state="readonly", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        cat_combo.pack(fill="x")
        cat_combo.bind("<<ComboboxSelected>>", self.load_menu_items)

        menu_scroll = ScrollableFrame(menu_frame)
        menu_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        self.menu_container = menu_scroll.scrollable_frame
        self.menu_container.columnconfigure(0, weight=1)
        self.menu_container.columnconfigure(1, weight=1)

        # Right: Current Order
        order_frame = tk.Frame(content, bg=Theme.BG_SECONDARY, width=400)
        order_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        order_frame.pack_propagate(False)

        order_header = tk.Frame(order_frame, bg=Theme.BG_TERTIARY, padx=10, pady=10)
        order_header.pack(fill="x")
        self.order_title = tk.Label(order_header, text="Select an order",
                                   bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                                   font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"))
        self.order_title.pack(side="left")
        self.order_status_label = tk.Label(order_header, text="",
                                    bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.order_status_label.pack(side="right")

        # Order items treeview – height=1, wider columns
        tree_frame = tk.Frame(order_frame, bg=Theme.BG_SECONDARY)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=3)

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        columns = ("item", "qty", "price", "total", "status", "chef")
        self.items_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                      height=1, style="Custom.Treeview",
                                      yscrollcommand=v_scroll.set,
                                      xscrollcommand=h_scroll.set)
        self.items_tree.pack(side="left", fill="both", expand=True)
        v_scroll.config(command=self.items_tree.yview)
        h_scroll.config(command=self.items_tree.xview)

        self.items_tree.heading("item", text="Item")
        self.items_tree.heading("qty", text="Qty")
        self.items_tree.heading("price", text="Unit Price")
        self.items_tree.heading("total", text="Total")
        self.items_tree.heading("status", text="Status")
        self.items_tree.heading("chef", text="Chef")

        # Wider columns for better readability
        self.items_tree.column("item", width=180)
        self.items_tree.column("qty", width=40, anchor="center")
        self.items_tree.column("price", width=80, anchor="e")
        self.items_tree.column("total", width=80, anchor="e")
        self.items_tree.column("status", width=70, anchor="center")
        self.items_tree.column("chef", width=80, anchor="center")

        # Special requests entry – minimal padding
        req_frame = tk.Frame(order_frame, bg=Theme.BG_SECONDARY, padx=10, pady=3)
        req_frame.pack(fill="x")
        tk.Label(req_frame, text="Special Requests:",
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w")
        self.notes_entry = tk.Entry(req_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                   insertbackground=Theme.TEXT_PRIMARY,
                                   font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                                   relief="flat")
        self.notes_entry.pack(fill="x", pady=(0, 3))

        # Action buttons – reduced padding
        action_frame = tk.Frame(order_frame, bg=Theme.BG_SECONDARY, padx=10, pady=3)
        action_frame.pack(fill="x")
        tk.Button(action_frame, text="Add", command=self.add_selected_item_from_tree,
                 bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                 relief="flat", padx=6, pady=2).pack(side="left", padx=2)
        tk.Button(action_frame, text="Remove", command=self.remove_selected_item,
                 bg=Theme.ACCENT_DANGER, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                 relief="flat", padx=6, pady=2).pack(side="left", padx=2)
        tk.Button(action_frame, text="Discount", command=self.apply_discount,
                 bg=Theme.ACCENT_WARNING, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                 relief="flat", padx=6, pady=2).pack(side="left", padx=2)
        tk.Button(action_frame, text="Serve", command=self.serve_selected_item,
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                 relief="flat", padx=6, pady=2).pack(side="left", padx=2)
        tk.Button(action_frame, text="Mark Order Served", command=self.mark_order_served,
                 bg=Theme.ACCENT_GOLD, fg=Theme.BG_PRIMARY,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                 relief="flat", padx=6, pady=2).pack(side="left", padx=2)

        # Totals frame – minimal padding, ensure it stays at bottom
        totals_frame = tk.Frame(order_frame, bg=Theme.BG_TERTIARY, padx=10, pady=2)
        totals_frame.pack(fill="x", side="bottom")
        self.subtotal_label = tk.Label(totals_frame, text=f"Subtotal: {CURRENCY_SYMBOL} 0.00",
                                      bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY,
                                      font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.subtotal_label.pack(anchor="e")
        self.discount_label = tk.Label(totals_frame, text=f"Discount: {CURRENCY_SYMBOL} 0.00",
                                      bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_WARNING,
                                      font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.discount_label.pack(anchor="e")
        self.total_label = tk.Label(totals_frame, text=f"TOTAL: {CURRENCY_SYMBOL} 0.00",
                                    bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_PRIMARY,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"))
        self.total_label.pack(anchor="e", pady=(2, 0))

        # Bottom buttons – minimal padding
        bottom_frame = tk.Frame(order_frame, bg=Theme.BG_SECONDARY, padx=10, pady=3)
        bottom_frame.pack(fill="x", side="bottom")
        tk.Button(bottom_frame, text="Send to Kitchen", command=self.send_to_kitchen,
                 bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                 relief="flat", cursor="hand2", padx=8, pady=2).pack(side="left", padx=2)
        tk.Button(bottom_frame, text="Go to Payment", command=self.go_to_payment,
                 bg=Theme.ACCENT_GOLD, fg=Theme.BG_PRIMARY,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                 relief="flat", cursor="hand2", padx=8, pady=2).pack(side="right", padx=2)

        self.load_menu_items()

    def load_active_orders(self):
        orders = Database.get_active_orders()
        self.order_combo["values"] = [f"Order #{o['id']} - Table {o['table_number']} ({o['status']})" for o in orders]
        if orders:
            self.order_combo.current(0)
            self.on_order_selected(None)

        ready_count = 0
        if self.current_order:
            items = Database.get_order_items(self.current_order["id"])
            ready_count = sum(1 for i in items if i["status"] == "ready")
        if ready_count > 0:
            self.badge_label.config(text=str(ready_count))
            self.badge_frame.pack(side="left", padx=10)
        else:
            self.badge_frame.pack_forget()

    def on_order_selected(self, event):
        selection = self.order_var.get()
        if not selection:
            return
        order_id = int(selection.split("#")[1].split(" -")[0])
        self.current_order = Database.get_order_by_id(order_id)
        if self.current_order:
            self.order_title.config(text=f"Order #{order_id} - Table {self.current_order['table_number']}")
            self.order_status_label.config(text=self.current_order['status'].upper())
            self.load_order_items()

    def load_order_items(self):
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        if not self.current_order:
            return
        items = Database.get_order_items_with_chef(self.current_order["id"])
        self.current_order_items = items
        for item in items:
            cust = item.get("customisations", [])
            cust_str = ", ".join([f"{c['name']} (+{c['price_extra']})" for c in cust]) if cust else ""
            display_name = item["item_name"] + (f" ({cust_str})" if cust_str else "")
            chef_name = item.get("chef_name") or ""
            self.items_tree.insert("", "end", values=(
                display_name,
                item["quantity"],
                f"{CURRENCY_SYMBOL} {item['unit_price']:,.2f}",
                f"{CURRENCY_SYMBOL} {item['total_price']:,.2f}",
                item["status"].upper(),
                chef_name
            ), tags=(str(item["id"]),))
        self.update_totals_display()

        # Combo check
        order_items = [(i["menu_item_id"], i["quantity"]) for i in items]
        combo_id, discount = ComboManager.find_matching_combo(order_items)
        if combo_id and discount > self.current_order.get("discount_percent", 0):
            Database.apply_discount(self.current_order["id"], discount)
            self.current_order = Database.get_order_by_id(self.current_order["id"])
            self.update_totals_display()
            messagebox.showinfo("Combo Applied", f"Combo discount of {discount}% applied!")

        ready_count = sum(1 for i in items if i["status"] == "ready")
        if ready_count > 0:
            self.badge_label.config(text=str(ready_count))
            self.badge_frame.pack(side="left", padx=10)
        else:
            self.badge_frame.pack_forget()

    def update_totals_display(self):
        if not self.current_order:
            return
        order = Database.get_order_by_id(self.current_order["id"])
        self.subtotal_label.config(text=f"Subtotal: {CURRENCY_SYMBOL} {order['subtotal']:,.2f}")
        self.discount_label.config(text=f"Discount: {CURRENCY_SYMBOL} {order['discount_amount']:,.2f}")
        self.total_label.config(text=f"TOTAL: {CURRENCY_SYMBOL} {order['total_amount']:,.2f}")

    def load_menu_items(self, event=None):
        for widget in self.menu_container.winfo_children():
            widget.destroy()
        category = self.cat_var.get()
        if category == "All":
            items = Database.get_all_menu_items_with_unavailable()
        else:
            cats = Database.get_all_categories()
            cat_id = next((c["id"] for c in cats if c["name"] == category), None)
            items = Database.get_menu_items_by_category_unavailable(cat_id) if cat_id else []
        row = 0
        col = 0
        for item in items:
            card = self.create_menu_item_card(item)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            col += 1
            if col > 1:
                col = 0
                row += 1

    def create_menu_item_card(self, item):
        card = tk.Frame(self.menu_container, bg=Theme.BG_TERTIARY, padx=8, pady=8)
        card.configure(highlightbackground=Theme.ACCENT_SECONDARY, highlightthickness=1)

        name_frame = tk.Frame(card, bg=Theme.BG_TERTIARY)
        name_frame.pack(fill="x")
        if not item["is_available"]:
            tk.Label(name_frame, text="[UNAVAILABLE]",
                    bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_DANGER,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left", padx=2)
            tk.Label(name_frame, text=item["name"],
                    bg=Theme.BG_TERTIARY, fg=Theme.TEXT_MUTED,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold")).pack(side="left")
        else:
            tk.Label(name_frame, text=item["name"],
                    bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold")).pack(side="left")

        tk.Label(card, text=f"{CURRENCY_SYMBOL} {item['price']:,.2f}",
                bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_GOLD if item["is_available"] else Theme.TEXT_MUTED,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold")).pack(anchor="w")

        if item["description"]:
            tk.Label(card, text=item["description"],
                    bg=Theme.BG_TERTIARY, fg=Theme.TEXT_MUTED,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                    wraplength=150, justify="left").pack(anchor="w", pady=(2,5))

        controls = tk.Frame(card, bg=Theme.BG_TERTIARY)
        controls.pack(fill="x", pady=2)
        qty_label = tk.Label(controls, text="0", bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        tk.Button(controls, text="-", command=lambda i=item, lbl=qty_label: self.adjust_qty_from_card(i, -1, lbl),
                 bg=Theme.ACCENT_DANGER, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                 relief="flat", width=2, padx=1, pady=1).pack(side="left", padx=1)
        qty_label.pack(side="left", padx=5)
        tk.Button(controls, text="+", command=lambda i=item, lbl=qty_label: self.adjust_qty_from_card(i, 1, lbl),
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                 relief="flat", width=2, padx=1, pady=1).pack(side="left", padx=1)

        card.item_data = item
        card.qty_label = qty_label
        card.bind("<Button-1>", lambda e, i=item: self.select_menu_item(i))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, i=item: self.select_menu_item(i))
        return card

    def adjust_qty_from_card(self, item, delta, qty_label):
        current = int(qty_label.cget("text"))
        new_qty = max(0, current + delta)
        qty_label.config(text=str(new_qty))

    def select_menu_item(self, item):
        self.selected_menu_item = item
        for child in self.menu_container.winfo_children():
            child.configure(bg=Theme.BG_TERTIARY)
        for child in self.menu_container.winfo_children():
            if hasattr(child, 'item_data') and child.item_data['id'] == item['id']:
                child.configure(bg=Theme.ACCENT_SECONDARY)
                break

    def add_selected_item_from_tree(self):
        if not hasattr(self, 'selected_menu_item') or not self.selected_menu_item:
            messagebox.showwarning("No Item Selected", "Click a menu item first.")
            return
        if not self.selected_menu_item["is_available"]:
            messagebox.showwarning("Item Unavailable", "This item is currently not available.")
            return
        if not self.current_order:
            messagebox.showwarning("No Order", "Please select an active order first.")
            return
        qty = 1
        for child in self.menu_container.winfo_children():
            if hasattr(child, 'item_data') and child.item_data['id'] == self.selected_menu_item['id']:
                qty = int(child.qty_label.cget("text"))
                break
        if qty == 0:
            messagebox.showwarning("Zero Quantity", "Please increase quantity using the +/- buttons.")
            return

        notes = self.notes_entry.get().strip()
        customisations = []
        cust_options = Database.get_customisations_for_item(self.selected_menu_item["id"])
        if cust_options:
            selection_window = tk.Toplevel(self.frame)
            selection_window.title("Customise Item")
            selection_window.configure(bg=Theme.BG_SECONDARY)
            selection_window.geometry("300x200")
            tk.Label(selection_window, text="Select extras:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY).pack(pady=10)
            vars_list = []
            for c in cust_options:
                var = tk.IntVar()
                cb = tk.Checkbutton(selection_window, text=f"{c['name']} (+{c['price_extra']} KSh)",
                                   variable=var, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                                   selectcolor=Theme.BG_INPUT)
                cb.pack(anchor="w", padx=20)
                vars_list.append((var, c))
            def confirm():
                for var, c in vars_list:
                    if var.get():
                        customisations.append({"name": c["name"], "price_extra": c["price_extra"]})
                selection_window.destroy()
            tk.Button(selection_window, text="Confirm", command=confirm,
                     bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT).pack(pady=10)
            self.frame.wait_window(selection_window)

        try:
            Database.add_order_item(self.current_order["id"], self.selected_menu_item["id"], qty, notes, customisations)
            Database.log_activity(self.current_user["id"], "ADD_ITEM", "order_items", 
                                self.current_order["id"], new_value=self.selected_menu_item["name"])
            for child in self.menu_container.winfo_children():
                if hasattr(child, 'item_data') and child.item_data['id'] == self.selected_menu_item['id']:
                    child.qty_label.config(text="0")
                    break
            self.load_order_items()
            messagebox.showinfo("Added", f"Added {qty}x {self.selected_menu_item['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def remove_selected_item(self):
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item in the order list to remove.")
            return
        item_id = int(self.items_tree.item(selection[0], "tags")[0])
        if messagebox.askyesno("Confirm Remove", "Remove this item from the order?"):
            try:
                Database.remove_order_item(item_id)
                self.load_order_items()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove item: {str(e)}")

    def serve_selected_item(self):
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to mark as served.")
            return
        item_id = int(self.items_tree.item(selection[0], "tags")[0])
        for item in self.current_order_items:
            if item["id"] == item_id:
                if item["status"] == "served":
                    messagebox.showinfo("Already Served", "This item is already marked as served.")
                    return
                if item["status"] != "ready":
                    messagebox.showwarning("Cannot Serve", "Item must be 'ready' before serving.")
                    return
                break
        if messagebox.askyesno("Confirm Serve", "Mark this item as served?"):
            try:
                Database.update_order_item_status(item_id, "served")
                Database.log_activity(self.current_user["id"], "ITEM_SERVED", "order_items", item_id)
                self.load_order_items()
                self.update_order_status_after_serve()
                messagebox.showinfo("Served", "Item marked as served.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update item: {str(e)}")

    def mark_order_served(self):
        if not self.current_order:
            messagebox.showwarning("No Order", "Please select an order first.")
            return
        items = Database.get_order_items(self.current_order["id"])
        ready_items = [i for i in items if i["status"] == "ready"]
        if not ready_items:
            messagebox.showinfo("No Ready Items", "There are no ready items to serve.")
            return
        if messagebox.askyesno("Confirm Serve Order", f"Mark {len(ready_items)} ready item(s) as served?"):
            try:
                for item in ready_items:
                    Database.update_order_item_status(item["id"], "served")
                self.load_order_items()
                self.update_order_status_after_serve()
                Database.log_activity(self.current_user["id"], "ORDER_SERVED", "orders", self.current_order["id"])
                messagebox.showinfo("Served", "Order items marked as served.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to serve items: {str(e)}")

    def update_order_status_after_serve(self):
        if not self.current_order:
            return
        items = Database.get_order_items(self.current_order["id"])
        all_served = all(i["status"] in ("served", "cancelled") for i in items)
        if all_served:
            Database.update_order_status(self.current_order["id"], "served")
            self.load_active_orders()
            self.order_status_label.config(text="SERVED")

    def apply_discount(self):
        if not self.current_order:
            messagebox.showwarning("No Order", "Please select an order first.")
            return
        discount = simpledialog.askinteger("Discount", "Enter discount percentage (0-100):",
                                          minvalue=0, maxvalue=100)
        if discount is not None:
            try:
                Database.apply_discount(self.current_order["id"], discount)
                self.load_order_items()
                messagebox.showinfo("Discount Applied", f"{discount}% discount applied.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply discount: {str(e)}")

    def send_to_kitchen(self):
        if not self.current_order:
            messagebox.showwarning("No Order", "Please select an order first.")
            return
        try:
            Database.update_order_status(self.current_order["id"], "preparing")
            for item in self.current_order_items:
                if item["status"] == "pending":
                    Database.update_order_item_status(item["id"], "preparing")
            Database.log_activity(self.current_user["id"], "SEND_KITCHEN", "orders", self.current_order["id"])
            messagebox.showinfo("Sent", "Order sent to kitchen successfully!")
            self.load_order_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send to kitchen: {str(e)}")

    def go_to_payment(self):
        if self.on_navigate:
            self.on_navigate("billing")

    def schedule_refresh(self):
        self.load_active_orders()
        self.frame.after(10000, self.schedule_refresh)

    def destroy(self):
        self.frame.destroy()