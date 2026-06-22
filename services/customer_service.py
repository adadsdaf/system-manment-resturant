from database.connection import create_connection


def get_all_customers():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                c.customer_id,
                c.full_name,
                c.phone,
                c.email,
                c.address,
                c.date_of_birth,
                c.is_active,
                c.created_at,
                COALESCE(la.points_balance, 0) AS points,
                COALESCE(la.total_earned, 0)   AS total_earned,
                COUNT(o.order_id)              AS total_orders,
                COALESCE(SUM(o.total_amount), 0) AS total_spent
            FROM customers c
            LEFT JOIN loyalty_accounts la
                ON c.customer_id = la.customer_id
            LEFT JOIN orders o
                ON c.customer_id = o.customer_id
            GROUP BY
                c.customer_id, c.full_name, c.phone,
                c.email, c.address, c.date_of_birth,
                c.is_active, c.created_at,
                la.points_balance, la.total_earned
            ORDER BY c.full_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return []
    finally:
        conn.close()


def get_customer_by_phone(phone):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                c.customer_id,
                c.full_name,
                c.phone,
                c.email,
                COALESCE(la.points_balance, 0) AS points
            FROM customers c
            LEFT JOIN loyalty_accounts la
                ON c.customer_id = la.customer_id
            WHERE c.phone = ?
        """, (phone,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching customer: {e}")
        return None
    finally:
        conn.close()


def add_customer(full_name, phone, email,
                 address, date_of_birth):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers
                (full_name, phone, email,
                 address, date_of_birth)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, phone, email,
              address, date_of_birth or None))
        cursor.execute("SELECT @@IDENTITY")
        customer_id = int(cursor.fetchone()[0])

        # Create loyalty account
        cursor.execute("""
            INSERT INTO loyalty_accounts (customer_id)
            VALUES (?)
        """, (customer_id,))
        conn.commit()
        return customer_id
    except Exception as e:
        print(f"Error adding customer: {e}")
        return None
    finally:
        conn.close()


def update_customer(customer_id, full_name, phone,
                    email, address, date_of_birth):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers
            SET full_name     = ?,
                phone         = ?,
                email         = ?,
                address       = ?,
                date_of_birth = ?
            WHERE customer_id = ?
        """, (full_name, phone, email, address,
              date_of_birth or None, customer_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating customer: {e}")
        return False
    finally:
        conn.close()


def toggle_customer_status(customer_id, current_status):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers
            SET is_active = ?
            WHERE customer_id = ?
        """, (0 if current_status else 1, customer_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error toggling customer: {e}")
        return False
    finally:
        conn.close()


def get_customer_orders(customer_id):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                o.order_id,
                o.total_amount,
                o.payment_method,
                o.order_status,
                o.created_at
            FROM orders o
            WHERE o.customer_id = ?
            ORDER BY o.created_at DESC
        """, (customer_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching customer orders: {e}")
        return []
    finally:
        conn.close()


def get_loyalty_transactions(customer_id):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                lt.lt_id,
                lt.transaction_type,
                lt.points,
                lt.reference,
                lt.notes,
                lt.created_at
            FROM loyalty_transactions lt
            JOIN loyalty_accounts la
                ON lt.loyalty_id = la.loyalty_id
            WHERE la.customer_id = ?
            ORDER BY lt.created_at DESC
        """, (customer_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching loyalty transactions: {e}")
        return []
    finally:
        conn.close()


def add_loyalty_points(customer_id, points,
                       reference, notes):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT loyalty_id
            FROM loyalty_accounts
            WHERE customer_id = ?
        """, (customer_id,))
        row = cursor.fetchone()
        if not row:
            return False
        loyalty_id = row[0]

        cursor.execute("""
            UPDATE loyalty_accounts
            SET points_balance = points_balance + ?,
                total_earned   = total_earned + ?
            WHERE loyalty_id = ?
        """, (points, points, loyalty_id))
        cursor.execute("""
            INSERT INTO loyalty_transactions
                (loyalty_id, transaction_type,
                 points, reference, notes)
            VALUES (?, 'Earned', ?, ?, ?)
        """, (loyalty_id, points, reference, notes))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding points: {e}")
        return False
    finally:
        conn.close()


def redeem_loyalty_points(customer_id, points, notes):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT loyalty_id, points_balance
            FROM loyalty_accounts
            WHERE customer_id = ?
        """, (customer_id,))
        row = cursor.fetchone()
        if not row:
            return False
        loyalty_id, balance = row[0], row[1]

        if balance < points:
            return False

        cursor.execute("""
            UPDATE loyalty_accounts
            SET points_balance = points_balance - ?,
                total_redeemed = total_redeemed + ?
            WHERE loyalty_id = ?
        """, (points, points, loyalty_id))
        cursor.execute("""
            INSERT INTO loyalty_transactions
                (loyalty_id, transaction_type,
                 points, notes)
            VALUES (?, 'Redeemed', ?, ?)
        """, (loyalty_id, points, notes))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error redeeming points: {e}")
        return False
    finally:
        conn.close()


def get_customer_stats():
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*)                          AS total,
                SUM(CASE WHEN is_active = 1
                    THEN 1 ELSE 0 END)            AS active,
                SUM(CASE WHEN date_of_birth IS NOT NULL
                    AND MONTH(date_of_birth) = MONTH(GETDATE())
                    AND DAY(date_of_birth)   = DAY(GETDATE())
                    THEN 1 ELSE 0 END)            AS birthdays_today
            FROM customers
        """)
        row = cursor.fetchone()

        cursor.execute("""
            SELECT COALESCE(SUM(points_balance), 0)
            FROM loyalty_accounts
        """)
        total_points = cursor.fetchone()[0] or 0

        return {
            "total":           row[0] or 0,
            "active":          row[1] or 0,
            "birthdays_today": row[2] or 0,
            "total_points":    int(total_points),
        }
    except Exception as e:
        print(f"Error fetching customer stats: {e}")
        return {}
    finally:
        conn.close()