from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox,
    QCheckBox, QToolButton, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, QEvent, QSettings
from PyQt6.QtGui import QFont, QColor
from services.auth_service import authenticate_user, log_action
from assets.styles import COLORS, primary_button


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("QuickEats", "RestaurantManagementSystem")
        self.setWindowTitle("Restaurant Management System")
        self.setFixedSize(560, 680)
        self.setStyleSheet(f"""
            LoginWindow {{
                background-color: {COLORS['bg_primary']};
                background-image: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc,
                    stop:0.48 #eef7f1,
                    stop:1 #edf4ff
                );
            }}
        """)
        self.setup_ui()
        self.load_saved_credentials()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 34, 40, 28)
        main_layout.setSpacing(18)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo_frame = QFrame()
        logo_frame.setFixedSize(58, 58)
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['accent']};
                border-radius: 8px;
                border: 1px solid {COLORS['accent_hover']};
            }}
        """)
        logo_inner = QVBoxLayout(logo_frame)
        logo_inner.setContentsMargins(0, 0, 0, 0)
        logo_icon = QLabel("RM")
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        logo_icon.setStyleSheet("background: transparent; border: none; color: white;")
        logo_inner.addWidget(logo_icon)

        try:
            from services.admin_service import get_all_settings
            _s = get_all_settings()
            _name = _s.get("restaurant_name", "RestaurantPro")
        except Exception:
            _name = "RestaurantPro"

        app_name = QLabel(_name)
        app_name.setFont(QFont("Segoe UI", 23, QFont.Weight.Bold))
        app_name.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")

        subtitle = QLabel("Secure staff access for daily restaurant operations")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setWordWrap(True)
        subtitle.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")

        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        title_column.addWidget(app_name)
        title_column.addWidget(subtitle)

        status_badge = QLabel("Staff Login")
        status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_badge.setFixedSize(92, 28)
        status_badge.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['accent_light']};
                color: {COLORS['accent_text']};
                border-radius: 8px;
                padding: 4px 10px;
            }}
        """)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(14)
        logo_row.addWidget(logo_frame)
        logo_row.addLayout(title_column, 1)
        logo_row.addWidget(status_badge, 0, Qt.AlignmentFlag.AlignTop)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet(f"""
            QFrame#loginCard {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border_strong']};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(15, 23, 42, 22))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(30, 28, 30, 28)

        form_title = QLabel("Welcome Back")
        form_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        form_title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; border: none;")

        form_hint = QLabel("Enter your username and password to open the dashboard.")
        form_hint.setFont(QFont("Segoe UI", 10))
        form_hint.setWordWrap(True)
        form_hint.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent; border: none; margin-bottom: 8px;"
        )

        input_style = f"""
            QLineEdit {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 14px;
                color: {COLORS['text_primary']};
                font-size: 14px;
                font-family: Segoe UI;
                selection-background-color: {COLORS['accent_light']};
            }}
            QLineEdit:hover {{
                border: 1px solid {COLORS['border_strong']};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {COLORS['accent']};
                background-color: white;
            }}
        """

        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        username_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent; border: none;"
        )

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(48)
        self.username_input.setStyleSheet(input_style)

        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        password_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent; border: none;"
        )

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(48)
        self.password_input.setStyleSheet(input_style)
        self.password_input.returnPressed.connect(self.handle_login)
        self.password_input.installEventFilter(self)

        self.password_toggle = QToolButton()
        self.password_toggle.setText("Show")
        self.password_toggle.setFixedSize(54, 48)
        self.password_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.password_toggle.setStyleSheet(f"""
            QToolButton {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_secondary']};
                font-size: 11px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QToolButton:hover {{
                background-color: {COLORS['accent_light']};
                color: {COLORS['accent_text']};
                border-color: {COLORS['accent_light']};
            }}
        """)
        self.password_toggle.setToolTip("Show password")
        self.password_toggle.clicked.connect(self.toggle_password_visibility)

        password_container = QHBoxLayout()
        password_container.setSpacing(8)
        password_container.setContentsMargins(0, 0, 0, 0)
        password_container.addWidget(self.password_input)
        password_container.addWidget(self.password_toggle)

        self.caps_lock_label = QLabel("")
        self.caps_lock_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.caps_lock_label.setFont(QFont("Segoe UI", 10))
        self.caps_lock_label.setStyleSheet(
            f"color: {COLORS['warning']}; background: transparent; margin-bottom: 4px;"
        )
        self.caps_lock_label.setVisible(False)

        self.remember_check = QCheckBox("Remember me")
        self.remember_check.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
                background: transparent;
                border: none;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
            }}
        """)

        self.forgot_password_btn = QPushButton("Forgot password?")
        self.forgot_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forgot_password_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLORS['accent']};
                font-size: 12px;
                font-weight: 600;
                padding: 0 2px;
            }}
            QPushButton:hover {{
                color: {COLORS['accent_hover']};
            }}
        """)
        self.forgot_password_btn.clicked.connect(self.show_forgot_password_info)

        remember_row = QHBoxLayout()
        remember_row.setContentsMargins(0, 0, 0, 0)
        remember_row.setSpacing(12)
        remember_row.addWidget(self.remember_check)
        remember_row.addStretch()
        remember_row.addWidget(self.forgot_password_btn)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setFixedHeight(34)
        self.error_label.setStyleSheet(
            f"color: {COLORS['danger']}; font-size: 12px; "
            f"background: transparent; border: none;"
        )

        self.login_btn = QPushButton("Sign In")
        self.login_btn.setFixedHeight(54)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet(primary_button() + """
            QPushButton {
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)

        card_layout.addWidget(form_title)
        card_layout.addWidget(form_hint)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(password_label)
        card_layout.addLayout(password_container)
        card_layout.addWidget(self.caps_lock_label)
        card_layout.addLayout(remember_row)
        card_layout.addWidget(self.error_label)
        card_layout.addWidget(self.login_btn)

        footer = QLabel("Restaurant Management System  |  v1.0")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet(
            f"color: {COLORS['text_muted']}; margin-top: 24px; background: transparent;"
        )

        main_layout.addLayout(logo_row)
        main_layout.addSpacing(12)
        main_layout.addWidget(card)
        main_layout.addStretch()
        main_layout.addWidget(footer)
        self.setLayout(main_layout)

    def load_saved_credentials(self):
        username = self.settings.value("login/username", "")
        remember = self.settings.value("login/remember", False, type=bool)
        self.username_input.setText(username)
        self.remember_check.setChecked(remember)

    def save_credentials(self):
        if self.remember_check.isChecked():
            self.settings.setValue("login/username", self.username_input.text().strip())
            self.settings.setValue("login/remember", True)
        else:
            self.settings.setValue("login/username", "")
            self.settings.setValue("login/remember", False)

    def eventFilter(self, obj, event):
        if obj is self.password_input and event.type() == QEvent.Type.KeyPress:
            modifiers = event.modifiers()
            text = event.text()
            shift_pressed = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
            caps_on = bool(text and text.isalpha() and text.isupper() and not shift_pressed)
            self.caps_lock_label.setVisible(caps_on)
        return super().eventFilter(obj, event)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.password_toggle.setText("Hide")
            self.password_toggle.setToolTip("Hide password")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_toggle.setText("Show")
            self.password_toggle.setToolTip("Show password")

    def show_forgot_password_info(self):
        QMessageBox.information(
            self,
            "Forgot Password",
            "Please contact your administrator to reset your password."
        )

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_label.setText("Please enter both username and password.")
            return

        self.login_btn.setText("Signing in...")
        self.login_btn.setEnabled(False)

        user, error = authenticate_user(username, password)

        if user:
            self.save_credentials()
            log_action(user["user_id"], "LOGIN", "users", user["user_id"])
            self.error_label.setText("")
            self.open_dashboard(user)
        else:
            self.error_label.setText(error or "Unable to sign in. Please try again.")
            self.login_btn.setText("Sign In")
            self.login_btn.setEnabled(True)

    def open_dashboard(self, user):
        from ui.dashboard import DashboardWindow
        self.dashboard = DashboardWindow(user)
        self.dashboard.show()
        self.close()
