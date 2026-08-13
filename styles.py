"""
Savanna Restaurant POS System - Custom Styling
==============================================
Modern dark theme styling for Tkinter widgets using ttk and custom configurations.
Provides a cohesive, professional restaurant POS aesthetic.
"""

import tkinter as tk
from tkinter import ttk
from config import Theme

class StyleManager:
    """Manages application-wide styling and theme configuration."""

    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.configure_base()
        self.configure_widgets()

    def configure_base(self):
        """Configure base window and ttk theme."""
        self.root.configure(bg=Theme.BG_PRIMARY)
        self.root.option_add("*Background", Theme.BG_PRIMARY)
        self.root.option_add("*Foreground", Theme.TEXT_PRIMARY)
        self.root.option_add("*Font", f"{Theme.FONT_FAMILY} {Theme.FONT_SIZE_NORMAL}")
        self.style.theme_use("clam")
        self.style.configure(".", 
                           background=Theme.BG_PRIMARY,
                           foreground=Theme.TEXT_PRIMARY,
                           fieldbackground=Theme.BG_INPUT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL))

    def configure_widgets(self):
        """Configure all widget styles."""
        self.style.configure("Card.TFrame", background=Theme.BG_SECONDARY, relief="flat")
        self.style.configure("Elevated.TFrame", background=Theme.BG_TERTIARY, relief="flat")

        self.style.configure("Title.TLabel",
                           background=Theme.BG_PRIMARY, foreground=Theme.TEXT_PRIMARY,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold"))
        self.style.configure("Subtitle.TLabel",
                           background=Theme.BG_PRIMARY, foreground=Theme.TEXT_SECONDARY,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM))
        self.style.configure("Header.TLabel",
                           background=Theme.BG_SECONDARY, foreground=Theme.ACCENT_PRIMARY,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"))
        self.style.configure("Muted.TLabel",
                           background=Theme.BG_PRIMARY, foreground=Theme.TEXT_MUTED,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL))

        self.style.configure("Accent.TButton",
                           background=Theme.ACCENT_PRIMARY, foreground=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"), padding=10)
        self.style.map("Accent.TButton",
                      background=[("active", "#1ed760"), ("pressed", "#1aa34a")],
                      foreground=[("active", Theme.TEXT_ON_ACCENT)])

        self.style.configure("Success.TButton",
                           background=Theme.ACCENT_SUCCESS, foreground=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"), padding=10)
        self.style.map("Success.TButton",
                      background=[("active", "#2a9d54"), ("pressed", "#1a7a3a")])

        self.style.configure("Secondary.TButton",
                           background=Theme.ACCENT_SECONDARY, foreground=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), padding=8)
        self.style.map("Secondary.TButton",
                      background=[("active", "#6a6a6a"), ("pressed", "#4a4a4a")])

        self.style.configure("Danger.TButton",
                           background=Theme.ACCENT_DANGER, foreground=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL), padding=8)
        self.style.map("Danger.TButton",
                      background=[("active", "#e74c3c"), ("pressed", "#c0392b")])

        self.style.configure("Gold.TButton",
                           background=Theme.ACCENT_GOLD, foreground=Theme.BG_PRIMARY,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"), padding=10)

        self.style.configure("TableFree.TButton",
                           background=Theme.TABLE_FREE, foreground=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"), padding=15)
        self.style.map("TableFree.TButton", background=[("active", "#2a9d54")])

        self.style.configure("TableOccupied.TButton",
                           background=Theme.TABLE_OCCUPIED, foreground=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"), padding=15)
        self.style.map("TableOccupied.TButton", background=[("active", "#e74c3c")])

        self.style.configure("TableReserved.TButton",
                           background=Theme.TABLE_RESERVED, foreground=Theme.TEXT_ON_ACCENT,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"), padding=15)

        self.style.configure("Custom.TEntry",
                           fieldbackground=Theme.BG_INPUT, foreground=Theme.TEXT_PRIMARY,
                           insertcolor=Theme.TEXT_PRIMARY, padding=8)

        self.style.configure("Custom.TCombobox",
                           fieldbackground=Theme.BG_INPUT, foreground=Theme.TEXT_PRIMARY,
                           selectbackground=Theme.ACCENT_PRIMARY,
                           selectforeground=Theme.TEXT_ON_ACCENT)

        self.style.configure("Custom.Treeview",
                           background=Theme.BG_SECONDARY, foreground=Theme.TEXT_PRIMARY,
                           fieldbackground=Theme.BG_SECONDARY, rowheight=30)
        self.style.configure("Custom.Treeview.Heading",
                           background=Theme.BG_TERTIARY, foreground=Theme.ACCENT_PRIMARY,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"), padding=8)
        self.style.map("Custom.Treeview",
                      background=[("selected", Theme.ACCENT_PRIMARY)],
                      foreground=[("selected", Theme.TEXT_ON_ACCENT)])

        self.style.configure("Custom.TNotebook", background=Theme.BG_PRIMARY, tabmargins=[2, 5, 2, 0])
        self.style.configure("Custom.TNotebook.Tab",
                           background=Theme.BG_TERTIARY, foreground=Theme.TEXT_SECONDARY,
                           font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), padding=[15, 8])
        self.style.map("Custom.TNotebook.Tab",
                      background=[("selected", Theme.ACCENT_PRIMARY)],
                      foreground=[("selected", Theme.TEXT_ON_ACCENT)],
                      expand=[("selected", [1, 1, 1, 0])])

        self.style.configure("Custom.Horizontal.TProgressbar",
                           background=Theme.ACCENT_PRIMARY, troughcolor=Theme.BG_TERTIARY,
                           borderwidth=0, thickness=8)

        self.style.configure("Custom.TSeparator", background=Theme.BG_TERTIARY)

    @staticmethod
    def create_rounded_button(parent, text, command, bg_color, fg_color, 
                             font_size=Theme.FONT_SIZE_NORMAL, width=15, height=1):
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg=fg_color,
                       font=(Theme.FONT_FAMILY, font_size, "bold"),
                       relief="flat", cursor="hand2",
                       activebackground=bg_color, activeforeground=fg_color,
                       width=width, height=height, bd=0, highlightthickness=0)
        return btn

    @staticmethod
    def create_status_badge(parent, text, color):
        badge = tk.Label(parent, text=text, bg=color, fg=Theme.TEXT_ON_ACCENT,
                        font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"),
                        padx=8, pady=2, relief="flat")
        return badge

    @staticmethod
    def create_card_frame(parent, title=""):
        card = tk.Frame(parent, bg=Theme.BG_SECONDARY, relief="flat", bd=1)
        card.configure(highlightbackground=Theme.BG_TERTIARY, highlightthickness=1)

        if title:
            title_label = tk.Label(card, text=title, bg=Theme.BG_SECONDARY, fg=Theme.ACCENT_PRIMARY,
                                  font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_MEDIUM, "bold"),
                                  padx=10, pady=8)
            title_label.pack(fill="x")
            separator = tk.Frame(card, bg=Theme.BG_TERTIARY, height=1)
            separator.pack(fill="x", padx=10)

        return card

    @staticmethod
    def format_currency(amount):
        return f"KSh {amount:,.2f}"

    @staticmethod
    def get_status_color(status):
        status_colors = {
            "free": Theme.TABLE_FREE,
            "occupied": Theme.TABLE_OCCUPIED,
            "reserved": Theme.TABLE_RESERVED,
            "pending": Theme.ORDER_PENDING,
            "preparing": Theme.ORDER_PREPARING,
            "ready": Theme.ORDER_READY,
            "served": Theme.ORDER_SERVED,
            "paid": Theme.ORDER_PAID,
            "cancelled": Theme.ORDER_CANCELLED
        }
        return status_colors.get(status.lower(), Theme.TEXT_MUTED)


class ScrollableFrame(tk.Frame):
    """A scrollable frame widget."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=Theme.BG_PRIMARY, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Theme.BG_PRIMARY)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")