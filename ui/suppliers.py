import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QMessageBox, QGraphicsDropShadowEffect, QTabWidget,
    QMenu, QDateEdit, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QCursor
from services.supplier_service import (
    get_all_suppliers, add_supplier, update_supplier,
    toggle_supplier_status, get_purchase_orders,
    get_po_items, create_purchase_order,
    receive_purchase_order, cancel_purchase_order,
    get_supplier_stats
)
from services.inventory_service import get_all_ingredients
from assets.styles import (
    COLORS, primary_button, outline_button,
    table_stylesheet, configure_table
)


# ── Status colours ────────────────────────────────────────────
PO_STATUS_COLORS = {
    "Pending":   (COLORS['warning'], "#fef3c7"),
    "Received":  (COLORS['accent'],  "#dcfce7"),
    "Cancelled": (COLORS['danger'],  "#fee2e2"),
}


# ── Supplier dialog ───────────────────────────────────────────
class SupplierDialog(QDialog):
    def __init__(self, parent=None, supplier=None):
        super().__init__(parent)
        self.supplier = supplier
        self.setWindowTitle(
            "Edit Supplier" if supplier else "Add Supplier"
        )
        self.setFixedSize(440, 400)
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
            "Edit Supplier" if self.supplier
            else "Add New Supplier"
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
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        self.name_input    = QLineEdit()
        self.contact_input = QLineEdit()
        self.phone_input   = QLineEdit()
        self.email_input   = QLineEdit()
        self.address_input = QLineEdit()

        for widget, placeholder in [
            (self.name_input,    "e.g. Fresh Farms Ltd"),
            (self.contact_input, "e.g. John Kamau"),
            (self.phone_input,   "e.g. +254 711 000 001"),
            (self.email_input,   "e.g. info@freshfarms.co.ke"),
            (self.address_input, "e.g. Nairobi, Kenya"),
        ]:
            widget.setPlaceholderText(placeholder)
            widget.setFixedHeight(40)
            widget.setStyleSheet(input_style)

        for lbl, widget in [
            ("Supplier Name *", self.name_input),
            ("Contact Person",  self.contact_input),
            ("Phone",           self.phone_input),
            ("Email",           self.email_input),
            ("Address",         self.address_input),
        ]:
            l = QLabel(lbl)
            l.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            l.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )
            form.addRow(l, widget)

        if self.supplier:
            self.name_input.setText(self.supplier[1])
            self.contact_input.setText(self.supplier[2] or "")
            self.phone_input.setText(self.supplier[3] or "")
            self.email_input.setText(self.supplier[4] or "")
            self.address_input.setText(self.supplier[5] or "")

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

        save_btn = QPushButton("Save Supplier")
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
                "Supplier name is required."
            )
            return
        self.result_data = {
            "name":         name,
            "contact_name": self.contact_input.text().strip(),
            "phone":        self.phone_input.text().strip(),
            "email":        self.email_input.text().strip(),
            "address":      self.address_input.text().strip(),
        }
        self.accept()


