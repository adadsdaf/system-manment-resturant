from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QMessageBox,
    QGraphicsDropShadowEffect, QTabWidget, QMenu,
    QDateEdit, QSpinBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QCursor
from services.customer_service import (
    get_all_customers, add_customer, update_customer,
    toggle_customer_status, get_customer_orders,
    get_loyalty_transactions, add_loyalty_points,
    redeem_loyalty_points, get_customer_stats
)
from assets.styles import COLORS, primary_button, outline_button, table_stylesheet


# ── Customer dialog ───────────────────────────────────────────
class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle(
            "Edit Customer" if customer else "Add Customer"
        )
        self.setFixedSize(440, 420)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
            }}
            QLabel {{
                background: transparent;
                color: {COLORS['text_primary']};
                font-family: Segoe UI;
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel(
            "Edit Customer" if self.customer
            else "Add New Customer"
        )
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        form = QFormLayout()
        form.setSpacing(12)

        input_style = f"""
            QLineEdit, QDateEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QDateEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.name_input    = QLineEdit()
        self.phone_input   = QLineEdit()
        self.email_input   = QLineEdit()
        self.address_input = QLineEdit()

        for widget, placeholder in [
            (self.name_input,    "e.g. John Doe"),
            (self.phone_input,   "e.g. +254 712 345 678"),
            (self.email_input,   "e.g. john@email.com"),
            (self.address_input, "e.g. Nairobi, Kenya"),
        ]:
            widget.setPlaceholderText(placeholder)
            widget.setFixedHeight(40)
            widget.setStyleSheet(input_style)

        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate(1990, 1, 1))
        self.dob_input.setFixedHeight(40)
        self.dob_input.setStyleSheet(input_style)
        self.dob_input.setDisplayFormat("dd/MM/yyyy")

        for lbl, widget in [
            ("Full Name *",   self.name_input),
            ("Phone",         self.phone_input),
            ("Email",         self.email_input),
            ("Address",       self.address_input),
            ("Date of Birth", self.dob_input),
        ]:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
            form.addRow(l, widget)

        if self.customer:
            self.name_input.setText(self.customer[1])
            self.phone_input.setText(self.customer[2] or "")
            self.email_input.setText(self.customer[3] or "")
            self.address_input.setText(self.customer[4] or "")
            if self.customer[5]:
                try:
                    import datetime
                    dob = self.customer[5]
                    if hasattr(dob, 'year'):
                        self.dob_input.setDate(
                            QDate(dob.year, dob.month, dob.day)
                        )
                except Exception:
                    pass

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Customer")
        save_btn.setFixedHeight(42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(primary_button())
        save_btn.clicked.connect(self.save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)

        layout.addWidget(title)
        layout.addWidget(div)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(btn_row)

    def save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self, "Validation",
                "Full name is required."
            )
            return
        dob = self.dob_input.date().toString("yyyy-MM-dd")
        self.result_data = {
            "full_name":     name,
            "phone":         self.phone_input.text().strip(),
            "email":         self.email_input.text().strip(),
            "address":       self.address_input.text().strip(),
            "date_of_birth": dob,
        }
        self.accept()


# ── Customer detail dialog ────────────────────────────────────
class CustomerDetailDialog(QDialog):
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle(f"Customer — {customer[1]}")
        self.setMinimumSize(560, 520)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
            }}
            QLabel {{
                background: transparent;
                color: {COLORS['text_primary']};
                font-family: Segoe UI;
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        avatar = QLabel(self.customer[1][0].upper())
        avatar.setFixedSize(52, 52)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        avatar.setStyleSheet(f"""
            background-color: {COLORS['accent_light']};
            color: {COLORS['accent']};
            border-radius: 26px;
            border: none;
        """)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        name_lbl = QLabel(self.customer[1])
        name_lbl.setFont(
            QFont("Segoe UI", 16, QFont.Weight.Bold)
        )
        name_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )
        contact_lbl = QLabel(
            f"{self.customer[2] or '—'}  •  "
            f"{self.customer[3] or '—'}"
        )
        contact_lbl.setFont(QFont("Segoe UI", 11))
        contact_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        info_col.addWidget(name_lbl)
        info_col.addWidget(contact_lbl)

        header_row.addWidget(avatar)
        header_row.addLayout(info_col)
        header_row.addStretch()

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        for label, value, color in [
            ("Total Orders",
             str(self.customer[10]), COLORS['blue']),
            ("Total Spent",
             f"${float(self.customer[11]):.2f}",
             COLORS['accent']),
            ("Loyalty Points",
             str(self.customer[8]), COLORS['warning']),
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_tertiary']};
                    border-radius: 10px;
                    border: 1px solid {COLORS['border']};
                }}
                QLabel {{
                    background: transparent;
                    border: none;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 10, 14, 10)
            card_layout.setSpacing(2)
            val_lbl = QLabel(value)
            val_lbl.setFont(
                QFont("Segoe UI", 16, QFont.Weight.Bold)
            )
            val_lbl.setStyleSheet(f"color: {color};")
            lbl_lbl = QLabel(label)
            lbl_lbl.setFont(QFont("Segoe UI", 10))
            lbl_lbl.setStyleSheet(
                f"color: {COLORS['text_muted']};"
            )
            card_layout.addWidget(val_lbl)
            card_layout.addWidget(lbl_lbl)
            stats_row.addWidget(card)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['bg_tertiary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 7px 16px;
                font-size: 12px;
                font-weight: 600;
                font-family: Segoe UI;
                margin-right: 3px;
            }}
            QTabBar::tab:selected {{
                color: {COLORS['accent']};
                border-bottom: 2px solid {COLORS['accent']};
                background-color: {COLORS['bg_tertiary']};
            }}
        """)

        # Orders tab
        orders_tab   = QWidget()
        orders_tab.setStyleSheet(
            f"background-color: {COLORS['bg_tertiary']};"
        )
        orders_layout = QVBoxLayout(orders_tab)
        orders_layout.setContentsMargins(8, 8, 8, 8)

        orders_table = QTableWidget()
        orders_table.setColumnCount(4)
        orders_table.setHorizontalHeaderLabels([
            "ORDER #", "TOTAL", "PAYMENT", "DATE"
        ])
        orders_table.setStyleSheet(
            table_stylesheet(
                background_color=COLORS['bg_tertiary'],
                header_background=COLORS['bg_secondary'],
                item_padding="8px 10px",
                font_size="12px",
                header_padding="8px",
            )
        )
        orders_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        orders_table.verticalHeader().setVisible(False)
        orders_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        orders_table.setShowGrid(False)

        orders = get_customer_orders(self.customer[0])
        orders_table.setRowCount(len(orders))
        for idx, o in enumerate(orders):
            orders_table.setRowHeight(idx, 40)
            orders_table.setItem(
                idx, 0, QTableWidgetItem(f"#{o[0]}")
            )
            orders_table.setItem(
                idx, 1,
                QTableWidgetItem(f"${float(o[1]):.2f}")
            )
            orders_table.setItem(
                idx, 2, QTableWidgetItem(o[2])
            )
            orders_table.setItem(
                idx, 3, QTableWidgetItem(str(o[4])[:16])
            )

        orders_layout.addWidget(orders_table)
        tabs.addTab(orders_tab, "🛒  Order History")

        # Loyalty tab
        loyalty_tab = QWidget()
        loyalty_tab.setStyleSheet(
            f"background-color: {COLORS['bg_tertiary']};"
        )
        loyalty_layout = QVBoxLayout(loyalty_tab)
        loyalty_layout.setContentsMargins(8, 8, 8, 8)
        loyalty_layout.setSpacing(8)

        # Redeem points button
        redeem_btn = QPushButton(
            f"🎁  Redeem Points  "
            f"(Balance: {self.customer[8]} pts)"
        )
        redeem_btn.setFixedHeight(38)
        redeem_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        redeem_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: #b45309;
            }}
        """)
        redeem_btn.clicked.connect(
            lambda: self.redeem_points()
        )

        loyalty_table = QTableWidget()
        loyalty_table.setColumnCount(4)
        loyalty_table.setHorizontalHeaderLabels([
            "TYPE", "POINTS", "REFERENCE", "DATE"
        ])
        loyalty_table.setStyleSheet(
            table_stylesheet(
                background_color=COLORS['bg_tertiary'],
                header_background=COLORS['bg_secondary'],
                item_padding="8px 10px",
                font_size="12px",
                header_padding="8px",
            )
        )
        loyalty_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        loyalty_table.verticalHeader().setVisible(False)
        loyalty_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        loyalty_table.setShowGrid(False)

        lt = get_loyalty_transactions(self.customer[0])
        loyalty_table.setRowCount(len(lt))
        for idx, t in enumerate(lt):
            loyalty_table.setRowHeight(idx, 40)
            type_item = QTableWidgetItem(t[1])
            type_item.setForeground(
                QColor(COLORS['accent'] if t[1] == 'Earned'
                       else COLORS['danger'])
            )
            type_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            loyalty_table.setItem(idx, 0, type_item)

            pts_item = QTableWidgetItem(
                f"+{t[2]}" if t[1] == 'Earned'
                else f"-{t[2]}"
            )
            pts_item.setForeground(
                QColor(COLORS['accent'] if t[1] == 'Earned'
                       else COLORS['danger'])
            )
            loyalty_table.setItem(idx, 1, pts_item)
            loyalty_table.setItem(
                idx, 2, QTableWidgetItem(t[3] or "—")
            )
            loyalty_table.setItem(
                idx, 3, QTableWidgetItem(str(t[5])[:16])
            )

        loyalty_layout.addWidget(redeem_btn)
        loyalty_layout.addWidget(loyalty_table)
        tabs.addTab(loyalty_tab, "⭐  Loyalty Points")

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(primary_button())
        close_btn.clicked.connect(self.accept)

        layout.addLayout(header_row)
        layout.addLayout(stats_row)
        layout.addWidget(div)
        layout.addWidget(tabs)
        layout.addWidget(close_btn)

    def redeem_points(self):
        balance = self.customer[8]
        if balance <= 0:
            QMessageBox.warning(
                self, "No Points",
                "This customer has no loyalty points."
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Redeem Points")
        dialog.setFixedSize(340, 220)
        dialog.setStyleSheet(
            f"QDialog {{ background-color: {COLORS['bg_secondary']}; }}"
            f"QLabel {{ background: transparent; color: {COLORS['text_primary']}; font-family: Segoe UI; }}"
        )
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(24, 24, 24, 24)
        dlg_layout.setSpacing(14)

        title = QLabel("Redeem Loyalty Points")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        bal_lbl = QLabel(f"Available Balance: {balance} points")
        bal_lbl.setFont(QFont("Segoe UI", 11))
        bal_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        spin = QSpinBox()
        spin.setRange(1, balance)
        spin.setValue(min(100, balance))
        spin.setFixedHeight(40)
        spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QSpinBox:focus {{
                border-color: {COLORS['accent']};
            }}
        """)

        notes_input = QLineEdit()
        notes_input.setPlaceholderText("Reason (optional)")
        notes_input.setFixedHeight(38)
        notes_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)

        confirm_btn = QPushButton("Redeem")
        confirm_btn.setFixedHeight(40)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(
            primary_button(COLORS['warning'])
        )
        confirm_btn.clicked.connect(dialog.accept)

        dlg_layout.addWidget(title)
        dlg_layout.addWidget(bal_lbl)
        dlg_layout.addWidget(spin)
        dlg_layout.addWidget(notes_input)
        dlg_layout.addWidget(confirm_btn)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            success = redeem_loyalty_points(
                self.customer[0],
                spin.value(),
                notes_input.text().strip()
            )
            if success:
                QMessageBox.information(
                    self, "Success",
                    f"{spin.value()} points redeemed successfully."
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to redeem points."
                )


