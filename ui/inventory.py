from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QMessageBox, QGraphicsDropShadowEffect,
    QTabWidget, QTextEdit, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QCursor
from services.inventory_service import (
    get_all_ingredients, get_all_suppliers,
    add_ingredient, update_ingredient,
    stock_in, stock_out, adjust_stock,
    get_transactions, get_inventory_stats,
    delete_ingredient
)
from assets.styles import (
    COLORS, primary_button, outline_button,
    table_stylesheet, configure_table
)


# ── Stock status colours ──────────────────────────────────────
STOCK_STATUS_COLORS = {
    "In Stock":     (COLORS['accent'],  "#dcfce7"),
    "Reorder Soon": (COLORS['warning'], "#fef3c7"),
    "Low Stock":    (COLORS['danger'],  "#fee2e2"),
    "Out of Stock": ("#7c3aed",         "#ede9fe"),
}


# ── Stock In dialog ───────────────────────────────────────────
class StockInDialog(QDialog):
    def __init__(self, ingredient, parent=None):
        super().__init__(parent)
        self.ingredient = ingredient
        self.setWindowTitle(f"Stock In — {ingredient[1]}")
        self.setFixedSize(400, 340)
        self.setStyleSheet(
            f"QDialog {{ background-color: {COLORS['bg_secondary']}; }}"
            f"QLabel {{ background: transparent; color: {COLORS['text_primary']}; font-family: Segoe UI; }}"
        )
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel(f"Stock In — {self.ingredient[1]}")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        current = QLabel(
            f"Current Stock:  {self.ingredient[3]:.2f} {self.ingredient[2]}"
        )
        current.setFont(QFont("Segoe UI", 11))
        current.setStyleSheet(f"color: {COLORS['text_secondary']};")

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        form   = QFormLayout()
        form.setSpacing(12)

        input_style = f"""
            QLineEdit, QDoubleSpinBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QDoubleSpinBox:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setRange(0.01, 99999)
        self.qty_spin.setDecimals(2)
        self.qty_spin.setValue(1.00)
        self.qty_spin.setSuffix(f"  {self.ingredient[2]}")
        self.qty_spin.setFixedHeight(40)
        self.qty_spin.setStyleSheet(input_style)

        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 99999)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setValue(float(self.ingredient[6]))
        self.cost_spin.setPrefix("$")
        self.cost_spin.setFixedHeight(40)
        self.cost_spin.setStyleSheet(input_style)

        self.ref_input = QLineEdit()
        self.ref_input.setPlaceholderText(
            "e.g. Invoice #123  (optional)"
        )
        self.ref_input.setFixedHeight(40)
        self.ref_input.setStyleSheet(input_style)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes")
        self.notes_input.setFixedHeight(40)
        self.notes_input.setStyleSheet(input_style)

        for lbl, widget in [
            ("Quantity *",      self.qty_spin),
            ("Unit Cost *",     self.cost_spin),
            ("Reference No",    self.ref_input),
            ("Notes",           self.notes_input),
        ]:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
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

        confirm_btn = QPushButton("✓  Confirm Stock In")
        confirm_btn.setFixedHeight(42)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(primary_button())
        confirm_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)

        layout.addWidget(title)
        layout.addWidget(current)
        layout.addWidget(div)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "quantity":     self.qty_spin.value(),
            "unit_cost":    self.cost_spin.value(),
            "reference_no": self.ref_input.text().strip(),
            "notes":        self.notes_input.text().strip(),
        }


# ── Stock Out dialog ──────────────────────────────────────────
class StockOutDialog(QDialog):
    def __init__(self, ingredient, parent=None):
        super().__init__(parent)
        self.ingredient = ingredient
        self.setWindowTitle(f"Stock Out — {ingredient[1]}")
        self.setFixedSize(380, 260)
        self.setStyleSheet(
            f"QDialog {{ background-color: {COLORS['bg_secondary']}; }}"
            f"QLabel {{ background: transparent; color: {COLORS['text_primary']}; font-family: Segoe UI; }}"
        )
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel(f"Stock Out — {self.ingredient[1]}")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        current = QLabel(
            f"Current Stock:  {self.ingredient[3]:.2f} {self.ingredient[2]}"
        )
        current.setFont(QFont("Segoe UI", 11))
        current.setStyleSheet(f"color: {COLORS['text_secondary']};")

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        form = QFormLayout()
        form.setSpacing(12)

        input_style = f"""
            QDoubleSpinBox, QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QDoubleSpinBox:focus, QLineEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setRange(0.01, 999999)
        self.qty_spin.setDecimals(2)
        self.qty_spin.setValue(1.00)
        self.qty_spin.setSuffix(f"  {self.ingredient[2]}")
        self.qty_spin.setFixedHeight(40)
        self.qty_spin.setStyleSheet(input_style)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(
            "Reason for stock out  (optional)"
        )
        self.notes_input.setFixedHeight(40)
        self.notes_input.setStyleSheet(input_style)

        for lbl, widget in [
            ("Quantity *", self.qty_spin),
            ("Notes",      self.notes_input),
        ]:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
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

        confirm_btn = QPushButton("✓  Confirm Stock Out")
        confirm_btn.setFixedHeight(42)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(
            primary_button(COLORS['danger'])
        )
        confirm_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)

        layout.addWidget(title)
        layout.addWidget(current)
        layout.addWidget(div)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "quantity": self.qty_spin.value(),
            "notes":    self.notes_input.text().strip(),
        }