# ── Create PO dialog ──────────────────────────────────────────
class CreatePODialog(QDialog):
    def __init__(self, suppliers, ingredients,
                 parent=None):
        super().__init__(parent)
        self.suppliers   = suppliers
        self.ingredients = ingredients
        self.po_items    = []
        self.setWindowTitle("Create Purchase Order")
        self.setMinimumSize(620, 580)
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

        title = QLabel("Create Purchase Order")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        input_style = f"""
            QComboBox, QLineEdit, QDateEdit {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QComboBox:focus, QLineEdit:focus,
            QDateEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
        """

        # Supplier selector
        sup_row = QHBoxLayout()
        sup_lbl = QLabel("Supplier *")
        sup_lbl.setFont(
            QFont("Segoe UI", 11, QFont.Weight.Bold)
        )
        sup_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        sup_lbl.setFixedWidth(120)

        self.supplier_combo = QComboBox()
        self.supplier_combo.setFixedHeight(40)
        self.supplier_combo.setStyleSheet(input_style)
        for s in self.suppliers:
            self.supplier_combo.addItem(s[1], s[0])

        sup_row.addWidget(sup_lbl)
        sup_row.addWidget(self.supplier_combo)

        # Expected date
        date_row = QHBoxLayout()
        date_lbl = QLabel("Expected Date")
        date_lbl.setFont(
            QFont("Segoe UI", 11, QFont.Weight.Bold)
        )
        date_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        date_lbl.setFixedWidth(120)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(
            QDate.currentDate().addDays(3)
        )
        self.date_edit.setFixedHeight(40)
        self.date_edit.setStyleSheet(input_style)

        date_row.addWidget(date_lbl)
        date_row.addWidget(self.date_edit)

        # Notes
        notes_row = QHBoxLayout()
        notes_lbl = QLabel("Notes")
        notes_lbl.setFont(
            QFont("Segoe UI", 11, QFont.Weight.Bold)
        )
        notes_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        notes_lbl.setFixedWidth(120)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(
            "Optional notes..."
        )
        self.notes_input.setFixedHeight(40)
        self.notes_input.setStyleSheet(input_style)

        notes_row.addWidget(notes_lbl)
        notes_row.addWidget(self.notes_input)

        # Add item row
        add_item_frame = QFrame()
        add_item_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
            QLabel {{
                background: transparent;
                color: {COLORS['text_secondary']};
            }}
        """)
        add_item_layout = QHBoxLayout(add_item_frame)
        add_item_layout.setContentsMargins(12, 10, 12, 10)
        add_item_layout.setSpacing(8)

        self.ing_combo = QComboBox()
        self.ing_combo.setFixedHeight(36)
        self.ing_combo.setStyleSheet(input_style)
        for ing in self.ingredients:
            self.ing_combo.addItem(
                f"{ing[1]} ({ing[2]})", ing[0]
            )

        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setRange(0.01, 99999)
        self.qty_spin.setDecimals(2)
        self.qty_spin.setValue(1)
        self.qty_spin.setFixedHeight(36)
        self.qty_spin.setFixedWidth(100)
        self.qty_spin.setStyleSheet(input_style)

        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 99999)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setPrefix("$")
        self.cost_spin.setFixedHeight(36)
        self.cost_spin.setFixedWidth(100)
        self.cost_spin.setStyleSheet(input_style)

        add_item_btn = QPushButton("+ Add")
        add_item_btn.setFixedHeight(36)
        add_item_btn.setFixedWidth(70)
        add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_item_btn.setStyleSheet(primary_button())
        add_item_btn.clicked.connect(self.add_item)

        add_item_layout.addWidget(QLabel("Item:"))
        add_item_layout.addWidget(self.ing_combo, 1)
        add_item_layout.addWidget(QLabel("Qty:"))
        add_item_layout.addWidget(self.qty_spin)
        add_item_layout.addWidget(QLabel("Cost:"))
        add_item_layout.addWidget(self.cost_spin)
        add_item_layout.addWidget(add_item_btn)

        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "INGREDIENT", "QTY", "UNIT COST",
            "SUBTOTAL", "REMOVE"
        ])
        self.items_table.setStyleSheet(
            table_stylesheet(
                border="1px solid {0}".format(COLORS['border']),
                border_radius="8px",
                item_padding="8px 10px",
                font_size="12px",
                header_padding="8px",
            )
        )
        self.items_table.setFixedHeight(180)
        self.items_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.items_table.setShowGrid(False)

        # Total row
        self.total_lbl = QLabel("Total:  $0.00")
        self.total_lbl.setFont(
            QFont("Segoe UI", 13, QFont.Weight.Bold)
        )
        self.total_lbl.setStyleSheet(
            f"color: {COLORS['accent']};"
        )
        self.total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Buttons
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

        create_btn = QPushButton("Create Purchase Order")
        create_btn.setFixedHeight(42)
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.setStyleSheet(primary_button())
        create_btn.clicked.connect(self.create_po)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(create_btn)

        layout.addWidget(title)
        layout.addWidget(div)
        layout.addLayout(sup_row)
        layout.addLayout(date_row)
        layout.addLayout(notes_row)
        layout.addWidget(add_item_frame)
        layout.addWidget(self.items_table)
        layout.addWidget(self.total_lbl)
        layout.addLayout(btn_row)

    def add_item(self):
        ing_id   = self.ing_combo.currentData()
        ing_name = self.ing_combo.currentText()
        qty      = self.qty_spin.value()
        cost     = self.cost_spin.value()
        subtotal = qty * cost

        # Check if already added
        for item in self.po_items:
            if item['ingredient_id'] == ing_id:
                QMessageBox.warning(
                    self, "Duplicate",
                    f"'{ing_name}' is already in the order."
                )
                return

        self.po_items.append({
            "ingredient_id": ing_id,
            "name":          ing_name,
            "quantity":      qty,
            "unit_cost":     cost,
        })
        self.refresh_items_table()

    def refresh_items_table(self):
        self.items_table.setRowCount(0)
        self.items_table.setRowCount(len(self.po_items))
        total = 0

        for idx, item in enumerate(self.po_items):
            self.items_table.setRowHeight(idx, 40)
            subtotal = item['quantity'] * item['unit_cost']
            total   += subtotal

            self.items_table.setItem(
                idx, 0,
                QTableWidgetItem(item['name'])
            )
            self.items_table.setItem(
                idx, 1,
                QTableWidgetItem(f"{item['quantity']:.2f}")
            )
            self.items_table.setItem(
                idx, 2,
                QTableWidgetItem(f"${item['unit_cost']:.2f}")
            )
            self.items_table.setItem(
                idx, 3,
                QTableWidgetItem(f"${subtotal:.2f}")
            )

            remove_btn = QPushButton("✕")
            remove_btn.setFixedSize(28, 28)
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['danger_light']};
                    color: {COLORS['danger']};
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['danger']};
                    color: white;
                }}
            """)
            remove_btn.clicked.connect(
                lambda _, i=idx: self.remove_item(i)
            )

            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(4, 0, 4, 0)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_layout.addWidget(remove_btn)
            self.items_table.setCellWidget(
                idx, 4, cell_widget
            )

        self.total_lbl.setText(f"Total:  ${total:.2f}")

    def remove_item(self, idx):
        self.po_items.pop(idx)
        self.refresh_items_table()

    def create_po(self):
        if not self.po_items:
            QMessageBox.warning(
                self, "No Items",
                "Please add at least one item to the order."
            )
            return

        supplier_id   = self.supplier_combo.currentData()
        expected_date = self.date_edit.date().toString(
            "yyyy-MM-dd"
        )
        notes         = self.notes_input.text().strip()

        self.result_data = {
            "supplier_id":   supplier_id,
            "expected_date": expected_date,
            "notes":         notes,
            "items":         self.po_items,
        }
        self.accept()


