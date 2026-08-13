"""
Savanna Restaurant POS System - Menu Manager
=============================================
Admin interface for adding, editing, and organizing menu categories and items.
Shows all items (including unavailable) with a toggle that works without disappearing.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from config import Theme, CURRENCY_SYMBOL
from styles import StyleManager, ScrollableFrame

class MenuManager:
    """Menu management interface for administrators and managers."""

    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user

        self.frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_categories()
        self.load_menu_items()

    def build_ui(self):
        header = tk.Frame(self.frame, bg=Theme.BG_TERTIARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Menu Editor",
                bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(side="left", padx=20, pady=15)

        btn_frame = tk.Frame(header, bg=Theme.BG_TERTIARY)
        btn_frame.pack(side="right", padx=10)

        tk.Button(btn_frame, text="+ Category",
                 command=self.add_category,
                 bg=Theme.ACCENT_SECONDARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                 relief="flat", cursor="hand2", padx=15, pady=5).pack(side="left", padx=5)

        tk.Button(btn_frame, text="+ Menu Item",
                 command=self.add_menu_item,
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                 relief="flat", cursor="hand2", padx=15, pady=5).pack(side="left", padx=5)

        content = tk.Frame(self.frame, bg=Theme.BG_PRIMARY)
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Categories
        cat_frame = tk.Frame(content, bg=Theme.BG_SECONDARY, width=250)
        cat_frame.pack(side="left", fill="y", padx=(0, 5))
        cat_frame.pack_propagate(False)

        tk.Label(cat_frame, text="Categories",
                bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=10, pady=10)

        self.cat_listbox = tk.Listbox(cat_frame, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                     font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                                     selectbackground=Theme.ACCENT_PRIMARY,
                                     selectforeground=Theme.TEXT_ON_ACCENT,
                                     relief="flat", bd=0, highlightthickness=0)
        self.cat_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.cat_listbox.bind("<<ListboxSelect>>", self.on_category_select)

        # Right: Menu Items with scrollbar
        items_frame = tk.Frame(content, bg=Theme.BG_SECONDARY)
        items_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        tk.Label(items_frame, text="Menu Items",
                bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(anchor="w", padx=10, pady=10)

        # Tree frame with scrollbar
        tree_frame = tk.Frame(items_frame, bg=Theme.BG_SECONDARY)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        columns = ("name", "category", "price", "available")
        self.items_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                      height=15, style="Custom.Treeview",
                                      yscrollcommand=scrollbar.set)
        self.items_tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.items_tree.yview)

        self.items_tree.heading("name", text="Item Name")
        self.items_tree.heading("category", text="Category")
        self.items_tree.heading("price", text="Price")
        self.items_tree.heading("available", text="Available")

        self.items_tree.column("name", width=250)
        self.items_tree.column("category", width=150)
        self.items_tree.column("price", width=100, anchor="e")
        self.items_tree.column("available", width=80, anchor="center")

        action_frame = tk.Frame(items_frame, bg=Theme.BG_SECONDARY, padx=10, pady=10)
        action_frame.pack(fill="x")

        tk.Button(action_frame, text="Edit", command=self.edit_item,
                 bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                 relief="flat", cursor="hand2", padx=15, pady=5).pack(side="left", padx=2)

        tk.Button(action_frame, text="Toggle Available", command=self.toggle_available,
                 bg=Theme.ACCENT_WARNING, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                 relief="flat", cursor="hand2", padx=15, pady=5).pack(side="left", padx=2)

        tk.Button(action_frame, text="Delete", command=self.delete_item,
                 bg=Theme.ACCENT_DANGER, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                 relief="flat", cursor="hand2", padx=15, pady=5).pack(side="left", padx=2)

    def load_categories(self):
        self.cat_listbox.delete(0, tk.END)
        self.categories = Database.get_all_categories()
        self.cat_listbox.insert(tk.END, "All Items")
        for cat in self.categories:
            self.cat_listbox.insert(tk.END, cat["name"])

    def load_menu_items(self):
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)

        # Fetch all items (including unavailable)
        items = Database.get_all_menu_items_with_unavailable()
        for item in items:
            self.items_tree.insert("", "end", values=(
                item["name"],
                item["category_name"],
                f"{CURRENCY_SYMBOL} {item['price']:,.2f}",
                "Yes" if item["is_available"] else "No"
            ), tags=(str(item["id"]),))

    def on_category_select(self, event):
        selection = self.cat_listbox.curselection()
        if not selection:
            return

        if selection[0] == 0:
            self.load_menu_items()
            return

        cat_name = self.cat_listbox.get(selection[0])
        cat_id = next((c["id"] for c in self.categories if c["name"] == cat_name), None)

        if cat_id:
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)

            # Fetch items by category (including unavailable)
            items = Database.get_menu_items_by_category_unavailable(cat_id)  # need new method
            for item in items:
                self.items_tree.insert("", "end", values=(
                    item["name"],
                    cat_name,
                    f"{CURRENCY_SYMBOL} {item['price']:,.2f}",
                    "Yes" if item["is_available"] else "No"
                ), tags=(str(item["id"]),))

    def add_category(self):
        dialog = tk.Toplevel(self.frame)
        dialog.title("Add Category")
        dialog.configure(bg=Theme.BG_SECONDARY)
        dialog.geometry("400x250")
        dialog.transient(self.frame)
        dialog.grab_set()

        tk.Label(dialog, text="Category Name", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(15, 5))
        name_entry = tk.Entry(dialog, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        name_entry.pack(fill="x", padx=20, pady=5)

        tk.Label(dialog, text="Description", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        desc_entry = tk.Entry(dialog, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        desc_entry.pack(fill="x", padx=20, pady=5)

        def save():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            if name:
                try:
                    Database.add_category(name, desc)
                    self.load_categories()
                    dialog.destroy()
                    messagebox.showinfo("Success", "Category added successfully!")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        tk.Button(dialog, text="Save", command=save,
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 relief="flat", cursor="hand2", padx=20, pady=8).pack(pady=20)

    def add_menu_item(self):
        dialog = tk.Toplevel(self.frame)
        dialog.title("Add Menu Item")
        dialog.configure(bg=Theme.BG_SECONDARY)
        dialog.geometry("450x400")
        dialog.transient(self.frame)
        dialog.grab_set()

        tk.Label(dialog, text="Category", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        cat_var = tk.StringVar()
        cat_combo = ttk.Combobox(dialog, textvariable=cat_var, values=[c["name"] for c in self.categories],
                                state="readonly", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        cat_combo.pack(fill="x", padx=20, pady=5)

        tk.Label(dialog, text="Item Name", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        name_entry = tk.Entry(dialog, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        name_entry.pack(fill="x", padx=20, pady=5)

        tk.Label(dialog, text="Description", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        desc_entry = tk.Entry(dialog, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        desc_entry.pack(fill="x", padx=20, pady=5)

        tk.Label(dialog, text="Price (KSh)", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        price_entry = tk.Entry(dialog, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                              font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        price_entry.pack(fill="x", padx=20, pady=5)

        def save():
            cat_name = cat_var.get()
            cat_id = next((c["id"] for c in self.categories if c["name"] == cat_name), None)

            if not cat_id:
                messagebox.showwarning("Input Required", "Please select a category.")
                return

            try:
                price = float(price_entry.get())
                Database.add_menu_item(
                    cat_id,
                    name_entry.get().strip(),
                    desc_entry.get().strip(),
                    price,
                    0,  # vegan
                    0   # gluten-free
                )
                self.load_menu_items()
                dialog.destroy()
                messagebox.showinfo("Success", "Menu item added successfully!")
            except ValueError:
                messagebox.showerror("Invalid Price", "Please enter a valid price.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(dialog, text="Save Item", command=save,
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 relief="flat", cursor="hand2", padx=20, pady=8).pack(pady=15)

    def edit_item(self):
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to edit.")
            return
        item_id = int(self.items_tree.item(selection[0], "tags")[0])
        item = Database.get_menu_item(item_id)
        if not item:
            messagebox.showerror("Error", "Item not found.")
            return

        dialog = tk.Toplevel(self.frame)
        dialog.title("Edit Menu Item")
        dialog.configure(bg=Theme.BG_SECONDARY)
        dialog.geometry("450x400")
        dialog.transient(self.frame)
        dialog.grab_set()

        tk.Label(dialog, text="Category", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        cat_var = tk.StringVar(value=item["category_name"])
        cat_combo = ttk.Combobox(dialog, textvariable=cat_var, values=[c["name"] for c in self.categories],
                                state="readonly", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        cat_combo.pack(fill="x", padx=20, pady=5)

        tk.Label(dialog, text="Item Name", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        name_entry = tk.Entry(dialog, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        name_entry.insert(0, item["name"])
        name_entry.pack(fill="x", padx=20, pady=5)

        tk.Label(dialog, text="Description", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        desc_entry = tk.Entry(dialog, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        desc_entry.insert(0, item["description"] or "")
        desc_entry.pack(fill="x", padx=20, pady=5)

        tk.Label(dialog, text="Price (KSh)", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY).pack(pady=(10, 5))
        price_entry = tk.Entry(dialog, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                              font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        price_entry.insert(0, str(item["price"]))
        price_entry.pack(fill="x", padx=20, pady=5)

        def save():
            cat_name = cat_var.get()
            cat_id = next((c["id"] for c in self.categories if c["name"] == cat_name), None)
            if not cat_id:
                messagebox.showwarning("Input Required", "Please select a category.")
                return
            try:
                price = float(price_entry.get())
                Database.update_menu_item(item_id,
                                         category_id=cat_id,
                                         name=name_entry.get().strip(),
                                         description=desc_entry.get().strip(),
                                         price=price)
                self.load_menu_items()
                dialog.destroy()
                messagebox.showinfo("Success", "Item updated successfully!")
            except ValueError:
                messagebox.showerror("Invalid Price", "Please enter a valid price.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(dialog, text="Update", command=save,
                 bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                 relief="flat", cursor="hand2", padx=20, pady=8).pack(pady=15)

    def toggle_available(self):
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item.")
            return
        item_id = int(self.items_tree.item(selection[0], "tags")[0])
        item = Database.get_menu_item(item_id)
        if item:
            new_status = 0 if item["is_available"] else 1
            Database.update_menu_item(item_id, is_available=new_status)
            self.load_menu_items()   # Refresh list – item stays visible with updated status
            messagebox.showinfo("Success", f"Availability toggled to {'Available' if new_status else 'Unavailable'}.")

    def delete_item(self):
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Delete this menu item? This cannot be undone."):
            item_id = int(self.items_tree.item(selection[0], "tags")[0])
            try:
                Database.delete_menu_item(item_id)
                self.load_menu_items()
                messagebox.showinfo("Deleted", "Item deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def destroy(self):
        self.frame.destroy()