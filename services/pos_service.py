from database.connection import create_connection


def get_setting(key):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT [value] FROM settings WHERE [key] = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error getting setting: {e}")
        return None
    finally:
        conn.close()


def get_available_menu_items():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                mi.item_id,
                mi.item_name,
                mc.category_name,
                mi.price,
                mi.description
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            WHERE mi.is_available = 1
            ORDER BY mc.category_name, mi.item_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching menu items: {e}")
        return []
    finally:
        conn.close()


def get_categories_with_items():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT mc.category_name
            FROM menu_categories mc
            JOIN menu_items mi ON mc.category_id = mi.category_id
            WHERE mi.is_available = 1
            ORDER BY mc.category_name
        """)
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []
    finally:
        conn.close()


def save_order(user_id, customer_name, cart, discount_pct,
               payment_method, reference_no=None):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()

        # Get tax rate
        tax_rate    = float(get_setting('tax_rate') or 0)
        tax_enabled = get_setting('tax_enabled') == '1'

        # Calculate totals
        subtotal = sum(
            item['price'] * item['quantity'] for item in cart
        )
        discount_amount = round(subtotal * (discount_pct / 100), 2)
        taxable         = subtotal - discount_amount
        tax_amount      = round(taxable * (tax_rate / 100), 2) if tax_enabled else 0
        total_amount    = round(taxable + tax_amount, 2)

        # Insert order
        cursor.execute("""
            INSERT INTO orders (
                customer_name, served_by, subtotal,
                discount_amount, tax_amount, total_amount,
                payment_method, payment_status, order_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Paid', 'Completed')
        """, (
            customer_name or "Guest",
            user_id, subtotal, discount_amount,
            tax_amount, total_amount, payment_method
        ))

        cursor.execute("SELECT @@IDENTITY")
        order_id = int(cursor.fetchone()[0])

        # Insert order items
        for item in cart:
            item_subtotal = item['price'] * item['quantity']
            cursor.execute("""
                INSERT INTO order_items (
                    order_id, menu_item_id, item_name,
                    quantity, unit_price, subtotal
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_id, item['item_id'], item['name'],
                item['quantity'], item['price'], item_subtotal
            ))

        # Insert payment
        cursor.execute("""
            INSERT INTO payments (
                order_id, amount_paid, payment_method, reference_no
            )
            VALUES (?, ?, ?, ?)
        """, (order_id, total_amount, payment_method, reference_no))

        conn.commit()
        return {
            "order_id":        order_id,
            "subtotal":        subtotal,
            "discount_amount": discount_amount,
            "tax_amount":      tax_amount,
            "total_amount":    total_amount,
        }

    except Exception as e:
        print(f"Error saving order: {e}")
        return None
    finally:
        conn.close()


def get_recent_orders(limit=20):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP (?)
                o.order_id,
                o.customer_name,
                o.total_amount,
                o.payment_method,
                o.order_status,
                o.created_at,
                u.full_name AS served_by
            FROM orders o
            JOIN users u ON o.served_by = u.user_id
            ORDER BY o.created_at DESC
        """, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching recent orders: {e}")
        return []
    finally:
        conn.close()
def create_kitchen_order(order_id, cart,
                         table_number=None,
                         customer_name=None,
                         notes=None):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO kitchen_orders
                (order_id, table_number, customer_name, notes)
            VALUES (?, ?, ?, ?)
        """, (order_id, table_number, customer_name, notes))
        cursor.execute("SELECT @@IDENTITY")
        kitchen_order_id = int(cursor.fetchone()[0])

        for item in cart:
            cursor.execute("""
                INSERT INTO kitchen_order_items
                    (kitchen_order_id, item_name, quantity)
                VALUES (?, ?, ?)
            """, (kitchen_order_id, item['name'], item['quantity']))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating kitchen order: {e}")
        return False
    finally:
        conn.close()
def search_customer_by_phone(phone):
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
                COALESCE(la.points_balance, 0) AS points
            FROM customers c
            LEFT JOIN loyalty_accounts la
                ON c.customer_id = la.customer_id
            WHERE c.phone = ?
        """, (phone,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error searching customer: {e}")
        return None
    finally:
        conn.close()


def award_loyalty_points(customer_id, order_id,
                         total_amount, user_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()

        # Get points rate from settings
        cursor.execute("""
            SELECT [value] FROM settings
            WHERE [key] = 'loyalty_points_per_dollar'
        """)
        row   = cursor.fetchone()
        rate  = float(row[0]) if row else 1.0
        points = int(total_amount * rate)

        if points <= 0:
            return False

        # Get loyalty account
        cursor.execute("""
            SELECT loyalty_id
            FROM loyalty_accounts
            WHERE customer_id = ?
        """, (customer_id,))
        row = cursor.fetchone()
        if not row:
            return False
        loyalty_id = row[0]

        # Update points balance
        cursor.execute("""
            UPDATE loyalty_accounts
            SET points_balance = points_balance + ?,
                total_earned   = total_earned + ?
            WHERE loyalty_id = ?
        """, (points, points, loyalty_id))

        # Log transaction
        cursor.execute("""
            INSERT INTO loyalty_transactions
                (loyalty_id, transaction_type,
                 points, reference, notes)
            VALUES (?, 'Earned', ?, ?, ?)
        """, (loyalty_id, points,
              f"Order #{order_id}",
              f"Auto awarded from POS"))

        # Link order to customer
        cursor.execute("""
            UPDATE orders
            SET customer_id = ?
            WHERE order_id  = ?
        """, (customer_id, order_id))

        conn.commit()
        return points
    except Exception as e:
        print(f"Error awarding points: {e}")
        return False
    finally:
        conn.close()