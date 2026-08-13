"""
Savanna Restaurant POS System - Authentication Module
======================================================
Handles user login, signup, and session management with secure password handling.
Provides role-based access control for different user types.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from config import Theme, APP_NAME, Roles
from styles import StyleManager

class AuthWindow:
    """Authentication window handling login and registration."""

    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.current_user = None

        self.root.title(f"{APP_NAME} - Sign In")
        self.root.geometry("450x600")
        self.root.configure(bg=Theme.BG_PRIMARY)
        self.root.resizable(False, False)

        self.style_manager = StyleManager(self.root)
        self.build_login_ui()

    def build_login_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(f"{APP_NAME} - Sign In")

        container = tk.Frame(self.root, bg=Theme.BG_PRIMARY)
        container.place(relx=0.5, rely=0.5, anchor="center")

        logo_label = tk.Label(container, text=APP_NAME,
                             bg=Theme.BG_PRIMARY, fg=Theme.ACCENT_PRIMARY,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold"))
        logo_label.pack(pady=(0, 5))

        tagline = tk.Label(container, text="Restaurant Management System",
                          bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY,
                          font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        tagline.pack(pady=(0, 30))

        card = tk.Frame(container, bg=Theme.BG_SECONDARY, padx=30, pady=25)
        card.pack(fill="x")

        tk.Label(card, text="Username", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w", pady=(0, 5))
        self.username_entry = tk.Entry(card, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                      insertbackground=Theme.TEXT_PRIMARY,
                                      font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                                      relief="flat", width=30)
        self.username_entry.pack(fill="x", pady=(0, 15), ipady=8)
        # Entry is left empty

        tk.Label(card, text="Password", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w", pady=(0, 5))
        self.password_entry = tk.Entry(card, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                      insertbackground=Theme.TEXT_PRIMARY,
                                      font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                                      relief="flat", width=30, show="*")
        self.password_entry.pack(fill="x", pady=(0, 20), ipady=8)
        # Entry is left empty

        login_btn = tk.Button(card, text="SIGN IN", command=self.attempt_login,
                             bg=Theme.ACCENT_PRIMARY, fg=Theme.TEXT_ON_ACCENT,
                             font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"),
                             relief="flat", cursor="hand2",
                             activebackground="#1ed760", activeforeground=Theme.TEXT_ON_ACCENT,
                             padx=20, pady=10)
        login_btn.pack(fill="x", pady=(0, 15))

        # No hint label

        signup_frame = tk.Frame(container, bg=Theme.BG_PRIMARY)
        signup_frame.pack(pady=20)
        tk.Label(signup_frame, text="New staff member? ",
                bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(side="left")
        signup_link = tk.Label(signup_frame, text="Register here",
                              bg=Theme.BG_PRIMARY, fg=Theme.ACCENT_PRIMARY,
                              font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                              cursor="hand2")
        signup_link.pack(side="left")
        signup_link.bind("<Button-1>", lambda e: self.show_signup())

        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

    def build_signup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(f"{APP_NAME} - Register")

        container = tk.Frame(self.root, bg=Theme.BG_PRIMARY)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Create Account",
                bg=Theme.BG_PRIMARY, fg=Theme.ACCENT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold")).pack(pady=(0, 20))

        card = tk.Frame(container, bg=Theme.BG_SECONDARY, padx=30, pady=20)
        card.pack(fill="x")

        tk.Label(card, text="Full Name", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w")
        self.reg_name = tk.Entry(card, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                insertbackground=Theme.TEXT_PRIMARY,
                                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        self.reg_name.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(card, text="Username", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w")
        self.reg_username = tk.Entry(card, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                    insertbackground=Theme.TEXT_PRIMARY,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        self.reg_username.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(card, text="Email", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w")
        self.reg_email = tk.Entry(card, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                 insertbackground=Theme.TEXT_PRIMARY,
                                 font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), relief="flat")
        self.reg_email.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(card, text="Role", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w")
        self.reg_role = ttk.Combobox(card, values=Roles.ALL, state="readonly",
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
        self.reg_role.set(Roles.WAITER)
        self.reg_role.pack(fill="x", pady=(0, 10))

        tk.Label(card, text="Password", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w")
        self.reg_password = tk.Entry(card, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                    insertbackground=Theme.TEXT_PRIMARY,
                                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                                    relief="flat", show="*")
        self.reg_password.pack(fill="x", pady=(0, 10), ipady=6)

        tk.Label(card, text="Confirm Password", bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)).pack(anchor="w")
        self.reg_confirm = tk.Entry(card, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                   insertbackground=Theme.TEXT_PRIMARY,
                                   font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                                   relief="flat", show="*")
        self.reg_confirm.pack(fill="x", pady=(0, 15), ipady=6)

        reg_btn = tk.Button(card, text="CREATE ACCOUNT", command=self.attempt_register,
                           bg=Theme.ACCENT_SUCCESS, fg=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"),
                           relief="flat", cursor="hand2", padx=20, pady=10)
        reg_btn.pack(fill="x", pady=(0, 10))

        back_link = tk.Label(card, text="Already have an account? Sign In",
                            bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_PRIMARY,
                            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), cursor="hand2")
        back_link.pack()
        back_link.bind("<Button-1>", lambda e: self.build_login_ui())

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter both username and password.")
            return

        user = Database.authenticate_user(username, password)

        if user:
            self.current_user = user
            Database.log_activity(user["id"], "LOGIN", "users", user["id"])
            self.on_login_success(user)
        else:
            messagebox.showerror("Authentication Failed", 
                               "Invalid username or password. Please try again.")
            self.password_entry.delete(0, tk.END)

    def attempt_register(self):
        full_name = self.reg_name.get().strip()
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        role = self.reg_role.get()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()

        if not all([full_name, username, email, password]):
            messagebox.showwarning("Input Required", "Please fill in all fields.")
            return

        if password != confirm:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return

        if len(password) < 6:
            messagebox.showwarning("Weak Password", "Password must be at least 6 characters.")
            return

        try:
            user_id = Database.create_user(username, password, full_name, email, role)
            messagebox.showinfo("Success", "Account created successfully! You can now sign in.")
            self.build_login_ui()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Registration Failed", "Username already exists.")
            else:
                messagebox.showerror("Error", f"Registration failed: {str(e)}")

    def show_signup(self):
        self.build_signup_ui()

    def show_login(self):
        self.build_login_ui()