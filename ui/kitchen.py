import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGraphicsDropShadowEffect, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from services.kitchen_service import (
    get_kitchen_orders, get_kitchen_order_items,
    update_kitchen_order_status, update_priority,
    get_kitchen_stats
)
from assets.styles import COLORS, primary_button


# ── Status config ─────────────────────────────────────────────
STATUS_CONFIG = {
    "Pending": {
        "color":  "#d97706",
        "bg":     "#fffbeb",
        "border": "#fbbf24",
        "badge":  "#fef3c7",
        "next":   "Preparing",
        "next_label": "▶  Start Preparing",
        "next_color": COLORS['blue'],
    },
    "Preparing": {
        "color":  COLORS['blue'],
        "bg":     "#eff6ff",
        "border": "#93c5fd",
        "badge":  "#dbeafe",
        "next":   "Ready",
        "next_label": "✓  Mark as Ready",
        "next_color": COLORS['accent'],
    },
    "Ready": {
        "color":  COLORS['accent'],
        "bg":     "#f0fdf4",
        "border": "#86efac",
        "badge":  "#dcfce7",
        "next":   "Served",
        "next_label": "🍽  Mark as Served",
        "next_color": "#7c3aed",
    },
    "Served": {
        "color":  "#7c3aed",
        "bg":     "#f5f3ff",
        "border": "#c4b5fd",
        "badge":  "#ede9fe",
        "next":   None,
        "next_label": None,
        "next_color": None,
    },
}

PRIORITY_COLORS = {
    "High":   COLORS['danger'],
    "Normal": COLORS['text_muted'],
    "Low":    COLORS['accent'],
}


