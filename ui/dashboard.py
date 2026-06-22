import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QGraphicsDropShadowEffect, QMessageBox, QLineEdit,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QPalette
from services.menu_service import get_dashboard_stats
from assets.styles import (
    COLORS, app_stylesheet, primary_button,
    outline_button, sidebar_button_style
)


def make_shadow(blur=16, opacity=40, offset_y=4):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(0, 0, 0, opacity))
    shadow.setOffset(0, offset_y)
    return shadow


class GradientCard(QFrame):
    """Large gradient stat card like sample 2."""
    def __init__(self, title, value, subtitle, icon,
                 grad_start, grad_end, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 140)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {grad_start}, stop:1 {grad_end}
                );
                border-radius: 14px;
                border: none;
            }}
            QLabel {{ background: transparent; border: none; color: white; }}
        """)
        self.setGraphicsEffect(make_shadow(20, 60, 6))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(4)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 22))
        icon_lbl.setStyleSheet("color: rgba(255,255,255,0.9); background: transparent; border: none;")
        top.addWidget(icon_lbl)
        top.addStretch()

        val_lbl = QLabel(str(value))
        val_lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        val_lbl.setStyleSheet("color: white; background: transparent; border: none;")

        title_lbl = QLabel(title.upper())
        title_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_lbl.setStyleSheet(
            "color: rgba(255,255,255,0.75); letter-spacing: 1px; "
            "background: transparent; border: none;"
        )

        sub_lbl = QLabel(subtitle)
        sub_lbl.setFont(QFont("Segoe UI", 10))
        sub_lbl.setStyleSheet("color: rgba(255,255,255,0.65); background: transparent; border: none;")

        layout.addLayout(top)
        layout.addWidget(val_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)


class SmallStatCard(QFrame):
    """Smaller white stat card like sample 3."""
    def __init__(self, title, value, subtitle, icon,
                 icon_bg, icon_color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        self.setGraphicsEffect(make_shadow(12, 25, 3))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        icon_frame = QFrame()
        icon_frame.setFixedSize(46, 46)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {icon_bg};
                border-radius: 10px;
                border: none;
            }}
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI", 18))
        icon_lbl.setStyleSheet(f"color: {icon_color}; background: transparent;")
        icon_layout.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        val_lbl = QLabel(str(value))
        val_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        val_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 10))
        title_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")

        text_col.addWidget(val_lbl)
        text_col.addWidget(title_lbl)

        layout.addWidget(icon_frame)
        layout.addLayout(text_col)
        layout.addStretch()


class TopBar(QFrame):
    """Top navigation bar with search and user profile."""
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border']};
                border-radius: 0;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)

        # Search bar
        search_frame = QFrame()
        search_frame.setFixedHeight(38)
        search_frame.setFixedWidth(280)
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_layout.setSpacing(6)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("background: transparent; border: none; font-size: 13px;")

        search_input = QLineEdit()
        search_input.setPlaceholderText("Search anything...")
        search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
        """)

        shortcut = QLabel("⌘K")
        shortcut.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            background: {COLORS['border']};
            border-radius: 4px;
            padding: 1px 5px;
            font-size: 10px;
            border: none;
        """)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(search_input)
        search_layout.addWidget(shortcut)

        layout.addWidget(search_frame)
        layout.addStretch()

        # Notification button
        for icon in ["🌙", "🔔", "⛶"]:
            btn = QPushButton(icon)
            btn.setFixedSize(36, 36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 18px;
                    font-size: 14px;
                    color: {COLORS['text_secondary']};
                }}
                QPushButton:hover {{
                    background-color: {COLORS['border']};
                }}
            """)
            layout.addWidget(btn)

        # Divider
        div = QFrame()
        div.setFixedSize(1, 32)
        div.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")
        layout.addWidget(div)

        # User avatar + info
        initials = "".join([n[0].upper() for n in user['full_name'].split()[:2]])
        avatar = QLabel(initials)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        avatar.setStyleSheet(f"""
            background-color: {COLORS['accent']};
            color: white;
            border-radius: 18px;
            border: none;
        """)

        user_text = QVBoxLayout()
        user_text.setSpacing(0)
        name_lbl = QLabel(user['full_name'])
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; border: none;")
        role_lbl = QLabel(user['role'])
        role_lbl.setFont(QFont("Segoe UI", 9))
        role_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")
        user_text.addWidget(name_lbl)
        user_text.addWidget(role_lbl)

        layout.addWidget(avatar)
        layout.addLayout(user_text)

        chevron = QLabel("∨")
        chevron.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")
        layout.addWidget(chevron)


