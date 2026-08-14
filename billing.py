"""
Savanna Restaurant POS System - Billing & Payment
==================================================
Handles bill splitting, payment processing, and receipt/bill generation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import os
from database import Database
from config import Theme, CURRENCY_SYMBOL, PAYMENT_METHODS, SPLIT_TYPES, RECEIPTS_DIR, TAX_RATE, SERVICE_CHARGE_RATE
from receipt import ReceiptGenerator
from styles import ScrollableFrame


class BillingSystem:
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self.current_order = None
        self.split_people = []
        self.payment_done = False

        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_unpaid_orders()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Billing & Payment",
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        self.order_var = tk.StringVar()
        self.order_combo = ttk.Combobox(header, textvariable=self.order_var, state="readonly",
                                         width=35, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.order_combo.pack(side="left", padx=20)
        self.order_combo.bind("<<ComboboxSelected>>", self.on_order_selected)

        refresh_btn = tk.Button(header, text="Refresh",
                               command=self.load_unpaid_orders,
                               bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                               font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                               relief="flat", cursor="hand2", padx=15, pady=5)
        refresh_btn.pack(side="right", padx=10)

        content = tk.Frame(self.frame, bg=Theme.BG_PRIMARY)
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Bill details
        bill_frame = tk.Frame(content, bg=Theme.BG_SECONDARY, width=450)
        bill_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        bill_frame.pack_propagate(False)

        tk.Label(bill_frame, text="Bill Details",
                bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=10, pady=10)

        columns = ("item", "qty", "price", "total")
        self.bill_tree = ttk.Treeview(bill_frame, columns=columns, show="headings",
                                      height=12, style="Custom.Treeview")
        self.bill_tree.heading("item", text="Item")
        self.bill_tree.heading("qty", text="Qty")
        self.bill_tree.heading("price", text="Unit Price")
        self.bill_tree.heading("total", text="Total")
        self.bill_tree.column("item", width=200)
        self.bill_tree.column("qty", width=50, anchor="center")
        self.bill_tree.column("price", width=80, anchor="e")
        self.bill_tree.column("total", width=80, anchor="e")
        self.bill_tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.totals_frame = tk.Frame(bill_frame, bg=Theme.BG_TERTIARY, padx=15, pady=15)
        self.totals_frame.pack(fill="x", side="bottom")

        self.bill_subtotal = tk.Label(self.totals_frame, text=f"Subtotal: {CURRENCY_SYMBOL} 0.00",
                                     bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY,
                                     font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.bill_subtotal.pack(anchor="e")
        self.bill_discount = tk.Label(self.totals_frame, text=f"Discount: {CURRENCY_SYMBOL} 0.00",
                                     bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_WARNING,
                                     font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.bill_discount.pack(anchor="e")
        self.bill_vat = tk.Label(self.totals_frame, text=f"VAT ({int(TAX_RATE*100)}%): {CURRENCY_SYMBOL} 0.00",
                                 bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY,
                                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.bill_vat.pack(anchor="e")
        self.bill_total = tk.Label(self.totals_frame, text=f"TOTAL: {CURRENCY_SYMBOL} 0.00",
                                    bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_GOLD,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XL, "bold"))
        self.bill_total.pack(anchor="e", pady=(5, 0))

        # Right: Payment panel with scroll
        payment_container = tk.Frame(content, bg=Theme.BG_SECONDARY, width=400)
        payment_container.pack(side="right", fill="both", expand=True, padx=(5, 0))
        payment_container.pack_propagate(False)

        payment_scroll = ScrollableFrame(payment_container)
        payment_scroll.pack(fill="both", expand=True)
        payment_frame = payment_scroll.scrollable_frame
        payment_frame.configure(bg=Theme.BG_SECONDARY)

        tk.Label(payment_frame, text="Payment",
                bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=10, pady=10)

        split_frame = tk.Frame(payment_frame, bg=Theme.BG_SECONDARY, padx=10)
        split_frame.pack(fill="x", pady=5)
        tk.Label(split_frame, text="Split Type:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(side="left")
        self.split_var = tk.StringVar(value="No Split")
        split_combo = ttk.Combobox(split_frame, textvariable=self.split_var,
                                  values=list(SPLIT_TYPES.values()), state="readonly",
                                  font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        split_combo.pack(side="left", padx=10)
        split_combo.bind("<<ComboboxSelected>>", self.on_split_change)
        self.split_details = tk.Frame(payment_frame, bg=Theme.BG_SECONDARY, padx=10)
        self.split_details.pack(fill="x", pady=5)

        method_frame = tk.Frame(payment_frame, bg=Theme.BG_SECONDARY, padx=10)
        method_frame.pack(fill="x", pady=10)
        tk.Label(method_frame, text="Payment Method:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w")
        self.method_var = tk.StringVar(value="cash")
        for key, label in PAYMENT_METHODS.items():
            tk.Radiobutton(method_frame, text=label, variable=self.method_var, value=key,
                          bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                          selectcolor=Theme.BG_INPUT, activebackground=Theme.BG_SECONDARY).pack(anchor="w", pady=2)

        ref_frame = tk.Frame(payment_frame, bg=Theme.BG_SECONDARY, padx=10)
        ref_frame.pack(fill="x", pady=5)
        tk.Label(ref_frame, text="Transaction Code (if non-cash):", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w")
        self.ref_entry = tk.Entry(ref_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                 insertbackground=Theme.TEXT_PRIMARY,
                                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        self.ref_entry.pack(fill="x", pady=5)

        amount_frame = tk.Frame(payment_frame, bg=Theme.BG_SECONDARY, padx=10)
        amount_frame.pack(fill="x", pady=10)
        tk.Label(amount_frame, text="Amount Paid (KSh):", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w")
        self.amount_entry = tk.Entry(amount_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                    insertbackground=Theme.TEXT_PRIMARY,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE),
                                    relief="flat", justify="right")
        self.amount_entry.pack(fill="x", pady=5)

        self.change_label = tk.Label(payment_frame, text=f"Change: {CURRENCY_SYMBOL} 0.00",
                                    bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_SUCCESS,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"))
        self.change_label.pack(anchor="w", padx=10, pady=5)

        btn_frame = tk.Frame(payment_frame, bg=Theme.BG_SECONDARY, padx=10, pady=10)
        btn_frame.pack(fill="x", side="bottom")

        self.payment_btn = tk.Button(btn_frame, text="Process Payment", command=self.process_payment,
                                     bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                                     font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"),
                                     relief="flat", cursor="hand2", padx=20, pady=10)
        self.payment_btn.pack(fill="x", pady=2)

        self.receipt_btn = tk.Button(btn_frame, text="Print Receipt", command=self.print_receipt,
                                     bg=Theme.ACCENT_GOLD, fg=Theme.BG_PRIMARY,
                                     font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                                     relief="flat", cursor="hand2", padx=15, pady=8)
        self.receipt_btn.pack(fill="x", pady=2)
        self.receipt_btn.config(state="disabled")

        tk.Button(btn_frame, text="Print Bill", command=self.print_bill,
                 bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 relief="flat", cursor="hand2", padx=15, pady=8).pack(fill="x", pady=2)

        tk.Button(btn_frame, text="Calculate Change", command=self.calculate_change,
                 bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 relief="flat", cursor="hand2", padx=15, pady=8).pack(fill="x", pady=2)

    def load_unpaid_orders(self):
        orders = Database.get_active_orders()
        self.order_combo["values"] = [f"Order #{o['id']} - Table {o['table_number']} - KSh {o['total_amount']:,.2f}" for o in orders]
        if orders:
            self.order_combo.current(0)
            self.on_order_selected(None)

    def on_order_selected(self, event):
        selection = self.order_var.get()
        if not selection:
            return
        order_id = int(selection.split("#")[1].split(" -")[0])
        self.current_order = Database.get_order_by_id(order_id)
        if self.current_order:
            self.load_bill_items()
            self.update_totals()
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, f"{self.current_order['total_amount']:.2f}")
            self.calculate_change()
            self.payment_done = False
            self.payment_btn.config(state="normal")
            self.receipt_btn.config(state="disabled")

    def load_bill_items(self):
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        if not self.current_order:
            return
        items = Database.get_order_items(self.current_order["id"])
        for item in items:
            self.bill_tree.insert("", "end", values=(
                item["item_name"],
                item["quantity"],
                f"{CURRENCY_SYMBOL} {item['unit_price']:,.2f}",
                f"{CURRENCY_SYMBOL} {item['total_price']:,.2f}"
            ))

    def update_totals(self):
        if not self.current_order:
            return
        order = self.current_order
        self.bill_subtotal.config(text=f"Subtotal: {CURRENCY_SYMBOL} {order['subtotal']:,.2f}")
        self.bill_discount.config(text=f"Discount: {CURRENCY_SYMBOL} {order['discount_amount']:,.2f}")
        self.bill_vat.config(text=f"VAT ({int(TAX_RATE*100)}%): {CURRENCY_SYMBOL} {order['tax_amount']:,.2f}")
        self.bill_total.config(text=f"TOTAL: {CURRENCY_SYMBOL} {order['total_amount']:,.2f}")

    def on_split_change(self, event=None):
        split_type = self.split_var.get()
        for widget in self.split_details.winfo_children():
            widget.destroy()
        if split_type == "Split Equally":
            tk.Label(self.split_details, text="Number of people:",
                    bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(side="left")
            self.people_count = tk.Spinbox(self.split_details, from_=2, to=20, width=5,
                                          font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
            self.people_count.pack(side="left", padx=5)
            tk.Button(self.split_details, text="Calculate",
                     command=self.calculate_equal_split,
                     bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                     relief="flat", cursor="hand2", padx=10).pack(side="left")
        elif split_type == "Split by Person":
            tk.Button(self.split_details, text="+ Add Person",
                     command=self.add_split_person,
                     bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                     relief="flat", cursor="hand2", padx=10).pack()

    def calculate_equal_split(self):
        if not self.current_order:
            return
        try:
            people = int(self.people_count.get())
            amount = self.current_order["total_amount"] / people
            messagebox.showinfo("Split Calculation", f"Each person pays: {CURRENCY_SYMBOL} {amount:,.2f}")
        except ValueError:
            messagebox.showerror("Error", "Invalid number of people.")

    def add_split_person(self):
        name = simpledialog.askstring("Person Name", "Enter name:")
        if name:
            amount = simpledialog.askfloat("Amount", f"Amount for {name} (KSh):")
            if amount:
                self.split_people.append({"name": name, "amount": amount})
                messagebox.showinfo("Added", f"{name}: {CURRENCY_SYMBOL} {amount:,.2f}")

    def calculate_change(self):
        if not self.current_order:
            return
        try:
            paid = float(self.amount_entry.get() or 0)
            total = self.current_order["total_amount"]
            change = paid - total
            self.change_label.config(text=f"Change: {CURRENCY_SYMBOL} {max(0, change):,.2f}")
        except ValueError:
            pass

    def process_payment(self):
        if not self.current_order:
            messagebox.showwarning("No Order", "Please select an order first.")
            return
        if self.payment_done:
            messagebox.showinfo("Already Paid", "This order has already been paid.")
            return
        try:
            amount_paid = float(self.amount_entry.get())
            payment_method = self.method_var.get()
            split_type = self.split_var.get().lower().replace(" ", "_")
            split_map = {"no_split": "none", "split_equally": "equal", "split_by_item": "by_item", "split_by_person": "by_person"}
            split_key = split_map.get(split_type, "none")
            if amount_paid < self.current_order["total_amount"]:
                messagebox.showerror("Insufficient Amount",
                                   f"Amount paid ({CURRENCY_SYMBOL} {amount_paid:,.2f}) is less than total ({CURRENCY_SYMBOL} {self.current_order['total_amount']:,.2f}).")
                return
            trans_ref = self.ref_entry.get().strip()
            if payment_method != 'cash' and not trans_ref:
                messagebox.showwarning("Missing Transaction Code", "Please enter the transaction code for M-Pesa or Card payment.")
                return
            payment_id = Database.process_payment(
                self.current_order["id"],
                self.current_user["id"],
                amount_paid,
                payment_method,
                split_key,
                trans_ref
            )
            if split_key == "by_person" and self.split_people:
                for person in self.split_people:
                    Database.add_payment_split(payment_id, person["name"], person["amount"], payment_method)
            Database.log_activity(self.current_user["id"], "PAYMENT", "payments", payment_id)
            self.payment_done = True
            self.payment_btn.config(state="disabled")
            self.receipt_btn.config(state="normal")
            messagebox.showinfo("Payment Successful",
                                f"Payment processed successfully!\nChange: {CURRENCY_SYMBOL} {amount_paid - self.current_order['total_amount']:,.2f}")
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid amount.")
        except Exception as e:
            messagebox.showerror("Payment Failed", f"Transaction failed: {str(e)}")

    def print_receipt(self):
        if not self.current_order:
            messagebox.showwarning("No Order", "Please select an order first.")
            return
        if not self.payment_done:
            messagebox.showwarning("Not Paid", "Please process payment first.")
            return
        receipt = ReceiptGenerator.generate_receipt(self.current_order["id"])
        window = tk.Toplevel(self.frame)
        window.title(f"Receipt - Order #{self.current_order['id']}")
        window.configure(bg=Theme.BG_PRIMARY)
        window.geometry("500x700")
        text_widget = tk.Text(window, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                             font=("Consolas", Theme.FONT_SIZE_NORMAL),
                             relief="flat", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", receipt)
        text_widget.config(state="disabled")
        tk.Button(window, text="Save to File", command=lambda: self.save_receipt(receipt),
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=10)

        self.load_unpaid_orders()
        self.payment_done = False
        self.receipt_btn.config(state="disabled")

    def print_bill(self):
        if not self.current_order:
            messagebox.showwarning("No Order", "Please select an order first.")
            return
        bill = ReceiptGenerator.generate_bill(self.current_order["id"])
        window = tk.Toplevel(self.frame)
        window.title(f"Bill - Order #{self.current_order['id']}")
        window.configure(bg=Theme.BG_PRIMARY)
        window.geometry("500x700")
        text_widget = tk.Text(window, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                             font=("Consolas", Theme.FONT_SIZE_NORMAL),
                             relief="flat", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", bill)
        text_widget.config(state="disabled")
        tk.Button(window, text="Save to File", command=lambda: self.save_receipt(bill),
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=10)

    def save_receipt(self, receipt_text):
        if not os.path.exists(RECEIPTS_DIR):
            os.makedirs(RECEIPTS_DIR)
        filename = f"{RECEIPTS_DIR}/receipt_{self.current_order['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(receipt_text)
        messagebox.showinfo("Saved", f"Receipt saved to:\n{filename}")

    def destroy(self):
        self.frame.destroy()