# ── Order ticket card ─────────────────────────────────────────
class OrderTicket(QFrame):
    def __init__(self, order, on_status_change, parent=None):
        super().__init__(parent)
        self.order            = order
        self.on_status_change = on_status_change
        status                = order[4]
        config                = STATUS_CONFIG.get(
            status, STATUS_CONFIG["Pending"]
        )

        self.setFixedWidth(280)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {config['bg']};
                border-radius: 12px;
                border: 2px solid {config['border']};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ── Ticket header ─────────────────────────────────────
        header_row = QHBoxLayout()

        order_num = QLabel(f"Order #{order[1]}")
        order_num.setFont(
            QFont("Segoe UI", 13, QFont.Weight.Bold)
        )
        order_num.setStyleSheet(
            f"color: {config['color']};"
        )

        # Timer
        self.timer_lbl = QLabel("")
        self.timer_lbl.setFont(QFont("Segoe UI", 10))
        self.timer_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']};"
        )
        self.update_timer()

        header_row.addWidget(order_num)
        header_row.addStretch()
        header_row.addWidget(self.timer_lbl)

        # Priority badge
        priority       = order[5]
        priority_color = PRIORITY_COLORS.get(
            priority, COLORS['text_muted']
        )
        priority_row   = QHBoxLayout()

        priority_badge = QLabel(f"● {priority} Priority")
        priority_badge.setFont(
            QFont("Segoe UI", 9, QFont.Weight.Bold)
        )
        priority_badge.setStyleSheet(
            f"color: {priority_color};"
        )

        status_badge = QLabel(status)
        status_badge.setFont(
            QFont("Segoe UI", 9, QFont.Weight.Bold)
        )
        status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_badge.setFixedHeight(22)
        status_badge.setStyleSheet(f"""
            color: {config['color']};
            background-color: {config['badge']};
            border-radius: 10px;
            padding: 0 10px;
            border: none;
        """)

        priority_row.addWidget(priority_badge)
        priority_row.addStretch()
        priority_row.addWidget(status_badge)

        # Customer / table info
        info_row = QHBoxLayout()
        info_row.setSpacing(12)

        if order[2]:
            table_lbl = QLabel(f"🪑  Table {order[2]}")
            table_lbl.setFont(QFont("Segoe UI", 10))
            table_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
            info_row.addWidget(table_lbl)

        if order[3]:
            cust_lbl = QLabel(f"👤  {order[3]}")
            cust_lbl.setFont(QFont("Segoe UI", 10))
            cust_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
            info_row.addWidget(cust_lbl)

        info_row.addStretch()

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {config['border']}; border: none;"
        )

        # Order items
        items = get_kitchen_order_items(order[0])
        items_layout = QVBoxLayout()
        items_layout.setSpacing(4)

        for item in items:
            item_row = QHBoxLayout()
            qty_lbl  = QLabel(f"x{item[2]}")
            qty_lbl.setFixedWidth(28)
            qty_lbl.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            qty_lbl.setStyleSheet(
                f"color: {config['color']};"
            )

            name_lbl = QLabel(item[1])
            name_lbl.setFont(QFont("Segoe UI", 11))
            name_lbl.setStyleSheet(
                f"color: {COLORS['text_primary']};"
            )

            item_row.addWidget(qty_lbl)
            item_row.addWidget(name_lbl)
            item_row.addStretch()
            items_layout.addLayout(item_row)

        # Notes
        if order[6]:
            notes_lbl = QLabel(f"📝  {order[6]}")
            notes_lbl.setFont(QFont("Segoe UI", 9))
            notes_lbl.setStyleSheet(
                f"color: {COLORS['text_muted']};"
            )
            notes_lbl.setWordWrap(True)
            items_layout.addWidget(notes_lbl)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        if config['next']:
            next_btn = QPushButton(config['next_label'])
            next_btn.setFixedHeight(36)
            next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            next_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {config['next_color']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    font-family: Segoe UI;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
            next_btn.clicked.connect(
                lambda _, oid=order[0], s=config['next']:
                self.on_status_change(oid, s)
            )
            btn_row.addWidget(next_btn)

        # Priority toggle
        if order[5] != "High":
            urgent_btn = QPushButton("🔴  Urgent")
            urgent_btn.setFixedHeight(36)
            urgent_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            urgent_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['danger_light']};
                    color: {COLORS['danger']};
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    font-family: Segoe UI;
                    padding: 0 12px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['danger']};
                    color: white;
                }}
            """)
            urgent_btn.clicked.connect(
                lambda _, oid=order[0]:
                self.on_status_change(oid, None, "High")
            )
            btn_row.addWidget(urgent_btn)

        layout.addLayout(header_row)
        layout.addLayout(priority_row)
        layout.addLayout(info_row)
        layout.addWidget(div)
        layout.addLayout(items_layout)
        layout.addLayout(btn_row)

        # Timer update every second
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_timer)
        self.tick_timer.start(1000)

    def update_timer(self):
        try:
            created = self.order[7]
            if isinstance(created, str):
                created = datetime.datetime.strptime(
                    created, "%Y-%m-%d %H:%M:%S"
                )
            elapsed = datetime.datetime.now() - created
            mins    = int(elapsed.total_seconds() // 60)
            secs    = int(elapsed.total_seconds() % 60)

            if mins >= 15:
                color = COLORS['danger']
            elif mins >= 8:
                color = COLORS['warning']
            else:
                color = COLORS['text_muted']

            self.timer_lbl.setText(f"⏱  {mins:02d}:{secs:02d}")
            self.timer_lbl.setStyleSheet(f"color: {color};")
        except Exception:
            self.timer_lbl.setText("")


# ── Main kitchen widget ───────────────────────────────────────
class KitchenWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user           = user
        self.active_filter  = "All"
        self.setStyleSheet(
            f"background-color: {COLORS['bg_primary']};"
        )
        self.setup_ui()
        self.load_orders()

        # Auto refresh every 15 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_orders)
        self.refresh_timer.start(15000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Header ────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_col  = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Kitchen Display")
        page_title.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        page_title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        page_sub = QLabel(
            "Real time order tickets for kitchen staff"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        self.last_refresh_lbl = QLabel("")
        self.last_refresh_lbl.setFont(QFont("Segoe UI", 10))
        self.last_refresh_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']};"
        )

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['accent']};
                border: 1.5px solid {COLORS['accent']};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_light']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_orders)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(self.last_refresh_lbl)
        header_row.addWidget(refresh_btn)

        # ── Stats row ─────────────────────────────────────────
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)

        # ── Filter tabs ───────────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        self.filter_btns = {}

        for label in ["All", "Pending", "Preparing",
                      "Ready", "Served"]:
            config = STATUS_CONFIG.get(label, {})
            color  = config.get("color", COLORS['text_secondary'])

            btn = QPushButton(label)
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
                    background-color: {color if label != 'All' else COLORS['accent']};
                    color: white;
                    border-color: {color if label != 'All' else COLORS['accent']};
                }}
                QPushButton:hover {{
                    border-color: {color if label != 'All' else COLORS['accent']};
                }}
            """)
            btn.clicked.connect(
                lambda _, f=label: self.set_filter(f)
            )
            filter_row.addWidget(btn)
            self.filter_btns[label] = btn

        filter_row.addStretch()
        self.filter_btns["All"].setChecked(True)

        # ── Orders scroll area ────────────────────────────────
        self.orders_scroll = QScrollArea()
        self.orders_scroll.setWidgetResizable(True)
        self.orders_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                width: 6px; background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1; border-radius: 3px;
            }
            QScrollBar:horizontal {
                height: 6px; background: transparent;
            }
            QScrollBar::handle:horizontal {
                background: #cbd5e1; border-radius: 3px;
            }
        """)

        self.orders_widget = QWidget()
        self.orders_widget.setStyleSheet("background: transparent;")
        self.orders_layout = QHBoxLayout(self.orders_widget)
        self.orders_layout.setContentsMargins(0, 0, 0, 0)
        self.orders_layout.setSpacing(16)
        self.orders_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.orders_scroll.setWidget(self.orders_widget)

        # Empty state
        self.empty_lbl = QLabel(
            "🍳\n\nNo active orders\nOrders will appear here"
        )
        
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setFont(QFont("Segoe UI", 14))
        self.empty_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']};"
        )

        layout.addLayout(header_row)
        layout.addLayout(self.stats_row)
        layout.addLayout(filter_row)
        layout.addWidget(self.orders_scroll)
        layout.addWidget(self.empty_lbl)

    def load_orders(self):
        stats = get_kitchen_stats()

        # Rebuild stats
        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, key, color in [
            ("Pending",   "pending",   COLORS['warning']),
            ("Preparing", "preparing", COLORS['blue']),
            ("Ready",     "ready",     COLORS['accent']),
            ("Served",    "served",    "#7c3aed"),
            ("Total Today", "total",   COLORS['text_secondary']),
        ]:
            pill = self.build_stat_pill(
                label, stats.get(key, 0), color
            )
            self.stats_row.addWidget(pill)
        self.stats_row.addStretch()

        # Load order tickets
        orders = get_kitchen_orders(
            None if self.active_filter == "All"
            else self.active_filter
        )

        while self.orders_layout.count():
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not orders:
            self.empty_lbl.show()
            self.orders_scroll.hide()
        else:
            self.empty_lbl.hide()
            self.orders_scroll.show()
            for order in orders:
                ticket = OrderTicket(
                    order, self.handle_status_change
                )
                self.orders_layout.addWidget(ticket)
            self.orders_layout.addStretch()

        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.last_refresh_lbl.setText(f"Last updated: {now}")

    def set_filter(self, f):
        self.active_filter = f
        for label, btn in self.filter_btns.items():
            btn.setChecked(label == f)
        self.load_orders()

    def handle_status_change(self, kitchen_order_id,
                              new_status, priority=None):
        if priority:
            from services.kitchen_service import update_priority
            update_priority(kitchen_order_id, priority)
        elif new_status:
            if new_status == "Served":
                reply = QMessageBox.question(
                    self, "Mark as Served",
                    "Mark this order as served and remove "
                    "from display?",
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            update_kitchen_order_status(
                kitchen_order_id, new_status
            )
        self.load_orders()

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