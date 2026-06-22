from database.connection import create_connection


def get_all_categories():
    """Fetch all menu categories."""
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category_id, category_name, description, is_active
            FROM menu_categories
            ORDER BY category_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []
    finally:
        conn.close()


def get_all_menu_items():
    """Fetch all menu items with category names."""
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
                mi.cost_price,
                mi.description,
                mi.is_available
            FROM menu_items mi
            JOIN menu_categories mc ON mi.category_id = mc.category_id
            ORDER BY mc.category_name, mi.item_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching menu items: {e}")
        return []
    finally:
        conn.close()


def add_menu_item(category_id, item_name, description, price, cost_price):
    """Add a new menu item."""
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO menu_items
                (category_id, item_name, description, price, cost_price)
            VALUES (?, ?, ?, ?, ?)
        """, (category_id, item_name, description, price, cost_price))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding menu item: {e}")
        return False
    finally:
        conn.close()


def update_menu_item(item_id, category_id, item_name, description, price, cost_price):
    """Update an existing menu item."""
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE menu_items
            SET category_id = ?,
                item_name   = ?,
                description = ?,
                price       = ?,
                cost_price  = ?,
                updated_at  = GETDATE()
            WHERE item_id = ?
        """, (category_id, item_name, description, price, cost_price, item_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating menu item: {e}")
        return False
    finally:
        conn.close()


def delete_menu_item(item_id):
    """Delete a menu item."""
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu_items WHERE item_id = ?", (item_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting menu item: {e}")
        return False
    finally:
        conn.close()


def toggle_item_availability(item_id, current_status):
    """Toggle a menu item between available and unavailable."""
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        new_status = 0 if current_status else 1
        cursor.execute("""
            UPDATE menu_items
            SET is_available = ?, updated_at = GETDATE()
            WHERE item_id = ?
        """, (new_status, item_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error toggling item availability: {e}")
        return False
    finally:
        conn.close()


def get_dashboard_stats():
    """Fetch summary statistics for the dashboard."""
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        today = __import__('datetime').date.today().strftime("%Y-%m-%d")

        # Total sales today
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0)
            FROM orders
            WHERE CAST(created_at AS DATE) = ?
        """, (today,))
        sales_today = cursor.fetchone()[0]

        # Orders today
        cursor.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE CAST(created_at AS DATE) = ?
        """, (today,))
        orders_today = cursor.fetchone()[0]

        # Total menu items
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE is_available = 1")
        active_items = cursor.fetchone()[0]

        # Total categories
        cursor.execute("SELECT COUNT(*) FROM menu_categories WHERE is_active = 1")
        active_categories = cursor.fetchone()[0]

        return {
            "sales_today":       sales_today,
            "orders_today":      orders_today,
            "active_items":      active_items,
            "active_categories": active_categories
        }
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return {
            "sales_today":       0,
            "orders_today":      0,
            "active_items":      0,
            "active_categories": 0
        }
    finally:
        conn.close()