from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QDialog, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QMessageBox,
    QGraphicsDropShadowEffect, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QCursor
from services.table_service import (
    get_all_tables, get_locations, open_table_session,
    close_table_session, reserve_table, transfer_table,
    add_table, update_table, delete_table, get_table_stats
)
from assets.styles import COLORS, primary_button, outline_button


# ── Status colours ────────────────────────────────────────────
STATUS_COLORS = {
    "Available": {
        "bg":     "#f0fdf4",
        "border": "#16a34a",
        "text":   "#15803d",
        "badge":  "#dcfce7",
    },
    "Occupied": {
        "bg":     "#fff1f2",
        "border": "#dc2626",
        "text":   "#dc2626",
        "badge":  "#fee2e2",
    },
    "Reserved": {
        "bg":     "#fffbeb",
        "border": "#d97706",
        "text":   "#d97706",
        "badge":  "#fef3c7",
    },
}


# ── Open session dialog ───────────────────────────────────────
class OpenSessionDialog(QDialog):
    def __init__(self, table, parent=None):
        super().__init__(parent)
        self.table = table
        self.setWindowTitle(f"Open Table {table[1]}")
        self.setFixedSize(380, 280)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS['bg_secondary']}; }}
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

        title = QLabel(f"Open Table {self.table[1]}")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        sub = QLabel(
            f"Capacity: {self.table[2]} guests  •  {self.table[3]}"
        )
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {COLORS['text_muted']};")

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        form = QFormLayout()
        form.setSpacing(12)

        input_style = f"""
            QLineEdit, QSpinBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText(
            "e.g. John Doe  (optional)"
        )
        self.customer_input.setFixedHeight(40)
        self.customer_input.setStyleSheet(input_style)

        self.guests_spin = QSpinBox()
        self.guests_spin.setRange(1, self.table[2])
        self.guests_spin.setValue(1)
        self.guests_spin.setFixedHeight(40)
        self.guests_spin.setStyleSheet(input_style)

        for lbl, widget in [
            ("Customer Name", self.customer_input),
            ("Number of Guests", self.guests_spin),
        ]:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(f"color: {COLORS['text_secondary']};")
            form.addRow(l, widget)

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

        open_btn = QPushButton("Open Table")
        open_btn.setFixedHeight(42)
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setStyleSheet(primary_button())
        open_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(open_btn)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addWidget(div)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "customer_name": self.customer_input.text().strip(),
            "guests":        self.guests_spin.value(),
        }


# ── Add/edit table dialog ─────────────────────────────────────
class TableDialog(QDialog):
    def __init__(self, parent=None, table=None, locations=None):
        super().__init__(parent)
        self.table     = table
        self.locations = locations or ["Main Hall", "Outdoor",
                                       "Private Room", "Bar"]
        self.setWindowTitle("Edit Table" if table else "Add Table")
        self.setFixedSize(380, 320)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS['bg_secondary']}; }}
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

        title = QLabel("Edit Table" if self.table else "Add New Table")
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
            QLineEdit, QSpinBox, QComboBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("e.g. T13")
        self.number_input.setFixedHeight(40)
        self.number_input.setStyleSheet(input_style)

        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 20)
        self.capacity_spin.setValue(4)
        self.capacity_spin.setFixedHeight(40)
        self.capacity_spin.setStyleSheet(input_style)

        self.location_combo = QComboBox()
        self.location_combo.setFixedHeight(40)
        self.location_combo.setStyleSheet(input_style)
        for loc in self.locations:
            self.location_combo.addItem(loc)

        # Custom location input
        self.custom_loc = QLineEdit()
        self.custom_loc.setPlaceholderText(
            "Or type a new location..."
        )
        self.custom_loc.setFixedHeight(40)
        self.custom_loc.setStyleSheet(input_style)

        for lbl, widget in [
            ("Table Number *",  self.number_input),
            ("Capacity *",      self.capacity_spin),
            ("Location *",      self.location_combo),
            ("New Location",    self.custom_loc),
        ]:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(f"color: {COLORS['text_secondary']};")
            form.addRow(l, widget)

        if self.table:
            self.number_input.setText(self.table[1])
            self.capacity_spin.setValue(self.table[2])
            idx = self.location_combo.findText(self.table[3])
            if idx >= 0:
                self.location_combo.setCurrentIndex(idx)

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

        save_btn = QPushButton("Save Table")
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
        number = self.number_input.text().strip()
        if not number:
            QMessageBox.warning(self, "Validation",
                                "Table number is required.")
            return
        location = (self.custom_loc.text().strip()
                    or self.location_combo.currentText())
        self.result_data = {
            "table_number": number,
            "capacity":     self.capacity_spin.value(),
            "location":     location,
        }
        self.accept()


# ── Table card widget ─────────────────────────────────────────
class TableCard(QFrame):
    def __init__(self, table, on_action, parent=None):
        super().__init__(parent)
        self.table     = table
        self.on_action = on_action
        status         = table[4]
        colors         = STATUS_COLORS.get(status, STATUS_COLORS["Available"])

        self.setFixedSize(160, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['bg']};
                border-radius: 12px;
                border: 2px solid {colors['border']};
            }}
            QFrame:hover {{
                border: 2px solid {colors['border']};
                background-color: white;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(4)

        # Table number
        num_lbl = QLabel(f"Table {table[1]}")
        num_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        num_lbl.setStyleSheet(f"color: {colors['text']};")

        # Capacity
        cap_lbl = QLabel(f"👥  {table[2]} guests")
        cap_lbl.setFont(QFont("Segoe UI", 10))
        cap_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")

        # Location
        loc_lbl = QLabel(f"📍  {table[3]}")
        loc_lbl.setFont(QFont("Segoe UI", 9))
        loc_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")

        # Customer name if occupied
        if table[7]:
            cust_lbl = QLabel(f"👤  {table[7]}")
            cust_lbl.setFont(QFont("Segoe UI", 9))
            cust_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
        else:
            cust_lbl = QLabel("")

        # Status badge
        badge = QLabel(status)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(22)
        badge.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        badge.setStyleSheet(f"""
            color: {colors['text']};
            background-color: {colors['badge']};
            border-radius: 10px;
            padding: 0 10px;
            border: none;
        """)

        layout.addWidget(num_lbl)
        layout.addWidget(cap_lbl)
        layout.addWidget(loc_lbl)
        layout.addWidget(cust_lbl)
        layout.addStretch()
        layout.addWidget(badge)

    def mousePressEvent(self, event):
        self.on_action(self.table)


# ── Main table management widget ──────────────────────────────
class TableManagementWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user   = user
        self.tables = []
        self.active_location = "All"
        self.setStyleSheet(
            f"background-color: {COLORS['bg_primary']};"
        )
        self.setup_ui()
        self.load_data()

        # Auto refresh every 30 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(30000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Header ────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_col  = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Table Management")
        page_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        page_title.setStyleSheet(f"color: {COLORS['text_primary']};")

        page_sub = QLabel(
            "Monitor and manage restaurant tables in real time"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(f"color: {COLORS['text_secondary']};")

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        add_btn = QPushButton("⊕  Add Table")
        add_btn.setFixedHeight(40)
        add_btn.setFixedWidth(130)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(primary_button())
        add_btn.clicked.connect(self.add_table)

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

        # ── Legend ────────────────────────────────────────────
        legend_row = QHBoxLayout()
        legend_row.setSpacing(16)

        for status, colors in STATUS_COLORS.items():
            dot = QLabel(f"●  {status}")
            dot.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            dot.setStyleSheet(f"color: {colors['text']};")
            legend_row.addWidget(dot)

        legend_row.addStretch()

        # ── Location tabs ─────────────────────────────────────
        self.loc_tab_row  = QHBoxLayout()
        self.loc_tab_row.setSpacing(8)
        self.loc_btn_map  = {}

        # ── Table grid scroll ─────────────────────────────────
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                width: 6px; background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1; border-radius: 3px;
            }
        """)

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.grid_scroll.setWidget(self.grid_widget)

        layout.addLayout(header_row)
        layout.addLayout(self.stats_row)
        layout.addLayout(legend_row)
        layout.addLayout(self.loc_tab_row)
        layout.addWidget(self.grid_scroll)

    def load_data(self):
        self.tables    = get_all_tables()
        locations      = ["All"] + get_locations()
        stats          = get_table_stats()

        # Rebuild stats
        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, value, color in [
            ("Total Tables", stats.get("total", 0),     COLORS['blue']),
            ("Available",    stats.get("available", 0), COLORS['accent']),
            ("Occupied",     stats.get("occupied", 0),  COLORS['danger']),
            ("Reserved",     stats.get("reserved", 0),  COLORS['warning']),
        ]:
            pill = self.build_stat_pill(label, value, color)
            self.stats_row.addWidget(pill)
        self.stats_row.addStretch()

        # Rebuild location tabs
        while self.loc_tab_row.count():
            item = self.loc_tab_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.loc_btn_map.clear()

        for loc in locations:
            btn = QPushButton(loc)
            btn.setFixedHeight(34)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['text_secondary']};
                    border: 1.5px solid {COLORS['border']};
                    border-radius: 17px;
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
                lambda _, l=loc: self.filter_by_location(l)
            )
            self.loc_tab_row.addWidget(btn)
            self.loc_btn_map[loc] = btn

        self.loc_tab_row.addStretch()

        if self.active_location in self.loc_btn_map:
            self.loc_btn_map[self.active_location].setChecked(True)
        else:
            self.active_location = "All"
            if "All" in self.loc_btn_map:
                self.loc_btn_map["All"].setChecked(True)

        self.render_grid()

    def filter_by_location(self, loc):
        self.active_location = loc
        for l, btn in self.loc_btn_map.items():
            btn.setChecked(l == loc)
        self.render_grid()

    def render_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = [
            t for t in self.tables
            if self.active_location == "All"
            or t[3] == self.active_location
        ]

        cols = 5
        for idx, table in enumerate(filtered):
            card = TableCard(table, self.handle_table_action)
            self.grid_layout.addWidget(
                card, idx // cols, idx % cols
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
        val_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        val_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        txt_lbl = QLabel(label)
        txt_lbl.setFont(QFont("Segoe UI", 10))
        txt_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")

        col.addWidget(val_lbl)
        col.addWidget(txt_lbl)

        row.addWidget(dot)
        row.addLayout(col)
        row.addStretch()
        return frame

    def handle_table_action(self, table):
        status = table[4]
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

        title_action = menu.addAction(
            f"Table {table[1]}  —  {status}"
        )
        title_action.setEnabled(False)
        menu.addSeparator()

        if status == "Available":
            open_action    = menu.addAction("🟢  Open Table")
            reserve_action = menu.addAction("🟡  Reserve Table")
            edit_action    = menu.addAction("✏️   Edit Table")
            menu.addSeparator()
            delete_action  = menu.addAction("🗑️   Remove Table")
            action = menu.exec(QCursor.pos())
            if action == open_action:
                self.open_session(table)
            elif action == reserve_action:
                self.reserve_table(table)
            elif action == edit_action:
                self.edit_table(table)
            elif action == delete_action:
                self.delete_table(table)

        elif status == "Occupied":
            close_action    = menu.addAction("🔴  Close Table / Mark Available")
            transfer_action = menu.addAction("🔄  Transfer to Another Table")
            action = menu.exec(QCursor.pos())
            if action == close_action:
                self.close_session(table)
            elif action == transfer_action:
                self.transfer_table(table)

        elif status == "Reserved":
            open_action  = menu.addAction("🟢  Open Table")
            avail_action = menu.addAction("⬜  Mark as Available")
            action = menu.exec(QCursor.pos())
            if action == open_action:
                self.open_session(table)
            elif action == avail_action:
                self.mark_available(table)

    def open_session(self, table):
        dialog = OpenSessionDialog(table, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data    = dialog.get_data()
            success = open_table_session(
                table[0], self.user['user_id'],
                data['customer_name'], data['guests']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to open table."
                )

    def close_session(self, table):
        reply = QMessageBox.question(
            self, "Close Table",
            f"Mark Table {table[1]} as Available?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = close_table_session(table[0], table[6])
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to close table."
                )

    def reserve_table(self, table):
        success = reserve_table(table[0])
        if success:
            self.load_data()
        else:
            QMessageBox.critical(
                self, "Error", "Failed to reserve table."
            )

    def mark_available(self, table):
        conn = __import__(
            'database.connection', fromlist=['create_connection']
        ).create_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("""
                    UPDATE restaurant_tables
                    SET status = 'Available'
                    WHERE table_id = ?
                """, (table[0],))
                conn.commit()
                self.load_data()
            finally:
                conn.close()

    def transfer_table(self, table):
        available = [
            t for t in self.tables
            if t[4] == "Available" and t[0] != table[0]
        ]
        if not available:
            QMessageBox.warning(
                self, "No Tables",
                "No available tables to transfer to."
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Transfer Table")
        dialog.setFixedSize(340, 240)
        dialog.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(24, 24, 24, 24)
        dlg_layout.setSpacing(14)

        title = QLabel(f"Transfer from Table {table[1]}")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {COLORS['text_primary']}; background: transparent;"
        )

        sub = QLabel("Select destination table:")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent;"
        )

        combo = QComboBox()
        combo.setFixedHeight(40)
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QComboBox:focus {{ border-color: {COLORS['accent']}; }}
        """)
        for t in available:
            combo.addItem(
                f"Table {t[1]}  ({t[3]}, {t[2]} guests)", t[0]
            )

        confirm_btn = QPushButton("Transfer")
        confirm_btn.setFixedHeight(42)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(primary_button())
        confirm_btn.clicked.connect(dialog.accept)

        dlg_layout.addWidget(title)
        dlg_layout.addWidget(sub)
        dlg_layout.addWidget(combo)
        dlg_layout.addStretch()
        dlg_layout.addWidget(confirm_btn)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            to_table_id = combo.currentData()
            success     = transfer_table(
                table[0], to_table_id, table[6]
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to transfer table."
                )

    def add_table(self):
        locations = get_locations()
        dialog    = TableDialog(self, locations=locations)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = add_table(
                d['table_number'], d['capacity'], d['location']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to add table. "
                    "Table number may already exist."
                )

    def edit_table(self, table):
        locations = get_locations()
        dialog    = TableDialog(
            self, table=table, locations=locations
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = update_table(
                table[0], d['table_number'],
                d['capacity'], d['location']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to update table."
                )

    def delete_table(self, table):
        reply = QMessageBox.question(
            self, "Remove Table",
            f"Remove Table {table[1]} from the system?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = delete_table(table[0])
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to remove table."
                )