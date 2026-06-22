from database.connection import create_connection


def get_all_suppliers():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                s.supplier_id,
                s.supplier_name,
                s.contact_name,
                s.phone,
                s.email,
                s.address,
                s.is_active,
                s.created_at,
                COUNT(po.po_id)            AS total_orders,
                COALESCE(SUM(po.total_amount), 0) AS total_value
            FROM suppliers s
            LEFT JOIN purchase_orders po
                ON s.supplier_id = po.supplier_id
            GROUP BY
                s.supplier_id, s.supplier_name,
                s.contact_name, s.phone, s.email,
                s.address, s.is_active, s.created_at
            ORDER BY s.supplier_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching suppliers: {e}")
        return []
    finally:
        conn.close()


def add_supplier(name, contact_name, phone,
                 email, address):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO suppliers
                (supplier_name, contact_name,
                 phone, email, address)
            VALUES (?, ?, ?, ?, ?)
        """, (name, contact_name, phone, email, address))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding supplier: {e}")
        return False
    finally:
        conn.close()


def update_supplier(supplier_id, name, contact_name,
                    phone, email, address):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE suppliers
            SET supplier_name = ?,
                contact_name  = ?,
                phone         = ?,
                email         = ?,
                address       = ?
            WHERE supplier_id = ?
        """, (name, contact_name, phone,
              email, address, supplier_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating supplier: {e}")
        return False
    finally:
        conn.close()


def toggle_supplier_status(supplier_id, current_status):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        new_status = 0 if current_status else 1
        cursor.execute("""
            UPDATE suppliers
            SET is_active = ?
            WHERE supplier_id = ?
        """, (new_status, supplier_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error toggling supplier: {e}")
        return False
    finally:
        conn.close()


def get_purchase_orders(supplier_id=None):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        if supplier_id:
            cursor.execute("""
                SELECT
                    po.po_id,
                    s.supplier_name,
                    po.status,
                    po.total_amount,
                    po.expected_date,
                    po.received_date,
                    po.notes,
                    po.created_at,
                    u.full_name AS created_by
                FROM purchase_orders po
                JOIN suppliers s
                    ON po.supplier_id = s.supplier_id
                JOIN users u
                    ON po.created_by = u.user_id
                WHERE po.supplier_id = ?
                ORDER BY po.created_at DESC
            """, (supplier_id,))
        else:
            cursor.execute("""
                SELECT
                    po.po_id,
                    s.supplier_name,
                    po.status,
                    po.total_amount,
                    po.expected_date,
                    po.received_date,
                    po.notes,
                    po.created_at,
                    u.full_name AS created_by
                FROM purchase_orders po
                JOIN suppliers s
                    ON po.supplier_id = s.supplier_id
                JOIN users u
                    ON po.created_by = u.user_id
                ORDER BY po.created_at DESC
            """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching purchase orders: {e}")
        return []
    finally:
        conn.close()


def get_po_items(po_id):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                poi.po_item_id,
                i.name,
                i.unit,
                poi.quantity,
                poi.unit_cost,
                poi.subtotal,
                poi.received_qty
            FROM purchase_order_items poi
            JOIN ingredients i
                ON poi.ingredient_id = i.ingredient_id
            WHERE poi.po_id = ?
        """, (po_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching PO items: {e}")
        return []
    finally:
        conn.close()


def create_purchase_order(supplier_id, user_id,
                          items, notes, expected_date):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        total = sum(
            item['quantity'] * item['unit_cost']
            for item in items
        )
        cursor.execute("""
            INSERT INTO purchase_orders
                (supplier_id, created_by, total_amount,
                 notes, expected_date)
            VALUES (?, ?, ?, ?, ?)
        """, (supplier_id, user_id, total,
              notes, expected_date))
        cursor.execute("SELECT @@IDENTITY")
        po_id = int(cursor.fetchone()[0])

        for item in items:
            subtotal = item['quantity'] * item['unit_cost']
            cursor.execute("""
                INSERT INTO purchase_order_items
                    (po_id, ingredient_id, quantity,
                     unit_cost, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (po_id, item['ingredient_id'],
                  item['quantity'], item['unit_cost'],
                  subtotal))
        conn.commit()
        return po_id
    except Exception as e:
        print(f"Error creating PO: {e}")
        return None
    finally:
        conn.close()


def receive_purchase_order(po_id, user_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                poi.ingredient_id,
                poi.quantity,
                poi.unit_cost
            FROM purchase_order_items poi
            WHERE poi.po_id = ?
        """, (po_id,))
        items = cursor.fetchall()

        for item in items:
            cursor.execute("""
                UPDATE ingredients
                SET current_stock = current_stock + ?,
                    unit_cost     = ?,
                    updated_at    = GETDATE()
                WHERE ingredient_id = ?
            """, (item[1], item[2], item[0]))
            cursor.execute("""
                INSERT INTO inventory_transactions
                    (ingredient_id, transaction_type,
                     quantity, unit_cost,
                     reference_no, performed_by)
                VALUES (?, 'Stock In', ?, ?, ?, ?)
            """, (item[0], item[1], item[2],
                  f"PO #{po_id}", user_id))
            cursor.execute("""
                UPDATE purchase_order_items
                SET received_qty = quantity
                WHERE po_id = ?
                AND ingredient_id = ?
            """, (po_id, item[0]))

        cursor.execute("""
            UPDATE purchase_orders
            SET status        = 'Received',
                received_date = GETDATE()
            WHERE po_id = ?
        """, (po_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error receiving PO: {e}")
        return False
    finally:
        conn.close()


def cancel_purchase_order(po_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE purchase_orders
            SET status = 'Cancelled'
            WHERE po_id = ?
        """, (po_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error cancelling PO: {e}")
        return False
    finally:
        conn.close()


def get_supplier_stats():
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(DISTINCT s.supplier_id) AS total,
                COUNT(DISTINCT CASE
                    WHEN s.is_active = 1
                    THEN s.supplier_id END)   AS active,
                COUNT(po.po_id)               AS total_orders,
                COALESCE(SUM(po.total_amount), 0) AS total_value
            FROM suppliers s
            LEFT JOIN purchase_orders po
                ON s.supplier_id = po.supplier_id
        """)
        row = cursor.fetchone()
        return {
            "total":        row[0] or 0,
            "active":       row[1] or 0,
            "total_orders": row[2] or 0,
            "total_value":  float(row[3] or 0),
        }
    except Exception as e:
        print(f"Error fetching supplier stats: {e}")
        return {}
    finally:
        conn.close()