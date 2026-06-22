import bcrypt
from database.connection import create_connection

def hash_password(plain_password):
    """Hash a plain password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def setup_admin_password():
    """
    On first run, if admin password is not hashed yet, hash it.
    """
    conn = create_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
        row = cursor.fetchone()
        if row and not row[0].startswith('$2b$'):
            hashed = hash_password(row[0])
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = 'admin'",
                (hashed,)
            )
            conn.commit()
            print("Admin password hashed successfully")
    except Exception as e:
        print(f"Error setting up admin password: {e}")
    finally:
        conn.close()

def authenticate_user(username, password):
    """
    Authenticate a user by username and password.
    Returns (user_details, error_message).
    """
    conn = create_connection()
    if not conn:
        return None, "Unable to connect to the database."
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.user_id, u.username, u.full_name, u.password_hash,
                   u.is_active, r.role_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.role_id
            WHERE u.username = ?
        """, (username,))
        row = cursor.fetchone()

        if not row:
            return None, "Invalid username or password."

        user_id, uname, full_name, password_hash, is_active, role_name = row

        if not is_active:
            return None, "Your account is inactive. Please contact an administrator."

        if not verify_password(password, password_hash):
            return None, "Invalid username or password."

        # Update last login
        cursor.execute(
            "UPDATE users SET last_login = GETDATE() WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()

        return {
            "user_id":   user_id,
            "username":  uname,
            "full_name": full_name,
            "role":      role_name
        }, None

    except Exception as e:
        print(f"Authentication error: {e}")
        return None, "An unexpected error occurred during login."
    finally:
        conn.close()

def log_action(user_id, action, table_name=None, record_id=None):
    """Log an action to the audit_logs table."""
    conn = create_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, table_name, record_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, action, table_name, record_id))
        conn.commit()
    except Exception as e:
        print(f"Logging error: {e}")
    finally:
        conn.close()