from database.connection import create_connection


def get_all_tables():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                t.table_id,
                t.table_number,
                t.capacity,
                t.location,
                t.status,
                t.is_active,
                ts.session_id,
                ts.customer_name,
                ts.guests,
                ts.opened_at
            FROM restaurant_tables t
            LEFT JOIN table_sessions ts
                ON t.table_id = ts.table_id
                AND ts.status = 'Open'
            WHERE t.is_active = 1
            ORDER BY t.location, t.table_number
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []
    finally:
        conn.close()


def get_locations():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT location
            FROM restaurant_tables
            WHERE is_active = 1
            ORDER BY location
        """)
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching locations: {e}")
        return []
    finally:
        conn.close()


def open_table_session(table_id, user_id,
                       customer_name=None, guests=1):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO table_sessions
                (table_id, customer_name, guests, opened_by)
            VALUES (?, ?, ?, ?)
        """, (table_id, customer_name, guests, user_id))
        cursor.execute("""
            UPDATE restaurant_tables
            SET status = 'Occupied'
            WHERE table_id = ?
        """, (table_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error opening session: {e}")
        return False
    finally:
        conn.close()


def close_table_session(table_id, session_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE table_sessions
            SET status = 'Closed', closed_at = GETDATE()
            WHERE session_id = ?
        """, (session_id,))
        cursor.execute("""
            UPDATE restaurant_tables
            SET status = 'Available'
            WHERE table_id = ?
        """, (table_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error closing session: {e}")
        return False
    finally:
        conn.close()


def reserve_table(table_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE restaurant_tables
            SET status = 'Reserved'
            WHERE table_id = ?
        """, (table_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error reserving table: {e}")
        return False
    finally:
        conn.close()


def transfer_table(from_table_id, to_table_id, session_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE table_sessions
            SET table_id = ?
            WHERE session_id = ?
        """, (to_table_id, session_id))
        cursor.execute("""
            UPDATE restaurant_tables
            SET status = 'Available'
            WHERE table_id = ?
        """, (from_table_id,))
        cursor.execute("""
            UPDATE restaurant_tables
            SET status = 'Occupied'
            WHERE table_id = ?
        """, (to_table_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error transferring table: {e}")
        return False
    finally:
        conn.close()


def add_table(table_number, capacity, location):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO restaurant_tables
                (table_number, capacity, location)
            VALUES (?, ?, ?)
        """, (table_number, capacity, location))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding table: {e}")
        return False
    finally:
        conn.close()


def update_table(table_id, table_number, capacity, location):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE restaurant_tables
            SET table_number = ?,
                capacity     = ?,
                location     = ?
            WHERE table_id = ?
        """, (table_number, capacity, location, table_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating table: {e}")
        return False
    finally:
        conn.close()


def delete_table(table_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE restaurant_tables
            SET is_active = 0
            WHERE table_id = ?
        """, (table_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting table: {e}")
        return False
    finally:
        conn.close()


def get_table_stats():
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available,
                SUM(CASE WHEN status = 'Occupied'  THEN 1 ELSE 0 END) AS occupied,
                SUM(CASE WHEN status = 'Reserved'  THEN 1 ELSE 0 END) AS reserved
            FROM restaurant_tables
            WHERE is_active = 1
        """)
        row = cursor.fetchone()
        return {
            "total":     row[0] or 0,
            "available": row[1] or 0,
            "occupied":  row[2] or 0,
            "reserved":  row[3] or 0,
        }
    except Exception as e:
        print(f"Error fetching table stats: {e}")
        return {}
    finally:
        conn.close()