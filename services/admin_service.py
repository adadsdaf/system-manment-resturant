from database.connection import create_connection
import bcrypt


def get_all_users():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                u.user_id,
                u.username,
                u.full_name,
                u.email,
                u.is_active,
                u.last_login,
                u.created_at,
                r.role_name,
                r.role_id
            FROM users u
            LEFT JOIN roles r
                ON u.role_id = r.role_id
            ORDER BY u.full_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
    finally:
        conn.close()


def get_all_roles():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role_id, role_name, description
            FROM roles
            ORDER BY role_name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching roles: {e}")
        return []
    finally:
        conn.close()


def create_user(username, full_name, email,
                password, role_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        hashed = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        cursor.execute("""
            INSERT INTO users
                (username, full_name, email,
                 password_hash, role_id)
            VALUES (?, ?, ?, ?, ?)
        """, (username, full_name, email,
              hashed, role_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        conn.close()


def update_user(user_id, full_name, email, role_id):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET full_name = ?,
                email     = ?,
                role_id   = ?
            WHERE user_id = ?
        """, (full_name, email, role_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
    finally:
        conn.close()


def reset_user_password(user_id, new_password):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        hashed = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        cursor.execute("""
            UPDATE users
            SET password_hash = ?
            WHERE user_id = ?
        """, (hashed, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False
    finally:
        conn.close()


def toggle_user_status(user_id, current_status):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET is_active = ?
            WHERE user_id = ?
        """, (0 if current_status else 1, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error toggling user: {e}")
        return False
    finally:
        conn.close()


def get_all_settings():
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT [key], [value] FROM settings")
        return {row[0]: row[1] for row in cursor.fetchall()}
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return {}
    finally:
        conn.close()


def save_setting(key, value):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            IF EXISTS (
                SELECT 1 FROM settings WHERE [key] = ?
            )
                UPDATE settings SET [value] = ?
                WHERE [key] = ?
            ELSE
                INSERT INTO settings ([key], [value])
                VALUES (?, ?)
        """, (key, value, key, key, value))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving setting: {e}")
        return False
    finally:
        conn.close()


def get_audit_logs(limit=100):
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP (?)
                al.log_id,
                COALESCE(u.full_name, 'System') AS user_name,
                al.action,
                al.table_name,
                al.record_id,
                al.action_time
            FROM audit_logs al
            LEFT JOIN users u
                ON al.user_id = u.user_id
            ORDER BY al.action_time DESC
        """, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        return []
    finally:
        conn.close()


def backup_database(backup_path):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            BACKUP DATABASE restaurant_management_system
            TO DISK = ?
            WITH FORMAT, INIT,
            NAME = 'Restaurant Management System Backup'
        """, (backup_path,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error backing up database: {e}")
        return False
    finally:
        conn.close()