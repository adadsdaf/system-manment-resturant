import bcrypt
from web.db import query, query_scalar
from datetime import datetime

def authenticate_user(username, password, ip_address='', machine_name=''):
    user = query(
        """SELECT u.user_id, u.username, u.full_name, u.password_hash,
                  u.is_active, u.branch_id, r.role_name
           FROM users u
           LEFT JOIN roles r ON u.role_id = r.role_id
           WHERE u.username = %s""",
        (username,), fetchone=True
    )
    if not user:
        return None, "اسم المستخدم أو كلمة المرور غير صحيحة"
    if not user['is_active']:
        return None, "الحساب غير نشط، تواصل مع المدير"
    if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return None, "اسم المستخدم أو كلمة المرور غير صحيحة"

    now = datetime.now()
    query("UPDATE users SET last_login=%s WHERE user_id=%s",
          (now, user['user_id']), commit=True)

    # تسجيل جلسة الدخول
    query(
        """INSERT INTO user_sessions
           (user_id, username, login_time, ip_address, machine_name, branch_id, session_status)
           VALUES (%s, %s, %s, %s, %s, %s, 'active')""",
        (user['user_id'], user['username'], now, ip_address, machine_name, user['branch_id']),
        commit=True
    )

    session_id = query_scalar(
        "SELECT session_id FROM user_sessions WHERE user_id=%s ORDER BY session_id DESC LIMIT 1",
        (user['user_id'],)
    )

    return {
        'user_id': user['user_id'],
        'username': user['username'],
        'full_name': user['full_name'],
        'role': user['role_name'],
        'branch_id': user['branch_id'],
        'session_id': session_id
    }, None

def logout_user(session_id):
    if session_id:
        query(
            "UPDATE user_sessions SET logout_time=%s, session_status='closed' WHERE session_id=%s",
            (datetime.now(), session_id), commit=True
        )

def hash_password(plain):
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