# ── Add/Edit ingredient dialog ────────────────────────────────
class IngredientDialog(QDialog):
    def __init__(self, parent=None,
                 ingredient=None, suppliers=None):
        super().__init__(parent)
        self.ingredient = ingredient
        self.suppliers  = suppliers or []
        self.setWindowTitle(
            "Edit Ingredient" if ingredient
            else "Add Ingredient"
        )
        self.setFixedSize(440, 420)
        self.setStyleSheet(
            f"QDialog {{ background-color: {COLORS['bg_secondary']}; }}"
            f"QLabel {{ background: transparent; color: {COLORS['text_primary']}; font-family: Segoe UI; }}"
        )
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel(
            "Edit Ingredient" if self.ingredient
            else "Add New Ingredient"
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
            QLineEdit, QDoubleSpinBox, QComboBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QDoubleSpinBox:focus,
            QComboBox:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Maize Flour")
        self.name_input.setFixedHeight(40)
        self.name_input.setStyleSheet(input_style)

        self.unit_combo = QComboBox()
        self.unit_combo.setFixedHeight(40)
        self.unit_combo.setStyleSheet(input_style)
        for unit in ["kg", "g", "ltr", "ml",
                     "pcs", "dozen", "bag", "box"]:
            self.unit_combo.addItem(unit)

        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(0, 99999)
        self.min_spin.setDecimals(2)
        self.min_spin.setFixedHeight(40)
        self.min_spin.setStyleSheet(input_style)

        self.reorder_spin = QDoubleSpinBox()
        self.reorder_spin.setRange(0, 99999)
        self.reorder_spin.setDecimals(2)
        self.reorder_spin.setFixedHeight(40)
        self.reorder_spin.setStyleSheet(input_style)

        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 99999)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setPrefix("$")
        self.cost_spin.setFixedHeight(40)
        self.cost_spin.setStyleSheet(input_style)

        self.supplier_combo = QComboBox()
        self.supplier_combo.setFixedHeight(40)
        self.supplier_combo.setStyleSheet(input_style)
        self.supplier_combo.addItem("— None —", None)
        for s in self.suppliers:
            self.supplier_combo.addItem(s[1], s[0])

        for lbl, widget in [
            ("Name *",          self.name_input),
            ("Unit *",          self.unit_combo),
            ("Minimum Stock *", self.min_spin),
            ("Reorder Level *", self.reorder_spin),
            ("Unit Cost *",     self.cost_spin),
            ("Supplier",        self.supplier_combo),
        ]:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
            form.addRow(l, widget)

        if self.ingredient:
            self.name_input.setText(self.ingredient[1])
            idx = self.unit_combo.findText(self.ingredient[2])
            if idx >= 0:
                self.unit_combo.setCurrentIndex(idx)
            self.min_spin.setValue(float(self.ingredient[4]))
            self.reorder_spin.setValue(
                float(self.ingredient[5])
            )
            self.cost_spin.setValue(float(self.ingredient[6]))

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

        save_btn = QPushButton("Save Ingredient")
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
                self, "Validation", "Name is required."
            )
            return
        self.result_data = {
            "name":          name,
            "unit":          self.unit_combo.currentText(),
            "minimum_stock": self.min_spin.value(),
            "reorder_level": self.reorder_spin.value(),
            "unit_cost":     self.cost_spin.value(),
            "supplier_id":   self.supplier_combo.currentData(),
        }
        self.accept()


