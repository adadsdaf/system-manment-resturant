import csv
import os
import datetime
import tempfile
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QComboBox, QFileDialog, QMessageBox,
    QGraphicsDropShadowEffect, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from services.reports_service import (
    get_sales_summary, get_daily_sales,
    get_sales_by_payment_method, get_top_selling_items,
    get_sales_by_category, get_top_customers,
    get_staff_performance, get_low_stock_report,
    get_hourly_sales
)
from assets.styles import (
    COLORS, primary_button, outline_button,
    table_stylesheet, configure_table
)


class ReportsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user   = user
        self.period = "month"
        self.setStyleSheet(
            f"background-color: {COLORS['bg_primary']};"
        )
        self.setup_ui()
        self.load_all()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # ── Header ────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_col  = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Reports & Analytics")
        page_title.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        page_title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        page_sub = QLabel(
            "Business insights and performance reports"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        # Period selector
        self.period_combo = QComboBox()
        self.period_combo.setFixedHeight(40)
        self.period_combo.setFixedWidth(160)
        self.period_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: 600;
                font-family: Segoe UI;
            }}
            QComboBox:focus {{
                border-color: {COLORS['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """)
        for label, value in [
            ("Today",      "today"),
            ("This Week",  "week"),
            ("This Month", "month"),
        ]:
            self.period_combo.addItem(label, value)
        self.period_combo.setCurrentIndex(2)
        self.period_combo.currentIndexChanged.connect(
            self.on_period_changed
        )

        export_btn = QPushButton("⬇  Export CSV")
        export_btn.setFixedHeight(40)
        export_btn.setFixedWidth(130)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet(outline_button())
        export_btn.clicked.connect(self.export_csv)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(outline_button())
        refresh_btn.clicked.connect(self.load_all)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(self.period_combo)
        header_row.addWidget(export_btn)
        header_row.addWidget(refresh_btn)

        # ── Summary cards ─────────────────────────────────────
        self.summary_row = QHBoxLayout()
        self.summary_row.setSpacing(12)
        self.summary_row.setContentsMargins(0, 0, 0, 0)

        # ── Tabs ──────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.tabs.setMinimumHeight(400)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                background-color: {COLORS['bg_secondary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: 600;
                font-family: Segoe UI;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['accent']};
                border-bottom: 2px solid {COLORS['accent']};
            }}
            QTabBar::tab:hover {{
                color: {COLORS['accent']};
            }}
        """)

        # Tab 1 — Sales
        sales_scroll = QScrollArea()
        sales_scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {COLORS['bg_secondary']}; }}
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar::handle:vertical {{ 
                background-color: {COLORS['border']};
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{ background-color: {COLORS['accent']}; }}
        """)
        sales_scroll.setWidgetResizable(True)
        sales_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        sales_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.sales_tab = QWidget()
        self.sales_tab.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        self.setup_sales_tab()
        sales_scroll.setWidget(self.sales_tab)
        self.tabs.addTab(sales_scroll, "💰  Sales")

        # Tab 2 — Menu
        menu_scroll = QScrollArea()
        menu_scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {COLORS['bg_secondary']}; }}
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar::handle:vertical {{ 
                background-color: {COLORS['border']};
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{ background-color: {COLORS['accent']}; }}
        """)
        menu_scroll.setWidgetResizable(True)
        menu_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        menu_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.menu_tab = QWidget()
        self.menu_tab.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        self.setup_menu_tab()
        menu_scroll.setWidget(self.menu_tab)
        self.tabs.addTab(menu_scroll, "🍽  Menu")

        # Tab 3 — Customers
        cust_scroll = QScrollArea()
        cust_scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {COLORS['bg_secondary']}; }}
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar::handle:vertical {{ 
                background-color: {COLORS['border']};
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{ background-color: {COLORS['accent']}; }}
        """)
        cust_scroll.setWidgetResizable(True)
        cust_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        cust_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.cust_tab = QWidget()
        self.cust_tab.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        self.setup_customers_tab()
        cust_scroll.setWidget(self.cust_tab)
        self.tabs.addTab(cust_scroll, "👥  Customers")

        # Tab 4 — Staff
        staff_scroll = QScrollArea()
        staff_scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {COLORS['bg_secondary']}; }}
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar::handle:vertical {{ 
                background-color: {COLORS['border']};
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{ background-color: {COLORS['accent']}; }}
        """)
        staff_scroll.setWidgetResizable(True)
        staff_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        staff_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.staff_tab = QWidget()
        self.staff_tab.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        self.setup_staff_tab()
        staff_scroll.setWidget(self.staff_tab)
        self.tabs.addTab(staff_scroll, "👨‍💼  Staff")

        # Tab 5 — Inventory
        inv_scroll = QScrollArea()
        inv_scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {COLORS['bg_secondary']}; }}
            QScrollBar:vertical {{ width: 10px; }}
            QScrollBar::handle:vertical {{ 
                background-color: {COLORS['border']};
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{ background-color: {COLORS['accent']}; }}
        """)
        inv_scroll.setWidgetResizable(True)
        inv_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        inv_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.inv_tab = QWidget()
        self.inv_tab.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        self.setup_inventory_tab()
        inv_scroll.setWidget(self.inv_tab)
        self.tabs.addTab(inv_scroll, "📦  Inventory")

        layout.addLayout(header_row)
        layout.addLayout(self.summary_row)
        layout.addWidget(self.tabs, 1)  # Stretch factor = 1 to grow and fill space

    # ── Tab setup methods ─────────────────────────────────────
    def setup_sales_tab(self):
        layout = QVBoxLayout(self.sales_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        # Daily sales table
        lbl = QLabel("Daily Sales Breakdown")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.daily_table = self.make_table(
            ["DATE", "ORDERS", "REVENUE"]
        )
        self.set_header_alignment(
            self.daily_table,
            ["left", "center", "right"]
        )
        self.daily_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        self.daily_table.setMaximumHeight(200)
        self.daily_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.daily_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.daily_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.daily_table.horizontalHeader().setStretchLastSection(False)

        # Payment method table
        lbl2 = QLabel("Sales by Payment Method")
        lbl2.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl2.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.payment_table = self.make_table(
            ["PAYMENT METHOD", "ORDERS", "REVENUE"]
        )
        self.set_header_alignment(
            self.payment_table,
            ["left", "center", "right"]
        )
        self.payment_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        self.payment_table.setMaximumHeight(200)
        self.payment_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.payment_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.payment_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.payment_table.horizontalHeader().setStretchLastSection(False)

        # Hourly sales table
        lbl3 = QLabel("Today's Hourly Sales")
        lbl3.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl3.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.hourly_table = self.make_table(
            ["HOUR", "ORDERS", "REVENUE"]
        )
        self.set_header_alignment(
            self.hourly_table,
            ["left", "center", "right"]
        )
        self.hourly_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        self.hourly_table.setMaximumHeight(200)
        self.hourly_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.hourly_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.hourly_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.hourly_table.horizontalHeader().setStretchLastSection(False)

        layout.addWidget(lbl)
        layout.addWidget(self.daily_table)
        layout.addWidget(lbl2)
        layout.addWidget(self.payment_table)
        layout.addWidget(lbl3)
        layout.addWidget(self.hourly_table)

    def setup_menu_tab(self):
        layout = QVBoxLayout(self.menu_tab)
        layout.setContentsMargins(20, 20, 20, 24)
        layout.setSpacing(18)

        lbl = QLabel("Top Selling Items")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.items_table = self.make_table(
            ["RANK", "ITEM NAME", "QTY SOLD", "REVENUE"]
        )
        self.set_header_alignment(
            self.items_table,
            ["left", "left", "center", "right"]
        )
        self.apply_sales_table_style(
            self.items_table,
            [
                QHeaderView.ResizeMode.Stretch,
                QHeaderView.ResizeMode.Stretch,
                QHeaderView.ResizeMode.Stretch,
                QHeaderView.ResizeMode.Stretch,
            ]
        )
        self.items_table.setMinimumHeight(150)
        self.items_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        lbl2 = QLabel("Revenue by Category")
        lbl2.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl2.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.cat_table = self.make_table(
            ["CATEGORY", "QTY SOLD", "REVENUE", "SHARE %"]
        )
        self.set_header_alignment(
            self.cat_table,
            ["left", "center", "right", "right"]
        )
        self.apply_sales_table_style(
            self.cat_table,
            [
                QHeaderView.ResizeMode.Stretch,
                QHeaderView.ResizeMode.Stretch,
                QHeaderView.ResizeMode.Stretch,
                QHeaderView.ResizeMode.Stretch,
            ]
        )
        self.cat_table.setMinimumHeight(150)
        self.cat_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        layout.addWidget(lbl)
        layout.addWidget(self.items_table)
        layout.addSpacing(26)
        layout.addWidget(lbl2)
        layout.addWidget(self.cat_table)
        layout.addStretch()

        self.equalize_menu_table_columns()

    def setup_customers_tab(self):
        layout = QVBoxLayout(self.cust_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        lbl = QLabel("Top Customers by Spend")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.cust_table = self.make_table(
            ["RANK", "CUSTOMER", "ORDERS", "TOTAL SPENT", "AVG ORDER"]
        )
        self.set_header_alignment(
            self.cust_table,
            ["left", "left", "center", "right", "right"]
        )
        self.apply_sales_table_style(self.cust_table)
        self.cust_table.setMaximumHeight(300)

        layout.addWidget(lbl)
        layout.addWidget(self.cust_table)

    def setup_staff_tab(self):
        layout = QVBoxLayout(self.staff_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        lbl = QLabel("Staff Sales Performance")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.staff_table = self.make_table(
            ["STAFF NAME", "ORDERS", "REVENUE", "AVG ORDER"]
        )
        self.set_header_alignment(
            self.staff_table,
            ["left", "center", "right", "right"]
        )
        self.apply_sales_table_style(self.staff_table)
        self.staff_table.setMaximumHeight(300)

        layout.addWidget(lbl)
        layout.addWidget(self.staff_table)

    def setup_inventory_tab(self):
        layout = QVBoxLayout(self.inv_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        lbl = QLabel("Low Stock & Reorder Alerts")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.low_stock_table = self.make_table([
            "INGREDIENT", "UNIT", "CURRENT",
            "MINIMUM", "UNIT COST",
            "VALUE", "SUPPLIER", "ALERT"
        ])
        self.set_header_alignment(
            self.low_stock_table,
            ["left", "center", "center", "center",
             "right", "right", "left", "center"]
        )
        self.apply_sales_table_style(self.low_stock_table)
        self.low_stock_table.setMaximumHeight(350)

        layout.addWidget(lbl)
        layout.addWidget(self.low_stock_table)

    # ── Data loading ──────────────────────────────────────────
    def on_period_changed(self):
        self.period = self.period_combo.currentData()
        self.load_all()

    def load_all(self):
        self.period = self.period_combo.currentData()
        self.load_summary()
        self.load_sales_tab()
        self.load_menu_tab()
        self.load_customers_tab()
        self.load_staff_tab()
        self.load_inventory_tab()

    def load_summary(self):
        summary = get_sales_summary(self.period)

        while self.summary_row.count():
            item = self.summary_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for title, value, sub, color in [
            ("Total Revenue",
             f"${summary.get('total_revenue', 0):.2f}",
             "Gross sales",
             COLORS['accent']),
            ("Total Orders",
             str(summary.get('total_orders', 0)),
             "Completed orders",
             COLORS['blue']),
            ("Avg Order Value",
             f"${summary.get('avg_order', 0):.2f}",
             "Per transaction",
             COLORS['warning']),
            ("Total Discounts",
             f"${summary.get('total_discount', 0):.2f}",
             "Discounts given",
             COLORS['danger']),
            ("Tax Collected",
             f"${summary.get('total_tax', 0):.2f}",
             "VAT collected",
             "#7c3aed"),
        ]:
            card = self.make_summary_card(
                title, value, sub, color
            )
            self.summary_row.addWidget(card)

    def load_sales_tab(self):
        # Daily sales
        daily = get_daily_sales(
            7 if self.period == "week" else
            30 if self.period == "month" else 1
        )
        self.daily_table.setRowCount(len(daily))
        for idx, row in enumerate(daily):
            self.daily_table.setRowHeight(idx, 44)
            date_str = (
                row[0].strftime("%d %b %Y")
                if hasattr(row[0], 'strftime')
                else str(row[0])
            )
            self.set_cell(
                self.daily_table, idx, 0,
                date_str, align="left"
            )
            self.set_cell(
                self.daily_table, idx, 1, str(row[1]),
                align="center"
            )
            self.set_cell(
                self.daily_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, align="right",
                color=COLORS['accent']
            )

        # Payment methods
        payments = get_sales_by_payment_method(self.period)
        self.payment_table.setRowCount(len(payments))
        for idx, row in enumerate(payments):
            self.payment_table.setRowHeight(idx, 44)
            self.set_cell(
                self.payment_table, idx, 0,
                row[0], bold=True, align="left"
            )
            self.set_cell(
                self.payment_table, idx, 1, str(row[1]),
                align="center"
            )
            self.set_cell(
                self.payment_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, align="right",
                color=COLORS['accent']
            )

        # Hourly sales
        hourly = get_hourly_sales()
        self.hourly_table.setRowCount(len(hourly))
        for idx, row in enumerate(hourly):
            self.hourly_table.setRowHeight(idx, 44)
            hour     = int(row[0])
            suffix   = "AM" if hour < 12 else "PM"
            hour_12  = hour % 12 or 12
            self.set_cell(
                self.hourly_table, idx, 0,
                f"{hour_12}:00 {suffix}", align="left"
            )
            self.set_cell(
                self.hourly_table, idx, 1, str(row[1]),
                align="center"
            )
            self.set_cell(
                self.hourly_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, align="right",
                color=COLORS['accent']
            )

    def load_menu_tab(self):
        # Top items
        items = get_top_selling_items(
            limit=10, period=self.period
        )
        self.items_table.setRowCount(len(items))
        for idx, row in enumerate(items):
            self.items_table.setRowHeight(idx, 44)
            self.set_cell(
                self.items_table, idx, 0,
                f"#{idx+1}", align="left",
                color=COLORS['accent']
            )
            self.set_cell(
                self.items_table, idx, 1,
                row[0], bold=True, align="left"
            )
            self.set_cell(
                self.items_table, idx, 2,
                str(int(row[1])), align=True
            )
            self.set_cell(
                self.items_table, idx, 3,
                f"${float(row[2]):.2f}",
                bold=True, align="right",
                color=COLORS['accent']
            )
        self.fit_table_to_rows(self.items_table)

        # Categories
        cats       = get_sales_by_category(self.period)
        total_rev  = sum(float(r[2]) for r in cats) or 1
        self.cat_table.setRowCount(len(cats))
        for idx, row in enumerate(cats):
            self.cat_table.setRowHeight(idx, 44)
            share = float(row[2]) / total_rev * 100
            self.set_cell(
                self.cat_table, idx, 0, row[0], bold=True,
                align="left"
            )
            self.set_cell(
                self.cat_table, idx, 1,
                str(int(row[1])), align=True
            )
            self.set_cell(
                self.cat_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, align="right",
                color=COLORS['accent']
            )
            self.set_cell(
                self.cat_table, idx, 3,
                f"{share:.1f}%", align="right"
            )
        self.fit_table_to_rows(self.cat_table)

        self.equalize_menu_table_columns()

    def load_customers_tab(self):
        customers = get_top_customers(
            limit=10, period=self.period
        )
        self.cust_table.setRowCount(len(customers))
        for idx, row in enumerate(customers):
            self.cust_table.setRowHeight(idx, 44)
            orders    = row[1]
            spent     = float(row[2])
            avg_order = spent / orders if orders > 0 else 0
            self.set_cell(
                self.cust_table, idx, 0,
                f"#{idx+1}", align="left",
                color=COLORS['accent']
            )
            self.set_cell(
                self.cust_table, idx, 1,
                row[0], bold=True, align="left"
            )
            self.set_cell(
                self.cust_table, idx, 2,
                str(orders), align="center"
            )
            self.set_cell(
                self.cust_table, idx, 3,
                f"${spent:.2f}",
                bold=True, align="right",
                color=COLORS['accent']
            )
            self.set_cell(
                self.cust_table, idx, 4,
                f"${avg_order:.2f}", align="right"
            )

        self.cust_table.horizontalHeader().setStretchLastSection(False)
        self.cust_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cust_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.cust_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.cust_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.cust_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

    def load_staff_tab(self):
        staff = get_staff_performance(self.period)
        self.staff_table.setRowCount(len(staff))
        for idx, row in enumerate(staff):
            self.staff_table.setRowHeight(idx, 44)
            self.set_cell(
                self.staff_table, idx, 0,
                row[0], bold=True, align="left"
            )
            self.set_cell(
                self.staff_table, idx, 1,
                str(row[1]), align="center"
            )
            self.set_cell(
                self.staff_table, idx, 2,
                f"${float(row[2]):.2f}",
                bold=True, align="right",
                color=COLORS['accent']
            )
            self.set_cell(
                self.staff_table, idx, 3,
                f"${float(row[3]):.2f}", align="right"
            )

    def load_inventory_tab(self):
        items = get_low_stock_report()
        self.low_stock_table.setRowCount(len(items))

        alert_colors = {
            "Out of Stock": COLORS['danger'],
            "Critical":     "#dc2626",
            "Low Stock":    COLORS['warning'],
        }

        for idx, row in enumerate(items):
            self.low_stock_table.setRowHeight(idx, 44)
            self.set_cell(
                self.low_stock_table, idx, 0,
                row[0], bold=True,
                color=COLORS['accent']
            )
            self.set_cell(
                self.low_stock_table, idx, 1,
                row[1], align="center"
            )
            self.set_cell(
                self.low_stock_table, idx, 2,
                f"{float(row[2]):.2f}",
                bold=True, align="center",
                color=(
                    COLORS['danger']
                    if float(row[2]) <= float(row[3])
                    else COLORS['text_primary']
                )
            )
            self.set_cell(
                self.low_stock_table, idx, 3,
                f"{float(row[3]):.2f}", align="center"
            )
            self.set_cell(
                self.low_stock_table, idx, 4,
                f"${float(row[5]):.2f}", align="right"
            )
            self.set_cell(
                self.low_stock_table, idx, 5,
                f"${float(row[6]):.2f}", align="right"
            )
            self.set_cell(
                self.low_stock_table, idx, 6,
                row[7], align="left"
            )
            self.low_stock_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.low_stock_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.low_stock_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            self.low_stock_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            self.low_stock_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            self.low_stock_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            self.low_stock_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
            self.low_stock_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

            # Alert badge
            alert      = row[8]
            a_color    = alert_colors.get(
                alert, COLORS['warning']
            )
            badge_widget = QWidget()
            badge_widget.setStyleSheet(
                "background: transparent;"
            )
            from PyQt6.QtWidgets import QHBoxLayout as QHL
            bl = QHL(badge_widget)
            bl.setContentsMargins(6, 0, 6, 0)
            bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge = QLabel(alert)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedHeight(24)
            badge.setFont(
                QFont("Segoe UI", 10, QFont.Weight.Bold)
            )
            badge.setStyleSheet(f"""
                color: {a_color};
                background-color: transparent;
                border: 1.5px solid {a_color};
                border-radius: 10px;
                padding: 0 8px;
            """)
            bl.addWidget(badge)
            self.low_stock_table.setCellWidget(
                idx, 7, badge_widget
            )

    # ── Export ────────────────────────────────────────────────
    def export_csv(self):
        path = QFileDialog.getSaveFileName(
            self, "Export Report",
            f"sales_report_{self.period}.csv",
            "CSV Files (*.csv)"
        )[0]
        if not path:
            return
        try:
            with open(path, "w", newline="",
                      encoding="utf-8") as f:
                writer = csv.writer(f)

                # Sales summary
                summary = get_sales_summary(self.period)
                writer.writerow(["SALES SUMMARY"])
                writer.writerow([
                    "Period", "Total Orders",
                    "Revenue", "Avg Order",
                    "Discounts", "Tax"
                ])
                writer.writerow([
                    self.period,
                    summary.get("total_orders", 0),
                    f"${summary.get('total_revenue', 0):.2f}",
                    f"${summary.get('avg_order', 0):.2f}",
                    f"${summary.get('total_discount', 0):.2f}",
                    f"${summary.get('total_tax', 0):.2f}",
                ])
                writer.writerow([])

                # Top items
                writer.writerow(["TOP SELLING ITEMS"])
                writer.writerow([
                    "Item", "Qty Sold", "Revenue"
                ])
                for row in get_top_selling_items(
                    period=self.period
                ):
                    writer.writerow([
                        row[0], row[1],
                        f"${float(row[2]):.2f}"
                    ])
                writer.writerow([])

                # Staff
                writer.writerow(["STAFF PERFORMANCE"])
                writer.writerow([
                    "Staff", "Orders",
                    "Revenue", "Avg Order"
                ])
                for row in get_staff_performance(
                    self.period
                ):
                    writer.writerow([
                        row[0], row[1],
                        f"${float(row[2]):.2f}",
                        f"${float(row[3]):.2f}"
                    ])

            QMessageBox.information(
                self, "Exported",
                f"Report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", str(e)
            )

    # ── Helpers ───────────────────────────────────────────────
    def make_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setStyleSheet(
            table_stylesheet(header_padding="10px 12px")
        )
        header = table.horizontalHeader()
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        header.setStretchLastSection(True)
        configure_table(table, row_height=44)
        table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        return table

    def set_header_alignment(self, table, alignments):
        for idx, align in enumerate(alignments):
            item = table.horizontalHeaderItem(idx)
            if not item:
                continue
            if align == "left":
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft |
                    Qt.AlignmentFlag.AlignVCenter
                )
            elif align == "right":
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight |
                    Qt.AlignmentFlag.AlignVCenter
                )
            else:
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter |
                    Qt.AlignmentFlag.AlignVCenter
                )

    def apply_sales_table_style(self, table, modes=None, widths=None):
        table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        table.setMinimumWidth(0)
        header = table.horizontalHeader()
        if modes is None:
            modes = [
                QHeaderView.ResizeMode.Stretch
                for _ in range(table.columnCount())
            ]
        for idx, mode in enumerate(modes):
            header.setSectionResizeMode(idx, mode)
        header.setStretchLastSection(False)
        if widths:
            for idx, width in enumerate(widths):
                if width is not None and idx < table.columnCount():
                    table.setColumnWidth(idx, width)

    def set_table_column_layout(self, table, modes):
        header = table.horizontalHeader()
        for idx, mode in enumerate(modes):
            header.setSectionResizeMode(idx, mode)
        header.setStretchLastSection(False)

    def equalize_menu_table_columns(self):
        ratios = [0.16, 0.44, 0.20, 0.20]
        for table in (self.items_table, self.cat_table):
            if table.columnCount() != len(ratios):
                continue
            header = table.horizontalHeader()
            header.setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive
            )
            header.setStretchLastSection(False)
            available = table.viewport().width()
            if available <= 0:
                continue
            widths = []
            remaining = available
            for ratio in ratios[:-1]:
                w = max(80, int(available * ratio))
                widths.append(w)
                remaining -= w
            widths.append(max(80, remaining))
            for idx, width in enumerate(widths):
                header.resizeSection(idx, width)
            table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

    def fit_table_to_rows(self, table, min_rows=2):
        row_count = max(table.rowCount(), min_rows)
        row_height = table.verticalHeader().defaultSectionSize()
        header_height = table.horizontalHeader().height() or 46
        frame_padding = 4
        table.setFixedHeight(header_height + (row_count * row_height) + frame_padding)

    def set_cell(self, table, row, col, text,
                 bold=False, align=None, color=None):
        item = QTableWidgetItem(str(text))
        if bold:
            item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
        if align is True or align == "center":
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
        elif align == "right":
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
        elif align == "left":
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
        if color:
            item.setForeground(QColor(color))
        table.setItem(row, col, item)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.equalize_menu_table_columns()

    def make_summary_card(self, title, value,
                          subtitle, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                border-left: 4px solid {color};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setOffset(0, 3)
        frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        val_lbl = QLabel(value)
        val_lbl.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        val_lbl.setStyleSheet(f"color: {color};")

        title_lbl = QLabel(title.upper())
        title_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; "
            f"letter-spacing: 1px;"
        )

        sub_lbl = QLabel(subtitle)
        sub_lbl.setFont(QFont("Segoe UI", 10))
        sub_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']};"
        )

        layout.addWidget(val_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)

        return frame