# ── PO items view dialog ──────────────────────────────────────
class POItemsDialog(QDialog):
    def __init__(self, po, items, parent=None):
        super().__init__(parent)
        self.po    = po
        self.items = items
        self.setWindowTitle(f"Purchase Order #{po[0]}")
        self.setFixedSize(500, 420)
        self.setStyleSheet(
            f"QDialog {{ background-color: {COLORS['bg_secondary']}; }}"
            f"QLabel {{ background: transparent; color: {COLORS['text_primary']}; font-family: Segoe UI; }}"
        )
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel(f"Purchase Order #{self.po[0]}")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        info_grid = QHBoxLayout()
        for label, value in [
            ("Supplier",  self.po[1]),
            ("Status",    self.po[2]),
            ("Created",   str(self.po[7])[:10]),
        ]:
            col = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 9))
            lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
            val = QLabel(value)
            val.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            col.addWidget(lbl)
            col.addWidget(val)
            info_grid.addLayout(col)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(
            f"background: {COLORS['border']}; border: none;"
        )

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "INGREDIENT", "QTY", "UNIT",
            "UNIT COST", "SUBTOTAL"
        ])
        table.setStyleSheet(
            table_stylesheet(
                background_color=COLORS['bg_tertiary'],
                border="1px solid {0}".format(COLORS['border']),
                border_radius="8px",
                item_padding="8px 10px",
                font_size="12px",
                header_background=COLORS['bg_secondary'],
                header_padding="8px",
            )
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        table.setShowGrid(False)
        table.setRowCount(len(self.items))

        for idx, item in enumerate(self.items):
            table.setRowHeight(idx, 42)
            table.setItem(idx, 0, QTableWidgetItem(item[1]))
            table.setItem(
                idx, 1,
                QTableWidgetItem(f"{float(item[3]):.2f}")
            )
            table.setItem(idx, 2, QTableWidgetItem(item[2]))
            table.setItem(
                idx, 3,
                QTableWidgetItem(f"${float(item[4]):.2f}")
            )
            table.setItem(
                idx, 4,
                QTableWidgetItem(f"${float(item[5]):.2f}")
            )

        total_lbl = QLabel(
            f"Total:  ${float(self.po[3]):.2f}"
        )
        total_lbl.setFont(
            QFont("Segoe UI", 13, QFont.Weight.Bold)
        )
        total_lbl.setStyleSheet(f"color: {COLORS['accent']};")
        total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(primary_button())
        close_btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addLayout(info_grid)
        layout.addWidget(div)
        layout.addWidget(table)
        layout.addWidget(total_lbl)
        layout.addWidget(close_btn)


# ── Main supplier widget ──────────────────────────────────────
class SupplierWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user        = user
        self.suppliers   = []
        self.ingredients = []
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

        page_title = QLabel("Supplier Management")
        page_title.setFont(
            QFont("Segoe UI", 20, QFont.Weight.Bold)
        )
        page_title.setStyleSheet(
            f"color: {COLORS['text_primary']};"
        )

        page_sub = QLabel(
            "Manage suppliers and purchase orders"
        )
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        add_sup_btn = QPushButton("⊕  Add Supplier")
        add_sup_btn.setFixedHeight(40)
        add_sup_btn.setFixedWidth(150)
        add_sup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_sup_btn.setStyleSheet(primary_button())
        add_sup_btn.clicked.connect(self.add_supplier)

        new_po_btn = QPushButton("📋  New Order")
        new_po_btn.setFixedHeight(40)
        new_po_btn.setFixedWidth(140)
        new_po_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_po_btn.setStyleSheet(
            outline_button(COLORS['blue'])
        )
        new_po_btn.clicked.connect(self.create_po)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(outline_button())
        refresh_btn.clicked.connect(self.load_data)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(refresh_btn)
        header_row.addWidget(new_po_btn)
        header_row.addWidget(add_sup_btn)

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
        """)

        # Tab 1: Suppliers
        self.sup_tab = QWidget()
        self.sup_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_suppliers_tab()
        self.tabs.addTab(self.sup_tab, "🏭  Suppliers")

        # Tab 2: Purchase Orders
        self.po_tab = QWidget()
        self.po_tab.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
        )
        self.setup_po_tab()
        self.tabs.addTab(self.po_tab, "📋  Purchase Orders")

        layout.addLayout(header_row)
        layout.addLayout(self.stats_row)
        layout.addWidget(self.tabs)

    def setup_suppliers_tab(self):
        layout = QVBoxLayout(self.sup_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.sup_table = QTableWidget()
        self.sup_table.setColumnCount(7)
        self.sup_table.setHorizontalHeaderLabels([
            "ID", "SUPPLIER NAME", "CONTACT",
            "PHONE", "ORDERS", "TOTAL VALUE",
            "ACTIONS"
        ])
        self.sup_table.setStyleSheet(
            table_stylesheet()
        )
        self.sup_table.setColumnWidth(0, 60)
        self.sup_table.setColumnWidth(3, 160)
        self.sup_table.setColumnWidth(4, 90)
        self.sup_table.setColumnWidth(5, 120)
        self.sup_table.setColumnWidth(6, 90)
        header = self.sup_table.horizontalHeader()
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
        self.sup_table.horizontalHeaderItem(1).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.sup_table.horizontalHeaderItem(2).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )
        header.setStretchLastSection(False)
        configure_table(self.sup_table, row_height=44)
        self.sup_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.sup_table)

    def setup_po_tab(self):
        layout = QVBoxLayout(self.po_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.po_table = QTableWidget()
        self.po_table.setColumnCount(7)
        self.po_table.setHorizontalHeaderLabels([
            "PO #", "SUPPLIER", "STATUS",
            "TOTAL", "EXPECTED DATE",
            "CREATED", "ACTIONS"
        ])
        self.po_table.setStyleSheet(
            table_stylesheet()
        )
        self.po_table.setColumnWidth(0, 90)
        self.po_table.setColumnWidth(1, 180)
        self.po_table.setColumnWidth(2, 120)
        self.po_table.setColumnWidth(3, 110)
        self.po_table.setColumnWidth(4, 130)
        self.po_table.setColumnWidth(5, 120)
        self.po_table.setColumnWidth(6, 90)
        header = self.po_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.setStretchLastSection(False)
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.po_table.horizontalHeaderItem(0).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.po_table.horizontalHeaderItem(1).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )
        configure_table(self.po_table, row_height=44)
        self.po_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.po_table)

    def load_data(self):
        self.suppliers   = get_all_suppliers()
        self.ingredients = get_all_ingredients()
        stats            = get_supplier_stats()

        # Rebuild stats
        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, value, color in [
            ("Total Suppliers",
             stats.get("total", 0),         COLORS['blue']),
            ("Active Suppliers",
             stats.get("active", 0),        COLORS['accent']),
            ("Purchase Orders",
             stats.get("total_orders", 0),  COLORS['warning']),
            ("Total Spend",
             f"${stats.get('total_value', 0):.2f}",
             "#7c3aed"),
        ]:
            pill = self.build_stat_pill(label, value, color)
            self.stats_row.addWidget(pill)
        self.stats_row.addStretch()

        self.populate_suppliers()
        self.populate_po_table()

    def populate_suppliers(self):
        self.sup_table.setRowCount(0)
        self.sup_table.setRowCount(len(self.suppliers))

        for idx, sup in enumerate(self.suppliers):
            self.sup_table.setRowHeight(idx, 44)

            id_item = QTableWidgetItem(str(sup[0]))
            id_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            id_item.setForeground(
                QColor(COLORS['text_muted'])
            )
            self.sup_table.setItem(idx, 0, id_item)

            name_item = QTableWidgetItem(sup[1])
            name_item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
            name_item.setForeground(QColor(COLORS['accent']))
            self.sup_table.setItem(idx, 1, name_item)

            contact_item = QTableWidgetItem(sup[2] or "—")
            contact_item.setForeground(
                QColor(COLORS['text_secondary'])
            )
            self.sup_table.setItem(idx, 2, contact_item)

            phone_item = QTableWidgetItem(sup[3] or "—")
            phone_item.setForeground(
                QColor(COLORS['text_secondary'])
            )
            self.sup_table.setItem(idx, 3, phone_item)

            orders_item = QTableWidgetItem(str(sup[8]))
            orders_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self.sup_table.setItem(idx, 4, orders_item)

            value_item = QTableWidgetItem(
                f"${float(sup[9]):.2f}"
            )
            value_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            value_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            value_item.setForeground(
                QColor(COLORS['text_primary'])
            )
            self.sup_table.setItem(idx, 5, value_item)

            dots_btn = QPushButton("⋮")
            dots_btn.setFixedSize(28, 28)
            dots_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            dots_btn.setToolTip("Actions")
            dots_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #9ca3af;
                    border: 1px solid #e5e7eb;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                    padding-bottom: 3px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent_light']};
                    border-color: {COLORS['accent']};
                    color: {COLORS['accent']};
                }}
            """)
            dots_btn.clicked.connect(
                lambda _, s=sup:
                self.show_supplier_menu(s)
            )

            cell = QWidget()
            cell.setStyleSheet("background: transparent;")
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            cell_layout.addWidget(dots_btn)
            self.sup_table.setCellWidget(idx, 6, cell)

    def populate_po_table(self):
        orders = get_purchase_orders()
        self.po_table.setRowCount(0)
        self.po_table.setRowCount(len(orders))

        for idx, po in enumerate(orders):
            self.po_table.setRowHeight(idx, 44)

            self.po_table.setItem(
                idx, 0,
                QTableWidgetItem(f"#{po[0]}")
            )

            sup_item = QTableWidgetItem(po[1])
            sup_item.setForeground(QColor(COLORS['accent']))
            sup_item.setFont(
                QFont("Segoe UI", 12, QFont.Weight.Bold)
            )
            self.po_table.setItem(idx, 1, sup_item)

            # Status badge
            status       = po[2]
            s_color, s_bg = PO_STATUS_COLORS.get(
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
            self.po_table.setCellWidget(idx, 2, badge_widget)

            total_item = QTableWidgetItem(
                f"${float(po[3]):.2f}"
            )
            total_item.setFont(
                QFont("Segoe UI", 11, QFont.Weight.Bold)
            )
            total_item.setForeground(
                QColor(COLORS['text_primary'])
            )
            self.po_table.setItem(idx, 3, total_item)

            exp_date = str(po[4])[:10] if po[4] else "—"
            self.po_table.setItem(
                idx, 4, QTableWidgetItem(exp_date)
            )

            created = str(po[7])[:10]
            self.po_table.setItem(
                idx, 5, QTableWidgetItem(created)
            )

            dots_btn = QPushButton("⋮")
            dots_btn.setFixedSize(28, 28)
            dots_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            dots_btn.setToolTip("Actions")
            dots_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #9ca3af;
                    border: 1px solid #e5e7eb;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                    padding-bottom: 3px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent_light']};
                    border-color: {COLORS['accent']};
                    color: {COLORS['accent']};
                }}
            """)
            dots_btn.clicked.connect(
                lambda _, p=po:
                self.show_po_menu(p)
            )

            cell = QWidget()
            cell.setStyleSheet("background: transparent;")
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            cell_layout.addWidget(dots_btn)
            self.po_table.setCellWidget(idx, 6, cell)

    def show_supplier_menu(self, supplier):
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

        edit_action   = menu.addAction("✏️   Edit Supplier")
        new_po_action = menu.addAction("📋  New Purchase Order")
        menu.addSeparator()
        toggle_label  = (
            "🔴  Deactivate" if supplier[6]
            else "🟢  Activate"
        )
        toggle_action = menu.addAction(toggle_label)

        action = menu.exec(QCursor.pos())

        if action == edit_action:
            self.edit_supplier(supplier)
        elif action == new_po_action:
            self.create_po(supplier_id=supplier[0])
        elif action == toggle_action:
            self.toggle_supplier(supplier)

    def show_po_menu(self, po):
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

        view_action = menu.addAction("👁   View Items")

        if po[2] == "Pending":
            receive_action = menu.addAction(
                "✅  Receive Stock"
            )
            menu.addSeparator()
            cancel_action  = menu.addAction(
                "🗑️   Cancel Order"
            )
        else:
            receive_action = None
            cancel_action  = None

        action = menu.exec(QCursor.pos())

        if action == view_action:
            items  = get_po_items(po[0])
            dialog = POItemsDialog(po, items, self)
            dialog.exec()
        elif receive_action and action == receive_action:
            self.receive_po(po)
        elif cancel_action and action == cancel_action:
            self.cancel_po(po)

    def add_supplier(self):
        dialog = SupplierDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = add_supplier(
                d['name'], d['contact_name'],
                d['phone'], d['email'], d['address']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to add supplier."
                )

    def edit_supplier(self, supplier):
        dialog = SupplierDialog(self, supplier=supplier)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d       = dialog.result_data
            success = update_supplier(
                supplier[0], d['name'], d['contact_name'],
                d['phone'], d['email'], d['address']
            )
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to update supplier."
                )

    def toggle_supplier(self, supplier):
        success = toggle_supplier_status(
            supplier[0], supplier[6]
        )
        if success:
            self.load_data()

    def create_po(self, supplier_id=None):
        active_suppliers = [
            s for s in self.suppliers if s[6]
        ]
        if not active_suppliers:
            QMessageBox.warning(
                self, "No Suppliers",
                "Please add an active supplier first."
            )
            return

        dialog = CreatePODialog(
            active_suppliers, self.ingredients, self
        )

        if supplier_id:
            for i, s in enumerate(active_suppliers):
                if s[0] == supplier_id:
                    dialog.supplier_combo.setCurrentIndex(i)
                    break

        if dialog.exec() == QDialog.DialogCode.Accepted:
            d      = dialog.result_data
            po_id  = create_purchase_order(
                d['supplier_id'],
                self.user['user_id'],
                d['items'],
                d['notes'],
                d['expected_date']
            )
            if po_id:
                QMessageBox.information(
                    self, "Success",
                    f"Purchase Order #{po_id} created successfully."
                )
                self.load_data()
                self.tabs.setCurrentIndex(1)
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to create purchase order."
                )

    def receive_po(self, po):
        reply = QMessageBox.question(
            self, "Receive Stock",
            f"Receive all items from PO #{po[0]}?\n\n"
            f"This will update inventory stock levels.",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = receive_purchase_order(
                po[0], self.user['user_id']
            )
            if success:
                QMessageBox.information(
                    self, "Success",
                    f"Stock received from PO #{po[0]}.\n"
                    f"Inventory has been updated."
                )
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to receive purchase order."
                )

    def cancel_po(self, po):
        reply = QMessageBox.question(
            self, "Cancel Order",
            f"Cancel Purchase Order #{po[0]}?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = cancel_purchase_order(po[0])
            if success:
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to cancel purchase order."
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