# ── Main customer widget ──────────────────────────────────────
class CustomerWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user      = user
        self.customers = []
        self.setStyleSheet(
            f"background-color: {COLORS['bg_primary']};"
        )
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Header ────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_col  = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Customer Management")
        page_title.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        page_title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        page_sub = QLabel(
            "Manage customers and loyalty points"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        add_btn = QPushButton("⊕  Add Customer")
        add_btn.setFixedHeight(40)
        add_btn.setFixedWidth(150)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(primary_button())
        add_btn.clicked.connect(self.add_customer)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(outline_button())
        refresh_btn.clicked.connect(self.load_data)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(refresh_btn)
        header_row.addWidget(add_btn)

        # ── Stats row ─────────────────────────────────────────
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)

        # ── Toolbar ───────────────────────────────────────────
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(14, 0, 14, 0)
        toolbar_layout.setSpacing(8)

        for label in ["CSV", "XLS", "PDF", "Print"]:
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    color: {COLORS['text_secondary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 600;
                    font-family: Segoe UI;
                    padding: 0 12px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent_light']};
                    color: {COLORS['accent_text']};
                    border-color: {COLORS['accent']};
                }}
            """)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()

        search_frame = QFrame()
        search_frame.setFixedHeight(34)
        search_frame.setFixedWidth(220)
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 0, 10, 0)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(
            "background: transparent; border: none; font-size: 12px;"
        )

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search customers..."
        )
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
        """)
        self.search_input.textChanged.connect(
            self.filter_customers
        )

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_frame)

        # ── Table ─────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "FULL NAME", "PHONE",
            "ORDERS", "TOTAL SPENT",
            "LOYALTY PTS", "STATUS", "ACTIONS"
        ])
        self.table.setStyleSheet(
            table_stylesheet()
        )

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 110)
        self.table.setColumnWidth(7, 80)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            5, QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            6, QHeaderView.ResizeMode.Fixed
        )
        header.setSectionResizeMode(
            7, QHeaderView.ResizeMode.Fixed
        )
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.table.horizontalHeaderItem(1).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.table.horizontalHeaderItem(2).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.table.horizontalHeaderItem(3).setTextAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.table.horizontalHeaderItem(4).setTextAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.table.horizontalHeaderItem(5).setTextAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        header.setStretchLastSection(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setShowGrid(False)

        layout.addLayout(header_row)
        layout.addLayout(self.stats_row)
        layout.addWidget(toolbar)
        layout.addWidget(self.table)

    def load_data(self):
        self.customers = get_all_customers()
        stats          = get_customer_stats()

        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, value, color in [
            ("Total Customers",
             stats.get("total", 0),         COLORS['blue']),
            ("Active Customers",
             stats.get("active", 0),        COLORS['accent']),
            ("Birthdays Today",
             stats.get("birthdays_today", 0), COLORS['danger']),
            ("Total Loyalty Points",
             stats.get("total_points", 0),  COLORS['warning']),
        ]:
            pill = self.build_stat_pill(label, value, color)
            self.stats_row.addWidget(pill)
        self.stats_row.addStretch()

        self.populate_table(self.customers)

    def populate_table(self, customers):
        self.table.setRowCount(0)
        self.table.setRowCount(len(customers))

        for idx, c in enumerate(customers):
            self.table.setRowHeight(idx, 52)

            id_item = QTableWidgetItem(str(c[0]))
            id_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            id_item.setForeground(
                QColor(COLORS['text_muted'])
            )
            self.table.setItem(idx, 0, id_item)

            name_item = QTableWidgetItem(c[1])
            name_item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
            name_item.setForeground(QColor(COLORS['accent']))
            self.table.setItem(idx, 1, name_item)

            phone_item = QTableWidgetItem(c[2] or "—")
            phone_item.setForeground(
                QColor(COLORS['text_secondary'])
            )
            self.table.setItem(idx, 2, phone_item)

            orders_item = QTableWidgetItem(str(c[10]))
            orders_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self.table.setItem(idx, 3, orders_item)

            spent_item = QTableWidgetItem(
                f"${float(c[11]):.2f}"
            )
            spent_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            spent_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            spent_item.setForeground(
                QColor(COLORS['text_primary'])
            )
            self.table.setItem(idx, 4, spent_item)

            pts_item = QTableWidgetItem(f"{c[8]} pts")
            pts_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            pts_item.setForeground(QColor(COLORS['warning']))
            pts_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            self.table.setItem(idx, 5, pts_item)

            # Status badge
            is_active    = c[6]
            badge_widget = QWidget()
            badge_widget.setStyleSheet("background: transparent;")
            badge_layout = QHBoxLayout(badge_widget)
            badge_layout.setContentsMargins(6, 0, 6, 0)
            badge_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            badge = QLabel("Active" if is_active else "Inactive")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedHeight(24)
            badge.setFont(
                QFont("Segoe UI", 10, QFont.Weight.Bold)
            )
            badge.setStyleSheet(f"""
                color: {COLORS['accent'] if is_active else COLORS['danger']};
                background-color: {COLORS['accent_light'] if is_active else COLORS['danger_light']};
                border-radius: 10px;
                padding: 0 10px;
                border: none;
            """)
            badge_layout.addWidget(badge)
            self.table.setCellWidget(idx, 6, badge_widget)

            # Actions
            dots_btn = QPushButton("⋮")
            dots_btn.setFixedSize(32, 32)
            dots_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            dots_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    font-size: 18px;
                    font-weight: bold;
                    padding-bottom: 4px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_tertiary']};
                }}
            """)
            dots_btn.clicked.connect(
                lambda _, cust=c:
                self.show_action_menu(cust)
            )

            cell = QWidget()
            cell.setStyleSheet("background: transparent;")
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            cell_layout.addWidget(dots_btn)
            self.table.setCellWidget(idx, 7, cell)

    def show_action_menu(self, customer):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 6px;
                font-family: Segoe UI;
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 6px;
                color: {COLORS['text_primary']};
            }}
            QMenu::item:selected {{
                background-color: {COLORS['bg_tertiary']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {COLORS['border']};
                margin: 4px 8px;
            }}
        """)

        view_action   = menu.addAction("👁   View Details")
        edit_action   = menu.addAction("✏️   Edit Customer")
        points_action = menu.addAction("⭐  Manage Points")
        menu.addSeparator()
        toggle_label  = (
            "🔴  Deactivate" if customer[6]
            else "🟢  Activate"
        )
        toggle_action = menu.addAction(toggle_label)

        action = menu.exec(QCursor.pos())

        if action == view_action:
            self.view_customer(customer)
        elif action == edit_action:
            self.edit_customer(customer)
        elif action == points_action:
            self.manage_points(customer)
        elif action == toggle_action:
            self.toggle_customer(customer)

    def filter_customers(self, text):
        filtered = [
            c for c in self.customers
            if text.lower() in c[1].lower()
            or text.lower() in (c[2] or "").lower()
        ]
        self.populate_table(filtered)

    def view_customer(self, customer):
        dialog = CustomerDetailDialog(customer, self)
        dialog.exec()
        self.load_data()

    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d          = dialog.result_data
            customer_id = add_customer(
                d['full_name'], d['phone'], d['email'],
                d['address'], d['date_of_birth']
            )
            if customer_id:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to add customer. "
                    "Phone number may already exist."
                )

    def edit_customer(self, customer):
        dialog = CustomerDialog(self, customer=customer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = update_customer(
                customer[0], d['full_name'], d['phone'],
                d['email'], d['address'], d['date_of_birth']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to update customer."
                )

    def toggle_customer(self, customer):
        success = toggle_customer_status(
            customer[0], customer[6]
        )
        if success:
            self.load_data()

    def manage_points(self, customer):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Loyalty Points")
        dialog.setFixedSize(360, 260)
        dialog.setStyleSheet(
            f"QDialog {{ background-color: {COLORS['bg_secondary']}; }}"
            f"QLabel {{ background: transparent; color: {COLORS['text_primary']}; font-family: Segoe UI; }}"
        )
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(24, 24, 24, 24)
        dlg_layout.setSpacing(14)

        title = QLabel(
            f"Add Points — {customer[1]}"
        )
        title.setFont(
            QFont("Segoe UI", 14, QFont.Weight.Bold)
        )
        bal_lbl = QLabel(
            f"Current Balance: {customer[8]} points"
        )
        bal_lbl.setFont(QFont("Segoe UI", 11))
        bal_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        spin = QSpinBox()
        spin.setRange(1, 99999)
        spin.setValue(10)
        spin.setFixedHeight(40)
        spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QSpinBox:focus {{
                border-color: {COLORS['accent']};
            }}
        """)

        ref_input = QLineEdit()
        ref_input.setPlaceholderText(
            "Reference (optional)"
        )
        ref_input.setFixedHeight(38)
        ref_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)

        confirm_btn = QPushButton("Add Points")
        confirm_btn.setFixedHeight(40)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(primary_button())
        confirm_btn.clicked.connect(dialog.accept)

        dlg_layout.addWidget(title)
        dlg_layout.addWidget(bal_lbl)
        dlg_layout.addWidget(spin)
        dlg_layout.addWidget(ref_input)
        dlg_layout.addStretch()
        dlg_layout.addWidget(confirm_btn)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            success = add_loyalty_points(
                customer[0], spin.value(),
                ref_input.text().strip(),
                "Manual adjustment"
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to add points."
                )

    def build_stat_pill(self, label, value, color):
        frame = QFrame()
        frame.setFixedHeight(56)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        row = QHBoxLayout(frame)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(10)

        dot = QLabel("●")
        dot.setFont(QFont("Segoe UI", 14))
        dot.setStyleSheet(f"color: {color};")

        col = QVBoxLayout()
        col.setSpacing(0)

        val_lbl = QLabel(str(value))
        val_lbl.setFont(
            QFont("Segoe UI", 14, QFont.Weight.Bold)
        )
        val_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        txt_lbl = QLabel(label)
        txt_lbl.setFont(QFont("Segoe UI", 10))
        txt_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        col.addWidget(val_lbl)
        col.addWidget(txt_lbl)
        row.addWidget(dot)
        row.addLayout(col)
        row.addStretch()
        return frame