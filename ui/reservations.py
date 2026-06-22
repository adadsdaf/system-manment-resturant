import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QMessageBox,
    QComboBox, QSpinBox, QMenu, QTextEdit, QDateEdit,
    QTimeEdit, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer
from PyQt6.QtGui import QFont, QColor, QCursor
from services.reservation_service import (
    get_reservations, get_todays_reservations,
    add_reservation, update_reservation,
    update_reservation_status, delete_reservation,
    get_reservation_stats
)
from services.table_service import get_all_tables
from services.customer_service import get_customer_by_phone
from assets.styles import COLORS, primary_button, outline_button, table_stylesheet


# ── Status config ─────────────────────────────────────────────
STATUS_CONFIG = {
    "Pending":   (COLORS['warning'],  "#fef3c7"),
    "Confirmed": (COLORS['blue'],     "#dbeafe"),
    "Seated":    (COLORS['accent'],   "#dcfce7"),
    "Completed": ("#7c3aed",          "#ede9fe"),
    "Cancelled": (COLORS['danger'],   "#fee2e2"),
    "No Show":   (COLORS['text_muted'], COLORS['bg_tertiary']),
}


# ── Reservation dialog ────────────────────────────────────────
class ReservationDialog(QDialog):
    def __init__(self, parent=None,
                 reservation=None, tables=None):
        super().__init__(parent)
        self.reservation = reservation
        self.tables      = tables or []
        self.customer_id = None
        if reservation:
            self.customer_id = reservation[10]
        self.setWindowTitle(
            "Edit Reservation" if reservation
            else "New Reservation"
        )
        self.setFixedSize(480, 520)
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
            "Edit Reservation" if self.reservation
            else "New Reservation"
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
            QLineEdit, QComboBox, QSpinBox,
            QDateEdit, QTimeEdit, QTextEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QComboBox:focus,
            QSpinBox:focus, QDateEdit:focus,
            QTimeEdit:focus, QTextEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        # Customer name + phone search
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "Customer full name *"
        )
        self.name_input.setFixedHeight(40)
        self.name_input.setStyleSheet(input_style)

        phone_row = QHBoxLayout()
        phone_row.setSpacing(6)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText(
            "Phone number"
        )
        self.phone_input.setFixedHeight(40)
        self.phone_input.setStyleSheet(input_style)

        lookup_btn = QPushButton("🔍")
        lookup_btn.setFixedSize(40, 40)
        lookup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        lookup_btn.setToolTip(
            "Lookup customer by phone"
        )
        lookup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
        """)
        lookup_btn.clicked.connect(self.lookup_customer)
        phone_row.addWidget(self.phone_input)
        phone_row.addWidget(lookup_btn)

        # Guests
        self.guests_spin = QSpinBox()
        self.guests_spin.setRange(1, 50)
        self.guests_spin.setValue(2)
        self.guests_spin.setFixedHeight(40)
        self.guests_spin.setStyleSheet(input_style)

        # Table
        self.table_combo = QComboBox()
        self.table_combo.setFixedHeight(40)
        self.table_combo.setStyleSheet(input_style)
        self.table_combo.addItem("— No specific table —", None)
        for t in self.tables:
            if t[4] in ("Available", "Reserved"):
                self.table_combo.addItem(
                    f"Table {t[1]}  ({t[3]}, "
                    f"{t[2]} guests)", t[0]
                )

        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedHeight(40)
        self.date_edit.setStyleSheet(input_style)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setMinimumDate(QDate.currentDate())

        # Time
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(19, 0))
        self.time_edit.setFixedHeight(40)
        self.time_edit.setStyleSheet(input_style)
        self.time_edit.setDisplayFormat("hh:mm AP")

        # Special requests
        self.requests_input = QTextEdit()
        self.requests_input.setPlaceholderText(
            "Special requests, dietary requirements, "
            "occasions..."
        )
        self.requests_input.setFixedHeight(70)
        self.requests_input.setStyleSheet(input_style)

        for lbl, widget in [
            ("Customer Name *", self.name_input),
            ("Phone",           phone_row),
            ("Guests *",        self.guests_spin),
            ("Table",           self.table_combo),
            ("Date *",          self.date_edit),
            ("Time *",          self.time_edit),
            ("Special Requests",self.requests_input),
        ]:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
            if isinstance(widget, QHBoxLayout):
                form.addRow(l, widget)
            else:
                form.addRow(l, widget)

        if self.reservation:
            r = self.reservation
            self.name_input.setText(r[1])
            self.phone_input.setText(r[2] or "")
            self.guests_spin.setValue(r[3])
            try:
                d = r[4]
                if hasattr(d, 'year'):
                    self.date_edit.setDate(
                        QDate(d.year, d.month, d.day)
                    )
                t = r[5]
                if hasattr(t, 'hour'):
                    self.time_edit.setTime(
                        QTime(t.hour, t.minute)
                    )
                elif isinstance(t, datetime.timedelta):
                    total = int(t.total_seconds())
                    h, m  = divmod(total // 60, 60)
                    self.time_edit.setTime(QTime(h, m))
            except Exception:
                pass
            self.requests_input.setPlainText(
                r[7] or ""
            )
            if r[11]:
                for i in range(self.table_combo.count()):
                    if self.table_combo.itemData(i) == r[11]:
                        self.table_combo.setCurrentIndex(i)
                        break

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

        save_btn = QPushButton(
            "Save Changes" if self.reservation
            else "Book Reservation"
        )
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

    def lookup_customer(self):
        phone = self.phone_input.text().strip()
        if not phone:
            return
        customer = get_customer_by_phone(phone)
        if customer:
            self.name_input.setText(customer[1])
            self.customer_id = customer[0]
            QMessageBox.information(
                self, "Customer Found",
                f"Linked to: {customer[1]}\n"
                f"Loyalty Points: {customer[4]}"
            )
        else:
            QMessageBox.information(
                self, "Not Found",
                "No customer found with that phone number.\n"
                "You can still proceed with the reservation."
            )

    def save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self, "Validation",
                "Customer name is required."
            )
            return
        self.result_data = {
            "customer_name":    name,
            "phone":            self.phone_input.text().strip(),
            "customer_id":      self.customer_id,
            "table_id":         self.table_combo.currentData(),
            "guests":           self.guests_spin.value(),
            "reservation_date": self.date_edit.date().toString(
                "yyyy-MM-dd"
            ),
            "reservation_time": self.time_edit.time().toString(
                "HH:mm"
            ),
            "special_requests": self.requests_input.toPlainText().strip(),
        }
        self.accept()


# ── Main reservations widget ──────────────────────────────────
class ReservationsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user          = user
        self.reservations  = []
        self.active_filter = "All"
        self.view_mode     = "today"
        self.setStyleSheet(
            f"background-color: {COLORS['bg_primary']};"
        )
        self.setup_ui()
        self.load_data()

        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(60000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Header ────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_col  = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Reservations")
        page_title.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        page_title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        page_sub = QLabel(
            "Manage table reservations and bookings"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        new_btn = QPushButton("⊕  New Reservation")
        new_btn.setFixedHeight(40)
        new_btn.setFixedWidth(170)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.setStyleSheet(primary_button())
        new_btn.clicked.connect(self.new_reservation)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(outline_button())
        refresh_btn.clicked.connect(self.load_data)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(refresh_btn)
        header_row.addWidget(new_btn)

        # ── Stats row ─────────────────────────────────────────
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)

        # ── View toggle ───────────────────────────────────────
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(8)

        self.today_btn = QPushButton("📅  Today")
        self.all_btn = QPushButton("📋  All Reservations")

        for btn, mode in [
            (self.today_btn, "today"),
            (self.all_btn, "all")
        ]:
            btn.setFixedHeight(34)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS['bg_secondary']};
                            color: {COLORS['text_secondary']};
                            border: 1.5px solid {COLORS['border']};
                            border-radius: 8px;
                            font-size: 12px;
                            font-weight: 600;
                            font-family: Segoe UI;
                            padding: 0 16px;
                        }}
                        QPushButton:checked {{
                            background-color: {COLORS['accent']};
                            color: white;
                            border-color: {COLORS['accent']};
                        }}
                        QPushButton:hover {{
                            border-color: {COLORS['accent']};
                        }}
                    """)
            btn.clicked.connect(
                lambda _, m=mode: self.set_view_mode(m)
            )

        self.today_btn.setChecked(True)
        toggle_row.addWidget(self.today_btn)
        toggle_row.addWidget(self.all_btn)
        toggle_row.addStretch()

        # ── Status filter tabs ────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        self.filter_btns = {}

        for status in ["All", "Pending", "Confirmed",
                       "Seated", "Completed",
                       "Cancelled", "No Show"]:
            config = STATUS_CONFIG.get(status, {})
            color = config[0] if config else COLORS['text_secondary']

            btn = QPushButton(status)
            btn.setFixedHeight(30)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS['bg_secondary']};
                            color: {COLORS['text_secondary']};
                            border: 1.5px solid {COLORS['border']};
                            border-radius: 15px;
                            font-size: 11px;
                            font-weight: 600;
                            font-family: Segoe UI;
                            padding: 0 12px;
                        }}
                        QPushButton:checked {{
                            background-color: {color if status != 'All' else COLORS['accent']};
                            color: white;
                            border-color: {color if status != 'All' else COLORS['accent']};
                        }}
                        QPushButton:hover {{
                            border-color: {color if status != 'All' else COLORS['accent']};
                        }}
                    """)
            btn.clicked.connect(
                lambda _, s=status: self.set_filter(s)
            )
            filter_row.addWidget(btn)
            self.filter_btns[status] = btn

        filter_row.addStretch()
        self.filter_btns["All"].setChecked(True)

        # ── Table ─────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "CUSTOMER", "PHONE",
            "GUESTS", "DATE", "TIME",
            "TABLE", "STATUS", "ACTIONS"
        ])
        self.table.setStyleSheet(
            table_stylesheet()
        )

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 90)
        self.table.setColumnWidth(6, 90)
        self.table.setColumnWidth(7, 130)
        self.table.setColumnWidth(8, 100)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
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
        self.table.horizontalHeaderItem(6).setTextAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.table.horizontalHeaderItem(7).setTextAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.table.horizontalHeaderItem(8).setTextAlignment(
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
        self.table.doubleClicked.connect(
            self.on_row_double_click
        )

        layout.addLayout(header_row)
        layout.addLayout(self.stats_row)
        layout.addLayout(toggle_row)
        layout.addLayout(filter_row)
        layout.addWidget(self.table)

    def load_data(self):
        stats = get_reservation_stats()

        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, key, color in [
            ("Today's Bookings", "total_today",  COLORS['blue']),
            ("Pending",          "pending",       COLORS['warning']),
            ("Confirmed",        "confirmed",     COLORS['blue']),
            ("Seated",           "seated",        COLORS['accent']),
            ("Total Guests",     "total_guests",  "#7c3aed"),
        ]:
            pill = self.build_stat_pill(
                label, stats.get(key, 0), color
            )
            self.stats_row.addWidget(pill)
        self.stats_row.addStretch()

        if self.view_mode == "today":
            self.reservations = get_todays_reservations()
        else:
            self.reservations = get_reservations(
                status_filter=(
                    None if self.active_filter == "All"
                    else self.active_filter
                )
            )

        self.populate_table(self.reservations)

    def set_view_mode(self, mode):
        self.view_mode = mode
        self.today_btn.setChecked(mode == "today")
        self.all_btn.setChecked(mode == "all")
        self.load_data()

    def set_filter(self, status):
        self.active_filter = status
        for s, btn in self.filter_btns.items():
            btn.setChecked(s == status)
        self.load_data()

    def populate_table(self, reservations):
        self.table.setRowCount(0)
        self.table.setRowCount(len(reservations))

        for idx, r in enumerate(reservations):
            self.table.setRowHeight(idx, 52)

            id_item = QTableWidgetItem(str(r[0]))
            id_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            id_item.setForeground(
                QColor(COLORS['text_muted'])
            )
            self.table.setItem(idx, 0, id_item)

            name_item = QTableWidgetItem(r[1])
            name_item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
            name_item.setForeground(QColor(COLORS['accent']))
            self.table.setItem(idx, 1, name_item)

            self.table.setItem(
                idx, 2,
                QTableWidgetItem(r[2] or "—")
            )

            guests_item = QTableWidgetItem(str(r[3]))
            guests_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self.table.setItem(idx, 3, guests_item)

            # Date
            try:
                d = r[4]
                date_str = (
                    d.strftime("%d %b %Y")
                    if hasattr(d, 'strftime')
                    else str(d)
                )
            except Exception:
                date_str = str(r[4])
            self.table.setItem(
                idx, 4, QTableWidgetItem(date_str)
            )

            # Time
            try:
                t = r[5]
                if hasattr(t, 'strftime'):
                    time_str = t.strftime("%H:%M")
                elif isinstance(t, datetime.timedelta):
                    total    = int(t.total_seconds())
                    h, rem   = divmod(total, 3600)
                    m        = rem // 60
                    time_str = f"{h:02d}:{m:02d}"
                else:
                    time_str = str(t)
            except Exception:
                time_str = str(r[5])
            self.table.setItem(
                idx, 5, QTableWidgetItem(time_str)
            )

            self.table.setItem(
                idx, 6, QTableWidgetItem(r[8])
            )

            # Status badge
            status       = r[6]
            s_color, s_bg = STATUS_CONFIG.get(
                status,
                (COLORS['text_muted'],
                 COLORS['bg_tertiary'])
            )
            badge_widget = QWidget()
            badge_widget.setStyleSheet(
                "background: transparent;"
            )
            badge_layout = QHBoxLayout(badge_widget)
            badge_layout.setContentsMargins(6, 0, 6, 0)
            badge_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            badge = QLabel(status)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedHeight(24)
            badge.setFont(
                QFont("Segoe UI", 10, QFont.Weight.Bold)
            )
            badge.setStyleSheet(f"""
                color: {s_color};
                background-color: {s_bg};
                border-radius: 10px;
                padding: 0 10px;
                border: none;
            """)
            badge_layout.addWidget(badge)
            self.table.setCellWidget(idx, 7, badge_widget)

            # Actions button
            dots_btn = QPushButton("⋮")
            dots_btn.setFixedSize(32, 32)
            dots_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            dots_btn.setToolTip("Actions")
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
                                border-color: {COLORS['border_strong']};
                                color: {COLORS['text_primary']};
                            }}
                        """)
            dots_btn.clicked.connect(
                lambda _, res=r: self.show_action_menu(res)
            )

            action_widget = QWidget()
            action_widget.setStyleSheet(
                "background: transparent;"
            )
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            action_layout.addWidget(dots_btn)
            self.table.setCellWidget(idx, 8, action_widget)

    def on_row_double_click(self, index):
        row = index.row()
        if row < len(self.reservations):
            self.show_action_menu(
                self.reservations[row]
            )

    def show_action_menu(self, reservation):
        status = reservation[6]
        menu   = QMenu(self)
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

        title = menu.addAction(
            f"Reservation #{reservation[0]} — {status}"
        )
        title.setEnabled(False)
        menu.addSeparator()

        edit_action = menu.addAction("✏️   Edit Reservation")

        if status == "Pending":
            confirm_action = menu.addAction(
                "✅  Confirm Reservation"
            )
            menu.addSeparator()
            cancel_action = menu.addAction(
                "🗑️   Cancel Reservation"
            )
        elif status == "Confirmed":
            seat_action   = menu.addAction(
                "🪑  Seat Guests"
            )
            cancel_action = menu.addAction(
                "🗑️   Cancel Reservation"
            )
        elif status == "Seated":
            complete_action = menu.addAction(
                "✓  Mark as Completed"
            )
            cancel_action   = None
        else:
            cancel_action = None

        menu.addSeparator()
        noshow_action = menu.addAction("❌  Mark as No Show")
        delete_action = menu.addAction("🗑️   Delete Record")

        action = menu.exec(QCursor.pos())

        if action == edit_action:
            self.edit_reservation(reservation)
        elif status == "Pending" and action == confirm_action:
            self.update_status(reservation[0], "Confirmed")
        elif status == "Confirmed" and action == seat_action:
            self.update_status(reservation[0], "Seated")
        elif status == "Seated" and action == complete_action:
            self.update_status(reservation[0], "Completed")
        elif cancel_action and action == cancel_action:
            self.update_status(reservation[0], "Cancelled")
        elif action == noshow_action:
            self.update_status(reservation[0], "No Show")
        elif action == delete_action:
            self.delete_res(reservation[0])

    def update_status(self, reservation_id, status):
        success = update_reservation_status(
            reservation_id, status
        )
        if success:
            self.load_data()
        else:
            QMessageBox.critical(
                self, "Error",
                "Failed to update reservation status."
            )

    def new_reservation(self):
        tables  = get_all_tables()
        dialog  = ReservationDialog(
            self, tables=tables
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = add_reservation(
                d['customer_name'], d['phone'],
                d['customer_id'], d['table_id'],
                d['guests'], d['reservation_date'],
                d['reservation_time'],
                d['special_requests'],
                self.user['user_id']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to create reservation."
                )

    def edit_reservation(self, reservation):
        tables = get_all_tables()
        dialog = ReservationDialog(
            self, reservation=reservation, tables=tables
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = update_reservation(
                reservation[0], d['customer_name'],
                d['phone'], d['table_id'], d['guests'],
                d['reservation_date'], d['reservation_time'],
                d['special_requests']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to update reservation."
                )

    def delete_res(self, reservation_id):
        reply = QMessageBox.question(
            self, "Delete Reservation",
            "Permanently delete this reservation record?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = delete_reservation(reservation_id)
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to delete reservation."
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