class DashboardHome(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(60000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        # Greeting
        hour = datetime.datetime.now().hour
        greeting = (
            "Good Morning" if hour < 12
            else "Good Afternoon" if hour < 17
            else "Good Evening"
        )
        first_name = self.user['full_name'].split()[0]

        greeting_row = QHBoxLayout()
        greet_col = QVBoxLayout()
        greet_col.setSpacing(2)

        greet_lbl = QLabel(f"☀️  {greeting}, {first_name}!")
        greet_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        greet_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        sub_lbl = QLabel(
            datetime.datetime.now().strftime("%A, %d %B %Y")
            + "  •  Hope your day is going great."
        )
        sub_lbl.setFont(QFont("Segoe UI", 11))
        sub_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")

        greet_col.addWidget(greet_lbl)
        greet_col.addWidget(sub_lbl)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(36)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(outline_button())
        refresh_btn.clicked.connect(self.refresh_stats)

        greeting_row.addLayout(greet_col)
        greeting_row.addStretch()
        greeting_row.addWidget(refresh_btn)

        # Section: Overview
        overview_lbl = QLabel("Overview")
        overview_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        overview_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        overview_sub = QLabel("Key performance indicators for today")
        overview_sub.setFont(QFont("Segoe UI", 11))
        overview_sub.setStyleSheet(f"color: {COLORS['text_secondary']};")

        # Large gradient cards row
        self.grad_cards_row = QHBoxLayout()
        self.grad_cards_row.setSpacing(16)

        # Small stat cards row
        self.small_cards_row = QHBoxLayout()
        self.small_cards_row.setSpacing(16)

        self.load_stats()

        # Quick actions
        actions_lbl = QLabel("Quick Actions")
        actions_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        actions_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        for label, icon, color, tip in [
            ("New Order",     "🛒", COLORS['accent'],  "Start a new customer order"),
            ("Menu Items",    "🍽", COLORS['blue'],    "Manage menu"),
            ("Sales Report",  "📊", COLORS['purple'],  "View reports"),
            ("Manage Users",  "👥", COLORS['warning'], "User management"),
        ]:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setFixedHeight(46)
            btn.setToolTip(tip)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['text_primary']};
                    border: 1.5px solid {COLORS['border']};
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: Segoe UI;
                    padding: 0 20px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    border-color: {color};
                    color: {color};
                    background-color: white;
                }}
            """)
            actions_row.addWidget(btn)

        layout.addLayout(greeting_row)
        layout.addWidget(overview_lbl)
        layout.addWidget(overview_sub)
        layout.addLayout(self.grad_cards_row)
        layout.addLayout(self.small_cards_row)
        layout.addWidget(actions_lbl)
        layout.addLayout(actions_row)
        layout.addStretch()

    def load_stats(self):
        for row in [self.grad_cards_row, self.small_cards_row]:
            while row.count():
                item = row.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        stats = get_dashboard_stats()

        # Gradient cards
        for title, value, subtitle, icon, g1, g2 in [
            ("Sales Today",  f"${stats['sales_today']:.2f}",
             "Total revenue today", "💰", "#16a34a", "#15803d"),
            ("Orders Today", str(stats['orders_today']),
             "Completed orders",    "🛒", "#7c3aed", "#6d28d9"),
            ("Menu Items",   str(stats['active_items']),
             "Items available",     "🍽", "#2563eb", "#1d4ed8"),
            ("Categories",   str(stats['active_categories']),
             "Active categories",   "📂", "#ea580c", "#c2410c"),
        ]:
            self.grad_cards_row.addWidget(
                GradientCard(title, value, subtitle, icon, g1, g2)
            )
        self.grad_cards_row.addStretch()

        # Small cards
        for title, value, subtitle, icon, ibg, icol in [
            ("Open Orders",   "0",  "Pending",        "📋",
             COLORS['accent_light'],  COLORS['accent']),
            ("Active Tables", "0",  "Occupied",       "🪑",
             COLORS['blue_light'],    COLORS['blue']),
            ("Low Stock",     "0",  "Items to reorder","⚠️",
             COLORS['orange_light'],  COLORS['orange']),
            ("Staff Online",  "1",  "Active sessions", "👥",
             COLORS['purple_light'],  COLORS['purple']),
        ]:
            card = SmallStatCard(title, value, subtitle, icon, ibg, icol)
            self.small_cards_row.addWidget(card)
        self.small_cards_row.addStretch()

    def refresh_stats(self):
        self.load_stats()


class DashboardWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Restaurant Management System")
        self.setMinimumSize(1200, 740)
        self.setStyleSheet(app_stylesheet())
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['sidebar']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Brand
        brand = QFrame()
        brand.setFixedHeight(64)
        brand.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['sidebar']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(20, 0, 20, 0)
        brand_layout.setSpacing(10)

        logo_frame = QFrame()
        logo_frame.setFixedSize(34, 34)
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['accent_light']};
                border-radius: 8px;
                border: none;
            }}
        """)
        logo_inner = QVBoxLayout(logo_frame)
        logo_inner.setContentsMargins(0, 0, 0, 0)
        try:
            from services.admin_service import get_all_settings as _gs2
            import os
            from PyQt6.QtGui import QPixmap
            _logo_path = _gs2().get("logo_path", "")
            if _logo_path and os.path.exists(_logo_path):
                _pixmap = QPixmap(_logo_path)
                if not _pixmap.isNull():
                    _scaled = _pixmap.scaled(
                        28, 28,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    logo_icon = QLabel()
                    logo_icon.setPixmap(_scaled)
                    logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    logo_icon.setStyleSheet(
                        "background: transparent; border: none;"
                    )
                else:
                    raise Exception("Invalid image")
            else:
                raise Exception("No logo")
        except Exception:
            logo_icon = QLabel("🍽")
            logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_icon.setFont(QFont("Segoe UI", 16))
            logo_icon.setStyleSheet(
                "background: transparent; border: none;"
            )
        logo_inner.addWidget(logo_icon)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        from services.admin_service import get_all_settings as _get_settings
        try:
            _rest_name = _get_settings().get("restaurant_name", "RestaurantPro")
        except Exception:
            _rest_name = "RestaurantPro"

        brand_name = QLabel(_rest_name)
        brand_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        brand_name.setStyleSheet(
            f"color: {COLORS['text_primary']}; background: transparent; border: none;"
        )
        brand_ver = QLabel("Enterprise v1.0")
        brand_ver.setFont(QFont("Segoe UI", 9))
        brand_ver.setStyleSheet(
            f"color: {COLORS['text_muted']}; background: transparent; border: none;"
        )
        brand_text.addWidget(brand_name)
        brand_text.addWidget(brand_ver)

        # Nav section helper
        def nav_section(label):
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            lbl.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                padding: 16px 16px 4px 16px;
                letter-spacing: 1px;
                background: transparent;
            """)
            return lbl

        self.nav_buttons = []

        sidebar_layout.addWidget(nav_section("MAIN"))

        def add_nav(icon, label, index):
            btn = QPushButton(f"  {label}")
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet(sidebar_button_style())
            btn.clicked.connect(lambda _, i=index: self.navigate(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        for label, index in [
            ("Dashboard", 0),
            ("Menu Management", 1),
            ("Point of Sale", 2),
            ("Table Manager", 3),
            ("Kitchen", 4),
            ("Inventory", 5),
            ("Suppliers", 6),
            ("Customers", 7),
            ("Reservations", 8),
        ]:
            add_nav("", label, index)

        sidebar_layout.addWidget(nav_section("MANAGEMENT"))

        for label, idx in [
            ("Reports", 9),
            ("Settings", 10),
        ]:
            add_nav("", label, idx)
        sidebar_layout.addStretch()

        # Profile at bottom
        profile = QFrame()
        profile.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-top: 1px solid {COLORS['border']};
                border-radius: 0;
            }}
        """)
        profile_layout = QVBoxLayout(profile)
        profile_layout.setContentsMargins(14, 12, 14, 12)
        profile_layout.setSpacing(8)

        p_top = QHBoxLayout()
        initials = "".join([n[0].upper() for n in self.user['full_name'].split()[:2]])
        avatar = QLabel(initials)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        avatar.setStyleSheet(f"""
            background-color: {COLORS['accent']};
            color: white;
            border-radius: 18px;
            border: none;
        """)

        p_text = QVBoxLayout()
        p_text.setSpacing(0)
        p_name = QLabel(self.user['full_name'])
        p_name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        p_name.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; border: none;")
        p_role = QLabel(self.user['role'])
        p_role.setFont(QFont("Segoe UI", 9))
        p_role.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")
        p_text.addWidget(p_name)
        p_text.addWidget(p_role)

        p_top.addWidget(avatar)
        p_top.addLayout(p_text)
        p_top.addStretch()

        logout_btn = QPushButton("⏻  Logout")
        logout_btn.setFixedHeight(32)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger_light']};
                color: {COLORS['danger']};
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: white;
            }}
        """)
        logout_btn.clicked.connect(self.logout)

        profile_layout.addLayout(p_top)
        profile_layout.addWidget(logout_btn)
        sidebar_layout.addWidget(profile)

        # ── Right side: topbar + stack ────────────────────────
        right_side = QVBoxLayout()
        right_side.setContentsMargins(0, 0, 0, 0)
        right_side.setSpacing(0)

        self.topbar = TopBar(self.user)
        right_side.addWidget(self.topbar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {COLORS['bg_primary']};")

        self.stack.addWidget(DashboardHome(self.user))

        from ui.menu_management import MenuManagementWidget
        self.stack.addWidget(MenuManagementWidget(self.user))

        # Page 2 — POS
        from ui.pos import POSWidget
        self.stack.addWidget(POSWidget(self.user))

        # Page 3 — Table Management
        from ui.table_management import TableManagementWidget
        self.stack.addWidget(TableManagementWidget(self.user))

        # Page 4 — Kitchen
        from ui.kitchen import KitchenWidget
        self.stack.addWidget(KitchenWidget(self.user))

        # Page 5 — Inventory
        from ui.inventory import InventoryWidget
        self.stack.addWidget(InventoryWidget(self.user))

        # Page 6 — Suppliers
        from ui.suppliers import SupplierWidget
        self.stack.addWidget(SupplierWidget(self.user))

        # Page 7 — Customers
        from ui.customers import CustomerWidget
        self.stack.addWidget(CustomerWidget(self.user))
        # Page 8 — Reservations
        from ui.reservations import ReservationsWidget
        self.stack.addWidget(ReservationsWidget(self.user))
        # Page 9 — Reports
        from ui.reports import ReportsWidget
        self.stack.addWidget(ReportsWidget(self.user))
        # Page 10 — Settings
        from ui.admin_settings import SettingsWidget
        self.stack.addWidget(SettingsWidget(self.user))
        # Pages 9 and 10 — Placeholders
        for name in ["Reports", "Settings"]:
            ph = QWidget()
            ph.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
            ph_layout = QVBoxLayout(ph)
            ph_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl = QLabel("🚧")
            icon_lbl.setFont(QFont("Segoe UI", 42))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("background: transparent;")
            txt_lbl = QLabel(f"{name} — Coming in next phase")
            txt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt_lbl.setFont(QFont("Segoe UI", 15))
            txt_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
            ph_layout.addWidget(icon_lbl)
            ph_layout.addWidget(txt_lbl)
            self.stack.addWidget(ph)

        right_side.addWidget(self.stack)

        right_widget = QWidget()
        right_widget.setLayout(right_side)

        root.addWidget(sidebar)
        root.addWidget(right_widget)

        self.navigate(0)

    def navigate(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from ui.login_window import LoginWindow
            self.login = LoginWindow()
            self.login.show()
            self.close()