# ── Main inventory widget ─────────────────────────────────────
class InventoryWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user        = user
        self.ingredients = []
        self.suppliers   = []
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

        page_title = QLabel("Inventory Management")
        page_title.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        page_title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        page_sub = QLabel(
            "Track ingredients, stock levels and transactions"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        add_btn = QPushButton("⊕  Add Ingredient")
        add_btn.setFixedHeight(40)
        add_btn.setFixedWidth(160)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(primary_button())
        add_btn.clicked.connect(self.add_ingredient)

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

        # ── Tabs ──────────────────────────────────────────────
        self.tabs = QTabWidget()
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
                padding: 8px 20px;
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

        # Tab 1: Ingredients
        self.ingredients_tab = QWidget()
        self.ingredients_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_ingredients_tab()
        self.tabs.addTab(self.ingredients_tab, "📦  Ingredients")

        # Tab 2: Transactions
        self.transactions_tab = QWidget()
        self.transactions_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_transactions_tab()
        self.tabs.addTab(
            self.transactions_tab, "🔄  Transaction History"
        )

        layout.addLayout(header_row)
        layout.addLayout(self.stats_row)
        layout.addWidget(self.tabs)

    def setup_ingredients_tab(self):
        layout = QVBoxLayout(self.ingredients_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 0, 12, 0)
        toolbar_layout.setSpacing(8)

        for label in ["CSV", "XLS", "PDF", "Print"]:
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_secondary']};
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
                background-color: {COLORS['bg_secondary']};
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
        self.search_input.setPlaceholderText("Search...")
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
            self.filter_ingredients
        )

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_frame)

        # Ingredients table
        self.ing_table = QTableWidget()
        self.ing_table.setColumnCount(9)
        self.ing_table.setHorizontalHeaderLabels([
            "ID", "INGREDIENT", "UNIT",
            "CURRENT STOCK", "MIN STOCK",
            "UNIT COST", "STOCK VALUE",
            "STATUS", "ACTIONS"
        ])
        self.ing_table.setStyleSheet(
            table_stylesheet(
                item_padding="0 12px",
                header_padding="14px 16px",
                header_font_size="12px"
            )
        )

        self.ing_table.setColumnWidth(0, 70)
        self.ing_table.setColumnWidth(2, 80)
        self.ing_table.setColumnWidth(3, 120)
        self.ing_table.setColumnWidth(4, 110)
        self.ing_table.setColumnWidth(5, 100)
        self.ing_table.setColumnWidth(6, 110)
        self.ing_table.setColumnWidth(7, 160)
        self.ing_table.setColumnWidth(8, 120)
        header = self.ing_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        header.setStretchLastSection(False)
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.ing_table.horizontalHeaderItem(1).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )
        configure_table(self.ing_table, row_height=58)
        self.ing_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        table_wrapper = QFrame()
        table_wrapper.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 16px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        table_wrapper.setGraphicsEffect(shadow)
        table_layout = QVBoxLayout(table_wrapper)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_layout.addWidget(self.ing_table)

        layout.addWidget(toolbar)
        layout.addWidget(table_wrapper)

    def setup_transactions_tab(self):
        layout = QVBoxLayout(self.transactions_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.tx_table = QTableWidget()
        self.tx_table.setColumnCount(7)
        self.tx_table.setHorizontalHeaderLabels([
            "DATE", "INGREDIENT", "TYPE",
            "QUANTITY", "UNIT COST",
            "REFERENCE", "PERFORMED BY"
        ])
        self.tx_table.setStyleSheet(
            table_stylesheet(
                item_padding="0 12px",
                header_padding="14px 16px",
                header_font_size="12px"
            )
        )

        self.tx_table.setColumnWidth(0, 120)
        self.tx_table.setColumnWidth(1, 240)
        self.tx_table.setColumnWidth(2, 140)
        self.tx_table.setColumnWidth(3, 150)
        self.tx_table.setColumnWidth(4, 100)
        self.tx_table.setColumnWidth(5, 140)
        self.tx_table.setColumnWidth(6, 120)

        header = self.tx_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.tx_table.horizontalHeaderItem(0).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.tx_table.horizontalHeaderItem(1).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )

        configure_table(self.tx_table, row_height=48)
        self.tx_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        table_wrapper = QFrame()
        table_wrapper.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 16px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        table_wrapper.setGraphicsEffect(shadow)
        table_layout = QVBoxLayout(table_wrapper)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_layout.addWidget(self.tx_table)

        layout.addWidget(table_wrapper)

    def load_data(self):
        self.suppliers   = get_all_suppliers()
        self.ingredients = get_all_ingredients()
        stats            = get_inventory_stats()

        # Rebuild stats
        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, value, color in [
            ("Total Ingredients",
             stats.get("total", 0),         COLORS['blue']),
            ("Low Stock",
             stats.get("low_stock", 0),     COLORS['danger']),
            ("Out of Stock",
             stats.get("out_of_stock", 0),  "#7c3aed"),
            ("Stock Value",
             f"${stats.get('total_value', 0):.2f}",
             COLORS['accent']),
        ]:
            pill = self.build_stat_pill(label, value, color)
            self.stats_row.addWidget(pill)
        self.stats_row.addStretch()

        self.populate_ingredients(self.ingredients)
        self.populate_transactions()

    def populate_ingredients(self, items):
        self.ing_table.setRowCount(0)
        self.ing_table.setRowCount(len(items))

        for row_idx, item in enumerate(items):
            self.ing_table.setRowHeight(row_idx, 58)

            # ID
            id_item = QTableWidgetItem(str(item[0]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setForeground(QColor(COLORS['text_muted']))
            self.ing_table.setItem(row_idx, 0, id_item)

            # Name
            name_item = QTableWidgetItem(item[1])
            name_item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
            name_item.setForeground(
                QColor(COLORS['accent'])
            )
            self.ing_table.setItem(row_idx, 1, name_item)

            # Unit
            unit_item = QTableWidgetItem(item[2])
            unit_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            unit_item.setForeground(
                QColor(COLORS['text_muted'])
            )
            self.ing_table.setItem(row_idx, 2, unit_item)

            # Current stock
            stock = item[3]
            min_s = item[4]
            stock_color = (
                COLORS['danger'] if stock <= min_s
                else COLORS['text_primary']
            )
            stock_item = QTableWidgetItem(
                f"{stock:.2f} {item[2]}"
            )
            stock_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            stock_item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
            stock_item.setForeground(QColor(stock_color))
            self.ing_table.setItem(row_idx, 3, stock_item)

            # Min stock
            min_item = QTableWidgetItem(
                f"{item[4]:.2f} {item[2]}"
            )
            min_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            min_item.setForeground(
                QColor(COLORS['text_secondary'])
            )
            self.ing_table.setItem(row_idx, 4, min_item)

            # Unit cost
            cost_item = QTableWidgetItem(f"${item[6]:.2f}")
            cost_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            cost_item.setForeground(
                QColor(COLORS['text_secondary'])
            )
            self.ing_table.setItem(row_idx, 5, cost_item)

            # Stock value
            stock_value = float(item[3]) * float(item[6])
            val_item = QTableWidgetItem(f"${stock_value:.2f}")
            val_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            val_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            val_item.setForeground(
                QColor(COLORS['text_primary'])
            )
            self.ing_table.setItem(row_idx, 6, val_item)

            # Status badge
            status       = item[9]
            s_color, s_bg = STOCK_STATUS_COLORS.get(
                status,
                (COLORS['text_muted'], COLORS['bg_tertiary'])
            )
            badge_widget = QWidget()
            badge_widget.setStyleSheet("background: transparent;")
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
            self.ing_table.setCellWidget(
                row_idx, 7, badge_widget
            )

            # Actions — three dot menu
            action_widget = QWidget()
            action_widget.setStyleSheet(
                "background: transparent;"
            )
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

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
                    border-color: {COLORS['border_strong']};
                }}
            """)
            dots_btn.clicked.connect(
                lambda _, i=item:
                self.show_action_menu(i)
            )
            action_layout.addWidget(dots_btn)
            self.ing_table.setCellWidget(
                row_idx, 8, action_widget
            )

    def populate_transactions(self):
        transactions = get_transactions(limit=100)
        self.tx_table.setRowCount(0)
        self.tx_table.setRowCount(len(transactions))

        type_colors = {
            "Stock In":   COLORS['accent'],
            "Stock Out":  COLORS['danger'],
            "Adjustment": COLORS['warning'],
        }

        for row_idx, tx in enumerate(transactions):
            self.tx_table.setRowHeight(row_idx, 48)

            # Date
            date_str = str(tx[9])[:16]
            date_item = QTableWidgetItem(date_str)
            date_item.setForeground(
                QColor(COLORS['text_secondary'])
            )
            self.tx_table.setItem(row_idx, 0, date_item)

            # Ingredient name
            name_item = QTableWidgetItem(tx[1])
            name_item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
            name_item.setForeground(QColor(COLORS['accent']))
            self.tx_table.setItem(row_idx, 1, name_item)

            # Type with colour
            type_color = type_colors.get(
                tx[2], COLORS['text_primary']
            )
            type_item = QTableWidgetItem(tx[2])
            type_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            type_item.setForeground(QColor(type_color))
            self.tx_table.setItem(row_idx, 2, type_item)

            # Quantity
            qty_item = QTableWidgetItem(
                f"{tx[3]:.2f} {tx[4]}"
            )
            qty_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self.tx_table.setItem(row_idx, 3, qty_item)

            # Unit cost
            cost_item = QTableWidgetItem(
                f"${tx[5]:.2f}" if tx[5] else "—"
            )
            cost_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self.tx_table.setItem(row_idx, 4, cost_item)

            # Reference
            ref_item = QTableWidgetItem(tx[6] or "—")
            ref_item.setForeground(
                QColor(COLORS['text_muted'])
            )
            self.tx_table.setItem(row_idx, 5, ref_item)

            # Performed by
            by_item = QTableWidgetItem(tx[8])
            by_item.setForeground(
                QColor(COLORS['text_secondary'])
            )
            self.tx_table.setItem(row_idx, 6, by_item)

    def show_action_menu(self, item):
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

        stock_in_action  = menu.addAction("📥  Stock In")
        stock_out_action = menu.addAction("📤  Stock Out")
        menu.addSeparator()
        edit_action      = menu.addAction("✏️   Edit Ingredient")
        menu.addSeparator()
        delete_action    = menu.addAction("🗑️   Remove Ingredient")

        action = menu.exec(QCursor.pos())

        if action == stock_in_action:
            self.do_stock_in(item)
        elif action == stock_out_action:
            self.do_stock_out(item)
        elif action == edit_action:
            self.edit_ingredient(item)
        elif action == delete_action:
            self.do_delete(item)

    def filter_ingredients(self, text):
        filtered = [
            i for i in self.ingredients
            if text.lower() in i[1].lower()
        ]
        self.populate_ingredients(filtered)

    def do_stock_in(self, item):
        dialog = StockInDialog(item, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.get_data()
            success = stock_in(
                item[0], d['quantity'], d['unit_cost'],
                d['reference_no'], d['notes'],
                self.user['user_id']
            )
            if success:
                QMessageBox.information(
                    self, "Success",
                    f"Stock updated successfully.\n"
                    f"New stock: "
                    f"{float(item[3]) + d['quantity']:.2f} {item[2]}"
                )
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to update stock."
                )

    def do_stock_out(self, item):
        current_stock = float(item[3])
        if current_stock <= 0:
            QMessageBox.warning(
                self, "Out of Stock",
                f"'{item[1]}' is currently out of stock.\n"
                f"Please restock before issuing."
            )
            return
        dialog = StockOutDialog(item, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d = dialog.get_data()
            if d['quantity'] > current_stock:
                QMessageBox.warning(
                    self, "Insufficient Stock",
                    f"Cannot issue {d['quantity']:.2f} {item[2]} of '{item[1]}'.\n\n"
                    f"Current stock: {current_stock:.2f} {item[2]}\n"
                    f"Requested:     {d['quantity']:.2f} {item[2]}\n\n"
                    f"Please enter a quantity within the available stock."
                )
                return
            success = stock_out(
                item[0], d['quantity'],
                d['notes'], self.user['user_id']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to update stock."
                )
    def add_ingredient(self):
        dialog = IngredientDialog(
            self, suppliers=self.suppliers
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = add_ingredient(
                d['name'], d['unit'], d['minimum_stock'],
                d['reorder_level'], d['unit_cost'],
                d['supplier_id']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to add ingredient. "
                    "Name may already exist."
                )

    def edit_ingredient(self, item):
        dialog = IngredientDialog(
            self, ingredient=item, suppliers=self.suppliers
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = update_ingredient(
                item[0], d['name'], d['unit'],
                d['minimum_stock'], d['reorder_level'],
                d['unit_cost'], d['supplier_id']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to update ingredient."
                )

    def do_delete(self, item):
        reply = QMessageBox.question(
            self, "Remove Ingredient",
            f"Remove '{item[1]}' from inventory?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = delete_ingredient(item[0])
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to remove ingredient."
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
