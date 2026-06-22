from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QComboBox, QMessageBox, QHeaderView, QFrame,
    QGraphicsDropShadowEffect, QMenu
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QColor, QCursor
from services.menu_service import (
    get_all_menu_items, get_all_categories, add_menu_item,
    update_menu_item, delete_menu_item, toggle_item_availability
)
from assets.styles import (
    COLORS, primary_button, outline_button,
    table_stylesheet, configure_table
)


class MenuItemDialog(QDialog):
    def __init__(self, parent=None, item=None, categories=None):
        super().__init__(parent)
        self.item = item
        self.categories = categories or []
        self.setWindowTitle("Edit Item" if item else "Add New Item")
        self.setFixedSize(460, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
            }}
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
                font-family: Segoe UI;
                background: transparent;
            }}
            QLineEdit, QComboBox {{
                background-color: {COLORS['bg_tertiary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-family: Segoe UI;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1.5px solid {COLORS['accent']};
                background-color: white;
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        # Header
        title = QLabel("Edit Menu Item" if self.item else "Add New Menu Item")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")

        subtitle = QLabel("Fill in the details below")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Grilled Chicken")
        self.name_input.setFixedHeight(40)

        self.category_combo = QComboBox()
        self.category_combo.setFixedHeight(40)
        for cat in self.categories:
            self.category_combo.addItem(cat[1], cat[0])

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("e.g. 15.00")
        self.price_input.setFixedHeight(40)

        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("e.g. 6.00  (optional)")
        self.cost_input.setFixedHeight(40)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Short description  (optional)")
        self.desc_input.setFixedHeight(40)

        for label_text, widget in [
            ("Item Name *",     self.name_input),
            ("Category *",      self.category_combo),
            ("Selling Price *", self.price_input),
            ("Cost Price",      self.cost_input),
            ("Description",     self.desc_input),
        ]:
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
            form.addRow(lbl, widget)

        if self.item:
            self.name_input.setText(self.item[1])
            self.price_input.setText(str(self.item[3]))
            self.cost_input.setText(str(self.item[4]) if self.item[4] else "")
            self.desc_input.setText(self.item[5] if self.item[5] else "")
            for i in range(self.category_combo.count()):
                if self.category_combo.itemText(i) == self.item[2]:
                    self.category_combo.setCurrentIndex(i)
                    break

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
                color: {COLORS['text_primary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Item")
        save_btn.setFixedHeight(42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(primary_button())
        save_btn.clicked.connect(self.save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(div)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(btn_row)

    def save(self):
        name      = self.name_input.text().strip()
        cat_id    = self.category_combo.currentData()
        price_str = self.price_input.text().strip()
        cost_str  = self.cost_input.text().strip()
        desc      = self.desc_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation", "Item name is required.")
            return
        try:
            price = float(price_str)
        except ValueError:
            QMessageBox.warning(self, "Validation", "Please enter a valid price.")
            return
        try:
            cost = float(cost_str) if cost_str else None
        except ValueError:
            QMessageBox.warning(self, "Validation", "Invalid cost price.")
            return

        self.result_data = {
            "category_id": cat_id,
            "item_name":   name,
            "description": desc,
            "price":       price,
            "cost_price":  cost,
        }
        self.accept()


class MenuManagementWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user       = user
        self.menu_items = []
        self.categories = []
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Page header ───────────────────────────────────────
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        page_icon = QLabel("🍽")
        page_icon.setFont(QFont("Segoe UI", 22))
        page_icon.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")

        page_title = QLabel("Menu Management")
        page_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        page_title.setStyleSheet(f"color: {COLORS['text_primary']};")

        page_sub = QLabel("Add, edit, and manage your restaurant menu items")
        page_sub.setFont(QFont("Segoe UI", 11))
        page_sub.setStyleSheet(f"color: {COLORS['text_secondary']};")

        icon_title = QHBoxLayout()
        icon_title.setSpacing(10)
        icon_title.addWidget(page_icon)
        icon_title.addWidget(page_title)
        icon_title.addStretch()

        title_col.addLayout(icon_title)
        title_col.addWidget(page_sub)

        add_btn = QPushButton("⊕  Add Menu Item")
        add_btn.setFixedHeight(40)
        add_btn.setFixedWidth(160)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(primary_button())
        add_btn.clicked.connect(self.add_item)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(100)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(outline_button())
        refresh_btn.clicked.connect(self.load_data)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(refresh_btn)
        header_row.addWidget(add_btn)

        # ── Stat pills ────────────────────────────────────────
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)

        # ── Toolbar: export + search ──────────────────────────
        toolbar = QFrame()
        toolbar.setFixedHeight(54)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 0, 16, 0)
        toolbar_layout.setSpacing(8)

        # Export buttons like sample
        for label, callback in [
            ("CSV", self.export_csv),
            ("XLS", self.export_csv),
            ("PDF", self.print_data),
            ("Print", self.print_data),
        ]:
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
            btn.clicked.connect(callback)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()

        # Search
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
        search_layout.setSpacing(6)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("background: transparent; border: none; font-size: 12px;")

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
        self.search_input.textChanged.connect(self.filter_table)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)

        toolbar_layout.addWidget(search_frame)

        # ── Table ─────────────────────────────────────────────
        table_wrapper = QFrame()
        table_wrapper.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 12px;
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

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Code", "Item Name", "Category",
            "Price", "Cost", "Status", "Actions"
        ])
        self.table.setStyleSheet(
            table_stylesheet(
                item_padding="0 12px",
                header_padding="14px 16px",
                header_font_size="12px"
            )
        )
        self.table.setColumnWidth(0, 90)   # Code
        self.table.setColumnWidth(2, 180)  # Category
        self.table.setColumnWidth(3, 120)  # Price
        self.table.setColumnWidth(4, 120)  # Cost
        self.table.setColumnWidth(5, 170)  # Status
        self.table.setColumnWidth(6, 110)  # Actions
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Fixed
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        configure_table(self.table, row_height=58)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        header = self.table.horizontalHeader()

        header.setStretchLastSection(False)

        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )  # Code

        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )  # Item Name

        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )  # Category

        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Fixed
        )  # Price

        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.Fixed
        )  # Cost

        header.setSectionResizeMode(
            5, QHeaderView.ResizeMode.Fixed
        )  # Status

        header.setSectionResizeMode(
            6, QHeaderView.ResizeMode.Fixed
        )  # Actions

        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )
        self.table.horizontalHeaderItem(1).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )

        table_layout.addWidget(self.table)

        layout.addLayout(header_row)
        layout.addLayout(self.stats_row)
        layout.addWidget(toolbar)
        layout.addWidget(table_wrapper)

    def build_stat_pill(self, label, value, color, bg):
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
        dot.setStyleSheet(f"color: {color}; background: transparent; border: none;")

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

    def load_data(self):
        self.categories = get_all_categories()
        self.menu_items = get_all_menu_items()

        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total     = len(self.menu_items)
        available = sum(1 for i in self.menu_items if i[6])
        unavail   = total - available

        for label, value, color, bg in [
            ("Total Items",  total,     COLORS['blue'],    COLORS['blue_light']),
            ("Available",    available, COLORS['accent'],  COLORS['accent_light']),
            ("Unavailable",  unavail,   COLORS['danger'],  COLORS['danger_light']),
            ("Categories",   len(self.categories), COLORS['purple'], COLORS['purple_light']),
        ]:
            pill = self.build_stat_pill(label, value, color, bg)
            self.stats_row.addWidget(pill)
        self.stats_row.addStretch()

        self.populate_table(self.menu_items)

    def populate_table(self, items):
        self.table.setRowCount(0)
        self.table.setRowCount(len(items))

        for row_idx, item in enumerate(items):
            self.table.setRowHeight(row_idx, 58)

            # Code
            id_item = QTableWidgetItem(str(item[0]))
            id_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            id_item.setForeground(QColor("#9ca3af"))
            id_item.setFont(QFont("Segoe UI", 12))
            self.table.setItem(row_idx, 0, id_item)

            # Item Name — semi bold not extra bold
            name_item = QTableWidgetItem(item[1])
            name_item.setFont(
                QFont("Segoe UI", 13, QFont.Weight.DemiBold)
            )
            name_item.setForeground(QColor(COLORS['accent']))
            name_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft |
                Qt.AlignmentFlag.AlignVCenter
            )

            self.table.setItem(row_idx, 1, name_item)

            # Category — center aligned to match header
            cat_item = QTableWidgetItem(item[2])
            cat_item.setFont(QFont("Segoe UI", 12))
            cat_item.setForeground(QColor("#6b7280"))
            cat_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            self.table.setItem(row_idx, 2, cat_item)

            # Price — right aligned, bold
            price_item = QTableWidgetItem(f"${item[3]:.2f}")
            price_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            price_item.setFont(
                QFont("Segoe UI", 13, QFont.Weight.Bold)
            )
            price_item.setForeground(
                QColor(COLORS['text_primary'])
            )
            self.table.setItem(row_idx, 3, price_item)

            # Cost — right aligned, normal weight
            cost_val  = f"${item[4]:.2f}" if item[4] else "—"
            cost_item = QTableWidgetItem(cost_val)
            cost_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            cost_item.setFont(QFont("Segoe UI", 12))
            cost_item.setForeground(QColor("#9ca3af"))
            self.table.setItem(row_idx, 4, cost_item)

            # Status badge
            badge_widget = QWidget()
            badge_widget.setStyleSheet("background: transparent;")
            badge_layout = QHBoxLayout(badge_widget)
            badge_layout.setContentsMargins(6, 0, 6, 0)
            badge_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            badge = QLabel(
                "Active" if item[6] else "Inactive"
            )
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedHeight(24)
            badge.setFont(
                QFont("Segoe UI", 11, QFont.Weight.DemiBold)
            )
            badge.setStyleSheet(f"""
                color: {'#15803d' if item[6] else '#dc2626'};
                background-color: {'#dcfce7' if item[6] else '#fee2e2'};
                border-radius: 10px;
                padding: 0 12px;
                border: none;
            """)
            badge_layout.addWidget(badge)
            self.table.setCellWidget(
                row_idx, 5, badge_widget
            )

            # Action button — compact
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
            dots_btn.setFixedSize(28, 28)
            dots_btn.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
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
                lambda _, i=item:
                self.show_action_menu(i)
            )
            action_layout.addWidget(dots_btn)
            self.table.setCellWidget(
                row_idx, 6, action_widget
            )

    def show_action_menu(self, item, button=None):
        """Show dropdown action menu like sample 1."""
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
                color: {COLORS['text_primary']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {COLORS['border']};
                margin: 4px 8px;
            }}
        """)

        edit_action   = menu.addAction("✏️   Edit Item")
        toggle_label  = "🔴   Disable Item" if item[6] else "🟢   Enable Item"
        toggle_action = menu.addAction(toggle_label)
        menu.addSeparator()
        delete_action = menu.addAction("🗑️   Delete Item")

        # Style delete red
        delete_action.setData("delete")

        action = menu.exec(QCursor.pos())

        if action == edit_action:
            self.edit_item(item)
        elif action == toggle_action:
            self.toggle_item(item[0], item[6])
        elif action == delete_action:
            self.delete_item(item[0])

    def filter_table(self, text):
        filtered = [
            item for item in self.menu_items
            if text.lower() in item[1].lower()
            or text.lower() in item[2].lower()
        ]
        self.populate_table(filtered)

    def add_item(self):
        dialog = MenuItemDialog(self, categories=self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d = dialog.result_data
            success = add_menu_item(
                d["category_id"], d["item_name"],
                d["description"], d["price"], d["cost_price"]
            )
            if success:
                QMessageBox.information(
                    self, "Success", "Menu item added successfully."
                )
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to add menu item.")

    def edit_item(self, item):
        dialog = MenuItemDialog(
            self, item=item, categories=self.categories
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            d = dialog.result_data
            success = update_menu_item(
                item[0], d["category_id"], d["item_name"],
                d["description"], d["price"], d["cost_price"]
            )
            if success:
                QMessageBox.information(
                    self, "Success", "Item updated successfully."
                )
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to update item.")

    def toggle_item(self, item_id, current_status):
        success = toggle_item_availability(item_id, current_status)
        if success:
            self.load_data()
        else:
            QMessageBox.critical(
                self, "Error", "Failed to update item status."
            )

    def delete_item(self, item_id):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this item?\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = delete_menu_item(item_id)
            if success:
                QMessageBox.information(
                    self, "Deleted", "Item deleted successfully."
                )
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to delete item."
                )

    def export_csv(self):
        import csv
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getSaveFileName(
            self, "Export Menu Items",
            "menu_items.csv",
            "CSV Files (*.csv)"
        )[0]
        if not path:
            return
        try:
            with open(path, "w", newline="",
                      encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Item Name", "Category",
                    "Price", "Cost Price",
                    "Description", "Status"
                ])
                for item in self.menu_items:
                    writer.writerow([
                        item[0], item[1], item[2],
                        f"${item[3]:.2f}",
                        f"${item[4]:.2f}" if item[4] else "",
                        item[5] or "",
                        "Active" if item[6] else "Inactive"
                    ])
            QMessageBox.information(
                self, "Exported",
                f"Menu items exported to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", str(e)
            )

    def print_data(self):
        import tempfile
        import subprocess
        try:
            tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=".txt",
                mode="w", encoding="utf-8"
            )
            tmp.write("MENU ITEMS\n")
            tmp.write("=" * 60 + "\n")
            tmp.write(
                f"{'ID':<5} {'Item Name':<20} {'Category':<12} "
                f"{'Price':<10} {'Status'}\n"
            )
            tmp.write("-" * 60 + "\n")
            for item in self.menu_items:
                tmp.write(
                    f"{item[0]:<5} {item[1]:<20} {item[2]:<12} "
                    f"${item[3]:<9.2f} "
                    f"{'Active' if item[6] else 'Inactive'}\n"
                )
            tmp.write("=" * 60 + "\n")
            tmp.write(f"Total Items: {len(self.menu_items)}\n")
            tmp.close()
            subprocess.run(
                ["notepad.exe", "/p", tmp.name], check=True
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Print Error", str(e)
            )
