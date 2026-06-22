import bcrypt
from web.db import query, query_scalar
from datetime import datetime

def authenticate_user(username, password):
    user = query(
        """SELECT u.user_id, u.username, u.full_name, u.password_hash,
                  u.is_active, r.role_name
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
    query("UPDATE users SET last_login=%s WHERE user_id=%s",
          (datetime.now(), user['user_id']), commit=True)
    return {
        'user_id': user['user_id'],
        'username': user['username'],
        'full_name': user['full_name'],
        'role': user['role_name']
    }, None

def hash_password(plain):
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
