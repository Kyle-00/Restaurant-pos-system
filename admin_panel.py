"""
Savanna Restaurant POS System - Admin Panel & Analytics
========================================================
Reporting dashboard + Manage Staff + Period Reports + Shift Log + QR Codes.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
import os
import socket
from database import Database
from config import Theme, CURRENCY_SYMBOL, REPORTS_DIR, Roles, DB_PATH, QR_CODES_DIR
from receipt import ReceiptGenerator


class AdminPanel:
    def __init__(self, parent, current_user, refresh_callback=None):
        self.parent = parent
        self.current_user = current_user
        self.refresh_callback = refresh_callback
        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)
        self.build_ui()
        self.load_daily_report()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Administration",
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        date_frame = tk.Frame(header, bg=Theme.BG_TERTIARY)
        date_frame.pack(side="right", padx=20)
        tk.Label(date_frame, text="Date:", bg=Theme.BG_TERTIARY, fg=Theme.TEXT_SECONDARY).pack(side="left")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(date_frame, textvariable=self.date_var, width=12,
                             bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        date_entry.pack(side="left", padx=5)
        tk.Button(date_frame, text="Load", command=self.load_daily_report,
                 bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                 relief="flat", cursor="hand2", padx=10, pady=3).pack(side="left", padx=5)

        self.notebook = ttk.Notebook(self.frame, style="Custom.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.summary_frame = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.items_frame = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.payments_frame = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.staff_frame = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.period_frame = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.shift_frame = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.qr_frame = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)

        self.notebook.add(self.summary_frame, text="Daily Summary")
        self.notebook.add(self.items_frame, text="Top Items")
        self.notebook.add(self.payments_frame, text="Payment Methods")
        self.notebook.add(self.staff_frame, text="Manage Staff")
        self.notebook.add(self.period_frame, text="Period Reports")
        self.notebook.add(self.shift_frame, text="Shift Log")
        self.notebook.add(self.qr_frame, text="QR Codes")

        self.build_summary_tab()
        self.build_items_tab()
        self.build_payments_tab()
        self.build_staff_tab()
        self.build_period_tab()
        self.build_shift_tab()
        self.build_qr_tab()

    # ---- Summary Tab ----
    def build_summary_tab(self):
        cards_frame = tk.Frame(self.summary_frame, bg=Theme.BG_PRIMARY)
        cards_frame.pack(fill="x", padx=20, pady=20)
        self.stat_cards = {}
        stats = [
            ("Total Revenue", "0.00", Theme.ACCENT_SUCCESS),
            ("Total Orders", "0", Theme.ACCENT_PRIMARY),
            ("Avg Order Value", "0.00", Theme.ACCENT_GOLD),
            ("Total Items Sold", "0", Theme.ACCENT_SECONDARY)
        ]
        for title, value, color in stats:
            card = tk.Frame(cards_frame, bg=Theme.BG_SECONDARY, padx=20, pady=15)
            card.pack(side="left", fill="both", expand=True, padx=5)
            card.configure(highlightbackground=color, highlightthickness=2)
            tk.Label(card, text=title, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w")
            label = tk.Label(card, text=f"{CURRENCY_SYMBOL} {value}" if "Revenue" in title or "Value" in title else value,
                          bg=Theme.BG_SECONDARY, fg=color,
                          font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_XL, "bold"))
            label.pack(anchor="w", pady=(5, 0))
            self.stat_cards[title] = label

        detail_frame = tk.Frame(self.summary_frame, bg=Theme.BG_SECONDARY, padx=20, pady=20)
        detail_frame.pack(fill="x", padx=20, pady=10)
        self.detail_labels = {}
        details = ["Subtotal", "Discounts", "VAT (10%)", "Net Total"]
        for detail in details:
            frame = tk.Frame(detail_frame, bg=Theme.BG_SECONDARY)
            frame.pack(fill="x", pady=3)
            tk.Label(frame, text=f"{detail}:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(side="left")
            label = tk.Label(frame, text=f"{CURRENCY_SYMBOL} 0.00",
                           bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"))
            label.pack(side="right")
            self.detail_labels[detail] = label

        tk.Button(self.summary_frame, text="Export Daily Report",
                 command=self.export_report,
                 bg=Theme.ACCENT_GOLD, fg=Theme.BG_PRIMARY,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=20)

    # ---- Items Tab ----
    def build_items_tab(self):
        columns = ("rank", "name", "category", "qty", "revenue", "orders")
        self.items_tree = ttk.Treeview(self.items_frame, columns=columns, show="headings",
                                      height=20, style="Custom.Treeview")
        self.items_tree.heading("rank", text="#")
        self.items_tree.heading("name", text="Item Name")
        self.items_tree.heading("category", text="Category")
        self.items_tree.heading("qty", text="Qty Sold")
        self.items_tree.heading("revenue", text="Revenue")
        self.items_tree.heading("orders", text="Times Ordered")
        self.items_tree.column("rank", width=40, anchor="center")
        self.items_tree.column("name", width=250)
        self.items_tree.column("category", width=120)
        self.items_tree.column("qty", width=80, anchor="center")
        self.items_tree.column("revenue", width=100, anchor="e")
        self.items_tree.column("orders", width=100, anchor="center")
        self.items_tree.pack(fill="both", expand=True, padx=20, pady=20)

    # ---- Payments Tab ----
    def build_payments_tab(self):
        self.payments_tree = ttk.Treeview(self.payments_frame, columns=("method", "count", "amount"),
                                          show="headings", height=10, style="Custom.Treeview")
        self.payments_tree.heading("method", text="Payment Method")
        self.payments_tree.heading("count", text="Transactions")
        self.payments_tree.heading("amount", text="Total Amount")
        self.payments_tree.column("method", width=200)
        self.payments_tree.column("count", width=150, anchor="center")
        self.payments_tree.column("amount", width=150, anchor="e")
        self.payments_tree.pack(fill="both", expand=True, padx=20, pady=20)

    # ---- Staff Tab ----
    def build_staff_tab(self):
        frame = self.staff_frame
        tk.Label(frame, text="Manage Staff", bg=Theme.BG_PRIMARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=20, pady=10)

        columns = ("id", "username", "full_name", "email", "phone", "role")
        self.staff_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10, style="Custom.Treeview")
        self.staff_tree.heading("id", text="ID")
        self.staff_tree.heading("username", text="Username")
        self.staff_tree.heading("full_name", text="Full Name")
        self.staff_tree.heading("email", text="Email")
        self.staff_tree.heading("phone", text="Phone")
        self.staff_tree.heading("role", text="Role")
        self.staff_tree.column("id", width=50)
        self.staff_tree.column("username", width=120)
        self.staff_tree.column("full_name", width=150)
        self.staff_tree.column("email", width=180)
        self.staff_tree.column("phone", width=120)
        self.staff_tree.column("role", width=80)
        self.staff_tree.pack(fill="both", expand=True, padx=20, pady=10)

        btn_frame = tk.Frame(frame, bg=Theme.BG_PRIMARY)
        btn_frame.pack(fill="x", padx=20, pady=10)
        tk.Button(btn_frame, text="Edit User", command=self.edit_user,
                 bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), padx=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Change Password", command=self.change_password,
                 bg=Theme.ACCENT_WARNING, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), padx=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_staff,
                 bg=Theme.ACCENT_DANGER, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), padx=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_staff,
                 bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), padx=10).pack(side="left", padx=5)

        self.load_staff()

    def load_staff(self):
        for item in self.staff_tree.get_children():
            self.staff_tree.delete(item)
        users = Database.get_all_users()
        for u in sorted(users, key=lambda x: x["id"]):
            self.staff_tree.insert("", "end", values=(u["id"], u["username"], u["full_name"], u["email"], u.get("phone", ""), u["role"]))

    def edit_user(self):
        selection = self.staff_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to edit.")
            return
        values = self.staff_tree.item(selection[0], "values")
        user_id = values[0]
        current_username = values[1]
        current_fullname = values[2]
        current_email = values[3]
        current_phone = values[4] if len(values) > 4 else ""
        current_role = values[5] if len(values) > 5 else "waiter"

        # Larger dialog with scrollable canvas
        dialog = tk.Toplevel(self.frame)
        dialog.title("Edit User")
        dialog.configure(bg=Theme.BG_SECONDARY)
        dialog.geometry("400x480")  # increased height
        dialog.transient(self.frame)
        dialog.grab_set()

        # Main frame to hold all widgets
        main_frame = tk.Frame(dialog, bg=Theme.BG_SECONDARY)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Username
        tk.Label(main_frame, text="Username:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(5,0))
        username_entry = tk.Entry(main_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        username_entry.insert(0, current_username)
        username_entry.pack(fill="x", pady=5)

        # Full Name
        tk.Label(main_frame, text="Full Name:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(5,0))
        fullname_entry = tk.Entry(main_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        fullname_entry.insert(0, current_fullname)
        fullname_entry.pack(fill="x", pady=5)

        # Email
        tk.Label(main_frame, text="Email:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(5,0))
        email_entry = tk.Entry(main_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        email_entry.insert(0, current_email if current_email else "")
        email_entry.pack(fill="x", pady=5)

        # Phone
        tk.Label(main_frame, text="Phone:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(5,0))
        phone_entry = tk.Entry(main_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        phone_entry.insert(0, current_phone)
        phone_entry.pack(fill="x", pady=5)

        # Role
        tk.Label(main_frame, text="Role:", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(5,0))
        role_combo = ttk.Combobox(main_frame, values=Roles.ALL, state="readonly")
        role_combo.set(current_role)
        role_combo.pack(fill="x", pady=5)

        # Save button
        def save():
            new_username = username_entry.get().strip()
            new_fullname = fullname_entry.get().strip()
            new_email = email_entry.get().strip()
            new_phone = phone_entry.get().strip()
            new_role = role_combo.get()
            if not new_username or not new_fullname:
                messagebox.showerror("Error", "Username and Full Name are required.")
                return
            try:
                Database.update_user(user_id, username=new_username, full_name=new_fullname,
                                     email=new_email, phone=new_phone, role=new_role)
                self.load_staff()
                if int(user_id) == self.current_user["id"] and self.refresh_callback:
                    self.refresh_callback()
                dialog.destroy()
                messagebox.showinfo("Success", "User updated.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(main_frame, text="Save", command=save,
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 padx=10, pady=5).pack(pady=15)

    def change_password(self):
        selection = self.staff_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user.")
            return
        values = self.staff_tree.item(selection[0], "values")
        user_id = values[0]
        username = values[1]

        new_password = simpledialog.askstring("Change Password", f"Enter new password for {username}:", show="*")
        if new_password:
            if len(new_password) < 6:
                messagebox.showerror("Weak Password", "Password must be at least 6 characters.")
                return
            confirm = simpledialog.askstring("Confirm Password", "Re-enter new password:", show="*")
            if new_password != confirm:
                messagebox.showerror("Mismatch", "Passwords do not match.")
                return
            try:
                Database.change_password(user_id, new_password)
                messagebox.showinfo("Success", "Password changed.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_staff(self):
        selection = self.staff_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to delete.")
            return
        values = self.staff_tree.item(selection[0], "values")
        user_id = values[0]
        username = values[1]
        if username == self.current_user["username"]:
            messagebox.showerror("Cannot Delete", "You cannot delete yourself.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete user '{username}'?"):
            try:
                Database.delete_user(user_id)
                self.load_staff()
                messagebox.showinfo("Deleted", "User deleted.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ---- Period Reports Tab ----
    def build_period_tab(self):
        frame = self.period_frame
        tk.Label(frame, text="Period Reports", bg=Theme.BG_PRIMARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=20, pady=10)

        control_frame = tk.Frame(frame, bg=Theme.BG_PRIMARY)
        control_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(control_frame, text="Period:", bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=5)
        self.period_type_var = tk.StringVar(value="month")
        period_combo = ttk.Combobox(control_frame, textvariable=self.period_type_var, values=["week", "month"],
                                   state="readonly", width=8)
        period_combo.pack(side="left", padx=5)
        period_combo.bind("<<ComboboxSelected>>", self.load_period_report)

        tk.Label(control_frame, text="Count:", bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=5)
        self.period_count_var = tk.StringVar(value="3")
        count_combo = ttk.Combobox(control_frame, textvariable=self.period_count_var, values=["3", "6", "12"],
                                   state="readonly", width=5)
        count_combo.pack(side="left", padx=5)
        count_combo.bind("<<ComboboxSelected>>", self.load_period_report)

        tree_frame = tk.Frame(frame, bg=Theme.BG_PRIMARY)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        columns = ("period", "revenue")
        self.period_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                       height=10, style="Custom.Treeview",
                                       yscrollcommand=scrollbar.set)
        self.period_tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.period_tree.yview)
        self.period_tree.heading("period", text="Period")
        self.period_tree.heading("revenue", text="Revenue")
        self.period_tree.column("period", width=200)
        self.period_tree.column("revenue", width=150, anchor="e")

        self.load_period_report()

    def load_period_report(self, event=None):
        period_type = self.period_type_var.get()
        count = int(self.period_count_var.get())
        data = Database.get_sales_by_period(period_type, count)
        for item in self.period_tree.get_children():
            self.period_tree.delete(item)
        for entry in data:
            self.period_tree.insert("", "end", values=(entry["label"], f"{CURRENCY_SYMBOL} {entry['revenue']:,.2f}"))

    # ---- Shift Log Tab ----
    def build_shift_tab(self):
        frame = self.shift_frame
        tk.Label(frame, text="Employee Shift Log", bg=Theme.BG_PRIMARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=20, pady=10)

        tree_frame = tk.Frame(frame, bg=Theme.BG_PRIMARY)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        columns = ("user", "event", "timestamp", "notes")
        self.shift_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                       height=12, style="Custom.Treeview",
                                       yscrollcommand=scrollbar.set)
        self.shift_tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.shift_tree.yview)
        self.shift_tree.heading("user", text="Employee")
        self.shift_tree.heading("event", text="Event")
        self.shift_tree.heading("timestamp", text="Timestamp")
        self.shift_tree.heading("notes", text="Notes")
        self.shift_tree.column("user", width=150)
        self.shift_tree.column("event", width=100)
        self.shift_tree.column("timestamp", width=180)
        self.shift_tree.column("notes", width=200)

        btn_frame = tk.Frame(frame, bg=Theme.BG_PRIMARY)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Refresh Shift Log", command=self.load_shift_log,
                 bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), padx=10).pack()

        self.load_shift_log()

    def load_shift_log(self):
        for item in self.shift_tree.get_children():
            self.shift_tree.delete(item)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ce.event_type, ce.timestamp, ce.notes, u.full_name
            FROM clock_events ce
            JOIN users u ON ce.user_id = u.id
            ORDER BY ce.timestamp DESC
            LIMIT 200
        """)
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            self.shift_tree.insert("", "end", values=(
                row["full_name"],
                row["event_type"].replace("_", " ").title(),
                row["timestamp"][:19],
                row["notes"] or ""
            ))

    # ---- QR Codes Tab ----
    def build_qr_tab(self):
        frame = self.qr_frame
        tk.Label(frame, text="QR Code Generation", bg=Theme.BG_PRIMARY, fg=Theme.ACCENT_GOLD,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=20, pady=10)

        info_label = tk.Label(frame, text="Generate QR codes for all tables.\n"
                                          "The images will be saved in the 'qr_codes/' folder.\n"
                                          "You can print them and place them on tables.",
                              bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY,
                              font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                              justify="left")
        info_label.pack(anchor="w", padx=20, pady=10)

        # Button to generate
        gen_btn = tk.Button(frame, text="Generate QR Codes for All Tables",
                           command=self.generate_qr_codes,
                           bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                           relief="flat", cursor="hand2", padx=20, pady=10)
        gen_btn.pack(pady=20)

        # Label to show folder path
        self.qr_path_label = tk.Label(frame, text=f"QR codes will be saved to: {QR_CODES_DIR}",
                                      bg=Theme.BG_PRIMARY, fg=Theme.TEXT_MUTED,
                                      font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.qr_path_label.pack(pady=10)

        # Button to open folder (optional)
        open_btn = tk.Button(frame, text="Open QR Codes Folder",
                            command=self.open_qr_folder,
                            bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                            relief="flat", cursor="hand2", padx=15, pady=5)
        open_btn.pack(pady=5)

    def generate_qr_codes(self):
        try:
            from qr_server import generate_all_qr_codes
            host_ip = socket.gethostbyname(socket.gethostname())
            generate_all_qr_codes(host_ip)
            messagebox.showinfo("QR Codes Generated",
                                f"QR codes for all tables have been generated and saved to:\n{QR_CODES_DIR}\n\n"
                                f"URL base: http://{host_ip}:5000/table/")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR codes:\n{str(e)}")

    def open_qr_folder(self):
        import os
        if os.path.exists(QR_CODES_DIR):
            os.startfile(QR_CODES_DIR)  # Works on Windows; for Linux use `xdg-open`, for macOS `open`
        else:
            messagebox.showerror("Folder Not Found", f"The folder '{QR_CODES_DIR}' does not exist yet. Generate QR codes first.")

    # ---- Reports ----
    def load_daily_report(self):
        try:
            date = self.date_var.get()
            sales = Database.get_daily_sales(date)
            summary = sales["summary"]

            self.stat_cards["Total Revenue"].config(text=f"{CURRENCY_SYMBOL} {summary['total_revenue']:,.2f}")
            self.stat_cards["Total Orders"].config(text=str(summary['total_orders']))
            self.stat_cards["Avg Order Value"].config(text=f"{CURRENCY_SYMBOL} {summary['avg_order_value']:,.2f}")

            total_items = sum(item["total_qty"] for item in sales["top_items"])
            self.stat_cards["Total Items Sold"].config(text=str(total_items))

            self.detail_labels["Subtotal"].config(text=f"{CURRENCY_SYMBOL} {summary['total_revenue'] + summary['total_discount']:,.2f}")
            self.detail_labels["Discounts"].config(text=f"-{CURRENCY_SYMBOL} {summary['total_discount']:,.2f}")
            self.detail_labels["VAT (10%)"].config(text=f"{CURRENCY_SYMBOL} {summary['total_tax']:,.2f}")
            self.detail_labels["Net Total"].config(text=f"{CURRENCY_SYMBOL} {summary['total_revenue']:,.2f}")

            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            for i, item in enumerate(sales["top_items"], 1):
                self.items_tree.insert("", "end", values=(
                    i,
                    item["name"],
                    "",
                    item["total_qty"],
                    f"{CURRENCY_SYMBOL} {item['total_revenue']:,.2f}",
                    ""
                ))

            for item in self.payments_tree.get_children():
                self.payments_tree.delete(item)
            method_map = {'cash': 'Cash', 'mpesa': 'M-Pesa', 'card': 'Card/Bank'}
            for pm in sales["payment_methods"]:
                self.payments_tree.insert("", "end", values=(
                    method_map.get(pm["payment_method"], pm["payment_method"].upper()),
                    pm["count"],
                    f"{CURRENCY_SYMBOL} {pm['amount']:,.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load report: {str(e)}")

    def export_report(self):
        try:
            import os
            if not os.path.exists(REPORTS_DIR):
                os.makedirs(REPORTS_DIR)
            date = self.date_var.get()
            report = ReceiptGenerator.generate_daily_report(date)
            filename = f"{REPORTS_DIR}/daily_report_{date}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            messagebox.showinfo("Exported", f"Report saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def destroy(self):
        self.frame.destroy()