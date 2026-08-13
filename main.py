"""
Savanna Restaurant POS System - Main Application
================================================
Central application controller managing all views, navigation, and session state.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
from config import Theme, APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, Roles
from styles import StyleManager
from database import Database, get_db_connection
from auth import AuthWindow
from landing_page import LandingPage
from table_manager import TableManager
from order_system import OrderSystem
from kitchen_view import KitchenView
from menu_manager import MenuManager
from billing import BillingSystem
from admin_panel import AdminPanel
from staff_view import StaffView
from activity_log import ActivityLog
from my_orders import MyOrders
from migrations import run_migrations
from backup_manager import create_backup
from settings_manager import SettingsManager


class RestaurantPOSApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.root.configure(bg=Theme.BG_PRIMARY)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.center_window()

        Database.init_database()
        run_migrations()

        # Auto‑seed if no users exist
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                Database.seed_demo_data()

        SettingsManager.apply_theme_to_root(self.root)

        # Start backup scheduler
        def schedule_backup():
            create_backup()
            threading.Timer(86400, schedule_backup).start()
        schedule_backup()

        # Start QR server (optional)
        try:
            import qr_server
            host_ip = socket.gethostbyname(socket.gethostname())
            qr_thread = threading.Thread(target=qr_server.start_server, args=(host_ip,), daemon=True)
            qr_thread.start()
            print(f"QR server started at http://{host_ip}:5000")
        except Exception as e:
            print(f"Could not start QR server: {e}")

        self.current_user = None
        self.current_view = None
        self.nav_buttons = {}

        self.show_auth()

    def center_window(self):
        self.root.update_idletasks()
        width = WINDOW_MIN_WIDTH
        height = WINDOW_MIN_HEIGHT
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def show_auth(self):
        self.clear_window()
        self.auth_window = AuthWindow(self.root, self.on_login_success)

    def on_login_success(self, user):
        self.current_user = user
        self.build_main_app()

    def build_main_app(self):
        self.clear_window()
        self.root.title(f"{APP_NAME} - {self.current_user['full_name']}")
        self.root.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.center_window()

        self.main_container = tk.Frame(self.root, bg=Theme.BG_PRIMARY)
        self.main_container.pack(fill="both", expand=True)

        self.build_sidebar()

        self.content_frame = tk.Frame(self.main_container, bg=Theme.BG_PRIMARY)
        self.content_frame.pack(side="left", fill="both", expand=True)

        self.navigate_to("landing")

    def build_sidebar(self):
        sidebar = tk.Frame(self.main_container, bg=Theme.BG_SECONDARY, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = tk.Frame(sidebar, bg=Theme.BG_TERTIARY, height=80)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text=APP_NAME,
                bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold")).pack(pady=20)

        role = self.current_user["role"]
        nav_items = [
            ("Dashboard", "landing", True),
            ("Floor Plan", "tables", role in [Roles.ADMIN, Roles.WAITER]),
            ("Orders", "orders", role in [Roles.ADMIN, Roles.WAITER]),
            ("Kitchen", "kitchen", role in [Roles.ADMIN, Roles.CHEF]),
            ("Menu", "menu", True),
            ("Billing", "billing", role in [Roles.ADMIN, Roles.WAITER]),
            ("Reports", "reports", role == Roles.ADMIN),
            ("Staff", "staff", role == Roles.ADMIN),
            ("Activity Log", "activity", role == Roles.ADMIN),
            ("My Orders", "my_orders", role == Roles.WAITER),
        ]

        nav_container = tk.Frame(sidebar, bg=Theme.BG_SECONDARY)
        nav_container.pack(fill="x", pady=10)

        for label, key, visible in nav_items:
            if not visible:
                continue
            btn = tk.Button(nav_container, text=label,
                           command=lambda k=key: self.navigate_to(k),
                           bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
                           relief="flat", cursor="hand2",
                           activebackground=Theme.BG_TERTIARY,
                           activeforeground=Theme.TEXT_PRIMARY,
                           anchor="w", padx=20, pady=10)
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        bottom_frame = tk.Frame(sidebar, bg=Theme.BG_SECONDARY)
        bottom_frame.pack(side="bottom", fill="x", pady=10)

        user_frame = tk.Frame(bottom_frame, bg=Theme.BG_TERTIARY, padx=15, pady=10)
        user_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.sidebar_user_label = tk.Label(user_frame, text=self.current_user["full_name"],
                                           bg=Theme.BG_TERTIARY, fg=Theme.TEXT_PRIMARY,
                                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"))
        self.sidebar_user_label.pack(anchor="w")

        self.sidebar_role_label = tk.Label(user_frame, text=self.current_user["role"].title(),
                                           bg=Theme.BG_TERTIARY, fg=Theme.TEXT_MUTED,
                                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL))
        self.sidebar_role_label.pack(anchor="w")

        logout_btn = tk.Button(bottom_frame, text="Sign Out",
                              command=self.logout,
                              bg=Theme.ACCENT_DANGER, fg=Theme.TEXT_ON_ACCENT,
                              font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"),
                              relief="flat", cursor="hand2",
                              activebackground="#ff4757",
                              padx=20, pady=8)
        logout_btn.pack(fill="x", padx=10)

    def refresh_current_user(self):
        if self.current_user:
            user = Database.get_user_by_id(self.current_user["id"])
            if user:
                self.current_user.update(user)
                self.sidebar_user_label.config(text=self.current_user["full_name"])
                self.sidebar_role_label.config(text=self.current_user["role"].title())
                if isinstance(self.current_view, LandingPage):
                    self.current_view.update_greeting()

    def navigate_to(self, destination):
        for key, btn in list(self.nav_buttons.items()):
            try:
                if key == destination:
                    btn.config(bg=Theme.BG_TERTIARY, fg=Theme.ACCENT_PRIMARY,
                              font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"))
                else:
                    btn.config(bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY,
                              font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))
            except tk.TclError:
                pass

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if destination == "landing":
            self.current_view = LandingPage(self.content_frame, self.current_user, self.navigate_to)
        elif destination == "tables":
            self.current_view = TableManager(self.content_frame, self.current_user, self.navigate_to)
        elif destination == "orders":
            self.current_view = OrderSystem(self.content_frame, self.current_user, self.navigate_to)
        elif destination == "kitchen":
            self.current_view = KitchenView(self.content_frame, self.current_user)
        elif destination == "menu":
            self.current_view = MenuManager(self.content_frame, self.current_user)
        elif destination == "billing":
            self.current_view = BillingSystem(self.content_frame, self.current_user)
        elif destination == "reports":
            self.current_view = AdminPanel(self.content_frame, self.current_user, self.refresh_current_user)
        elif destination == "staff":
            self.current_view = StaffView(self.content_frame, self.current_user)
        elif destination == "activity":
            self.current_view = ActivityLog(self.content_frame, self.current_user)
        elif destination == "my_orders":
            self.current_view = MyOrders(self.content_frame, self.current_user)

    def logout(self):
        if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
            if self.current_user:
                Database.log_activity(self.current_user["id"], "LOGOUT", "users", self.current_user["id"])
            self.current_user = None
            self.nav_buttons.clear()
            self.show_auth()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = RestaurantPOSApp()
    app.run()


if __name__ == "__main__":
    main()