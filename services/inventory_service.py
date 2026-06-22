from database.connection import create_connection


def get_all_ingredients():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT i.ingredient_id, i.name, i.unit, i.current_stock, "
            "i.minimum_stock, i.reorder_level, i.unit_cost, i.is_active, "
            "COALESCE(s.supplier_name, '--') AS supplier_name, "
            "CASE WHEN i.current_stock <= 0 THEN 'Out of Stock' "
            "WHEN i.current_stock <= i.minimum_stock THEN 'Low Stock' "
            "WHEN i.current_stock <= i.reorder_level THEN 'Reorder Soon' "
            "ELSE 'In Stock' END AS stock_status "
            "FROM ingredients i "
            "LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id "
            "WHERE i.is_active = 1 ORDER BY i.name"
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching ingredients: {e}")
        return []
    finally:
        conn.close()

def get_all_suppliers():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT supplier_id, supplier_name,
                   contact_name, phone, email
            FROM suppliers
            WHERE is_active = 1
            ORDER BY supplier_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching suppliers: {e}")
        return []
    finally:
        conn.close()


def add_ingredient(name, unit, minimum_stock,
                   reorder_level, unit_cost, supplier_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ingredients
                (name, unit, minimum_stock,
                 reorder_level, unit_cost, supplier_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, unit, minimum_stock,
              reorder_level, unit_cost, supplier_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding ingredient: {e}")
        return False
    finally:
        conn.close()


def update_ingredient(ingredient_id, name, unit,
                      minimum_stock, reorder_level,
                      unit_cost, supplier_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ingredients
            SET name          = ?,
                unit          = ?,
                minimum_stock = ?,
                reorder_level = ?,
                unit_cost     = ?,
                supplier_id   = ?,
                updated_at    = GETDATE()
            WHERE ingredient_id = ?
        """, (name, unit, minimum_stock, reorder_level,
              unit_cost, supplier_id, ingredient_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating ingredient: {e}")
        return False
    finally:
        conn.close()


def stock_in(ingredient_id, quantity, unit_cost,
             reference_no, notes, user_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ingredients
            SET current_stock = current_stock + ?,
                unit_cost     = ?,
                updated_at    = GETDATE()
            WHERE ingredient_id = ?
        """, (quantity, unit_cost, ingredient_id))
        cursor.execute("""
            INSERT INTO inventory_transactions
                (ingredient_id, transaction_type, quantity,
                 unit_cost, reference_no, notes, performed_by)
            VALUES (?, 'Stock In', ?, ?, ?, ?, ?)
        """, (ingredient_id, quantity, unit_cost,
              reference_no, notes, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error stocking in: {e}")
        return False
    finally:
        conn.close()


def stock_out(ingredient_id, quantity, notes, user_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ingredients
            SET current_stock = current_stock - ?,
                updated_at    = GETDATE()
            WHERE ingredient_id = ?
        """, (quantity, ingredient_id))
        cursor.execute("""
            INSERT INTO inventory_transactions
                (ingredient_id, transaction_type,
                 quantity, notes, performed_by)
            VALUES (?, 'Stock Out', ?, ?, ?)
        """, (ingredient_id, quantity, notes, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error stocking out: {e}")
        return False
    finally:
        conn.close()


def adjust_stock(ingredient_id, new_quantity,
                 notes, user_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT current_stock
            FROM ingredients
            WHERE ingredient_id = ?
        """, (ingredient_id,))
        row = cursor.fetchone()
        if not row:
            return False
        old_qty    = row[0]
        difference = new_quantity - old_qty
        cursor.execute("""
            UPDATE ingredients
            SET current_stock = ?,
                updated_at    = GETDATE()
            WHERE ingredient_id = ?
        """, (new_quantity, ingredient_id))
        cursor.execute("""
            INSERT INTO inventory_transactions
                (ingredient_id, transaction_type,
                 quantity, notes, performed_by)
            VALUES (?, 'Adjustment', ?, ?, ?)
        """, (ingredient_id, difference, notes, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adjusting stock: {e}")
        return False
    finally:
        conn.close()


def get_transactions(ingredient_id=None, limit=50):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        if ingredient_id:
            cursor.execute(
                "SELECT TOP (?) "
                "t.transaction_id, i.name, t.transaction_type, "
                "t.quantity, i.unit, t.unit_cost, t.reference_no, "
                "t.notes, u.full_name, t.created_at "
                "FROM inventory_transactions t "
                "JOIN ingredients i ON t.ingredient_id = i.ingredient_id "
                "JOIN users u ON t.performed_by = u.user_id "
                "WHERE t.ingredient_id = ? "
                "ORDER BY t.created_at DESC",
                (limit, ingredient_id)
            )
        else:
            cursor.execute(
                "SELECT TOP (?) "
                "t.transaction_id, i.name, t.transaction_type, "
                "t.quantity, i.unit, t.unit_cost, t.reference_no, "
                "t.notes, u.full_name, t.created_at "
                "FROM inventory_transactions t "
                "JOIN ingredients i ON t.ingredient_id = i.ingredient_id "
                "JOIN users u ON t.performed_by = u.user_id "
                "ORDER BY t.created_at DESC",
                (limit,)
            )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []
    finally:
        conn.close()


def get_inventory_stats():
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE
                    WHEN current_stock <= 0
                        THEN 1 ELSE 0 END) AS out_of_stock,
                SUM(CASE
                    WHEN current_stock > 0
                    AND current_stock <= minimum_stock
                        THEN 1 ELSE 0 END) AS low_stock,
                SUM(current_stock * unit_cost) AS total_value
            FROM ingredients
            WHERE is_active = 1
        """)
        row = cursor.fetchone()
        return {
            "total":         row[0] or 0,
            "out_of_stock":  row[1] or 0,
            "low_stock":     row[2] or 0,
            "total_value":   row[3] or 0.0,
        }
    except Exception as e:
        print(f"Error fetching inventory stats: {e}")
        return {}
    finally:
        conn.close()


def delete_ingredient(ingredient_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ingredients
            SET is_active = 0
            WHERE ingredient_id = ?
        """, (ingredient_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting ingredient: {e}")
        return False
    finally:
        conn.close()