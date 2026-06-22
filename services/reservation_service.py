from database.connection import create_connection
import datetime


def get_reservations(date_filter=None, status_filter=None):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        query = """
            SELECT
                r.reservation_id,
                r.customer_name,
                r.phone,
                r.guests,
                r.reservation_date,
                r.reservation_time,
                r.status,
                r.special_requests,
                COALESCE(t.table_number, '—') AS table_number,
                r.created_at,
                r.customer_id,
                r.table_id
            FROM reservations r
            LEFT JOIN restaurant_tables t
                ON r.table_id = t.table_id
            WHERE 1=1
        """
        params = []
        if date_filter:
            query += " AND r.reservation_date = ?"
            params.append(date_filter)
        if status_filter and status_filter != "All":
            query += " AND r.status = ?"
            params.append(status_filter)
        query += " ORDER BY r.reservation_date, r.reservation_time"
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching reservations: {e}")
        return []
    finally:
        conn.close()


def get_todays_reservations():
    today = datetime.date.today().strftime("%Y-%m-%d")
    return get_reservations(date_filter=today)


def add_reservation(customer_name, phone, customer_id,
                    table_id, guests, reservation_date,
                    reservation_time, special_requests,
                    user_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reservations (
                customer_name, phone, customer_id,
                table_id, guests, reservation_date,
                reservation_time, special_requests,
                created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer_name, phone, customer_id,
              table_id, guests, reservation_date,
              reservation_time, special_requests,
              user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding reservation: {e}")
        return False
    finally:
        conn.close()


def update_reservation(reservation_id, customer_name,
                       phone, table_id, guests,
                       reservation_date, reservation_time,
                       special_requests):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reservations
            SET customer_name     = ?,
                phone             = ?,
                table_id          = ?,
                guests            = ?,
                reservation_date  = ?,
                reservation_time  = ?,
                special_requests  = ?,
                updated_at        = GETDATE()
            WHERE reservation_id = ?
        """, (customer_name, phone, table_id, guests,
              reservation_date, reservation_time,
              special_requests, reservation_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating reservation: {e}")
        return False
    finally:
        conn.close()


def update_reservation_status(reservation_id, status):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reservations
            SET status     = ?,
                updated_at = GETDATE()
            WHERE reservation_id = ?
        """, (status, reservation_id))

        # If seated, mark table as occupied
        if status == "Seated":
            cursor.execute("""
                UPDATE restaurant_tables
                SET status = 'Occupied'
                WHERE table_id = (
                    SELECT table_id FROM reservations
                    WHERE reservation_id = ?
                )
            """, (reservation_id,))

        # If completed or cancelled, free the table
        if status in ("Completed", "Cancelled", "No Show"):
            cursor.execute("""
                UPDATE restaurant_tables
                SET status = 'Available'
                WHERE table_id = (
                    SELECT table_id FROM reservations
                    WHERE reservation_id = ?
                )
                AND status = 'Occupied'
            """, (reservation_id,))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating status: {e}")
        return False
    finally:
        conn.close()


def delete_reservation(reservation_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM reservations
            WHERE reservation_id = ?
        """, (reservation_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting reservation: {e}")
        return False
    finally:
        conn.close()


def get_reservation_stats():
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        today = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT
                COUNT(*) AS total_today,
                SUM(CASE WHEN status = 'Pending'
                    THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'Confirmed'
                    THEN 1 ELSE 0 END) AS confirmed,
                SUM(CASE WHEN status = 'Seated'
                    THEN 1 ELSE 0 END) AS seated,
                SUM(CASE WHEN status = 'Completed'
                    THEN 1 ELSE 0 END) AS completed,
                COALESCE(SUM(guests), 0) AS total_guests
            FROM reservations
            WHERE reservation_date = ?
        """, (today,))
        row = cursor.fetchone()
        return {
            "total_today":  row[0] or 0,
            "pending":      row[1] or 0,
            "confirmed":    row[2] or 0,
            "seated":       row[3] or 0,
            "completed":    row[4] or 0,
            "total_guests": row[5] or 0,
        }
    except Exception as e:
        print(f"Error fetching reservation stats: {e}")
        return {}
    finally:
        conn.close()