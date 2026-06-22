from database.connection import create_connection


def get_kitchen_orders(status_filter=None):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        if status_filter and status_filter != "All":
            cursor.execute("""
                SELECT
                    ko.kitchen_order_id,
                    ko.order_id,
                    ko.table_number,
                    ko.customer_name,
                    ko.status,
                    ko.priority,
                    ko.notes,
                    ko.created_at,
                    ko.updated_at
                FROM kitchen_orders ko
                WHERE ko.status = ?
                ORDER BY
                    CASE ko.priority
                        WHEN 'High'   THEN 1
                        WHEN 'Normal' THEN 2
                        WHEN 'Low'    THEN 3
                    END,
                    ko.created_at ASC
            """, (status_filter,))
        else:
            cursor.execute("""
                SELECT
                    ko.kitchen_order_id,
                    ko.order_id,
                    ko.table_number,
                    ko.customer_name,
                    ko.status,
                    ko.priority,
                    ko.notes,
                    ko.created_at,
                    ko.updated_at
                FROM kitchen_orders ko
                WHERE ko.status != 'Served'
                ORDER BY
                    CASE ko.priority
                        WHEN 'High'   THEN 1
                        WHEN 'Normal' THEN 2
                        WHEN 'Low'    THEN 3
                    END,
                    ko.created_at ASC
            """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching kitchen orders: {e}")
        return []
    finally:
        conn.close()


def get_kitchen_order_items(kitchen_order_id):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                kitchen_item_id,
                item_name,
                quantity,
                notes,
                status
            FROM kitchen_order_items
            WHERE kitchen_order_id = ?
        """, (kitchen_order_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching kitchen items: {e}")
        return []
    finally:
        conn.close()


def update_kitchen_order_status(kitchen_order_id, new_status):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE kitchen_orders
            SET status     = ?,
                updated_at = GETDATE()
            WHERE kitchen_order_id = ?
        """, (new_status, kitchen_order_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating kitchen order: {e}")
        return False
    finally:
        conn.close()


def update_item_status(kitchen_item_id, new_status):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE kitchen_order_items
            SET status = ?
            WHERE kitchen_item_id = ?
        """, (new_status, kitchen_item_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating item status: {e}")
        return False
    finally:
        conn.close()


def update_priority(kitchen_order_id, priority):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE kitchen_orders
            SET priority   = ?,
                updated_at = GETDATE()
            WHERE kitchen_order_id = ?
        """, (priority, kitchen_order_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating priority: {e}")
        return False
    finally:
        conn.close()


def get_kitchen_stats():
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                SUM(CASE WHEN status = 'Pending'   THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'Preparing' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'Ready'     THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'Served'    THEN 1 ELSE 0 END),
                COUNT(*)
            FROM kitchen_orders
            WHERE CAST(created_at AS DATE) = CAST(GETDATE() AS DATE)
        """)
        row = cursor.fetchone()
        return {
            "pending":   row[0] or 0,
            "preparing": row[1] or 0,
            "ready":     row[2] or 0,
            "served":    row[3] or 0,
            "total":     row[4] or 0,
        }
    except Exception as e:
        print(f"Error fetching kitchen stats: {e}")
        return {}
    finally:
        conn.close()