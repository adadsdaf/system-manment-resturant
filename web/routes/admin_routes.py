from flask import Blueprint, render_template, request, jsonify, session
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required
from web.auth import hash_password

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def index():
    if session.get('role') != 'Admin':
        return render_template('403.html')
    users = query(
        """SELECT u.user_id, u.username, u.full_name, u.email, u.is_active,
                  u.last_login, u.created_at, r.role_name, r.role_id
           FROM users u LEFT JOIN roles r ON u.role_id=r.role_id ORDER BY u.full_name""",
        fetchall=True
    ) or []
    roles = query("SELECT role_id, role_name FROM roles ORDER BY role_name", fetchall=True) or []
    settings = query("SELECT key, value FROM settings ORDER BY key", fetchall=True) or {}
    settings_dict = {s['key']: s['value'] for s in settings}
    tables = query("SELECT * FROM restaurant_tables WHERE is_active=true ORDER BY location, table_number", fetchall=True) or []
    audit = query(
        """SELECT al.log_id, COALESCE(u.full_name,'System') as user_name,
                  al.action, al.table_name, al.record_id, al.action_time
           FROM audit_logs al LEFT JOIN users u ON al.user_id=u.user_id
           ORDER BY al.action_time DESC LIMIT 100""",
        fetchall=True
    ) or []
    return render_template('admin.html', users=users, roles=roles,
                           settings=settings_dict, tables=tables, audit=audit)

@admin_bp.route('/admin/create_user', methods=['POST'])
@login_required
def create_user():
    d = request.get_json()
    hashed = hash_password(d['password'])
    try:
        query("INSERT INTO users (username,full_name,email,password_hash,role_id) VALUES (%s,%s,%s,%s,%s)",
              (d['username'],d['full_name'],d.get('email',''),hashed,d['role_id']), commit=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/admin/update_user', methods=['POST'])
@login_required
def update_user():
    d = request.get_json()
    query("UPDATE users SET full_name=%s,email=%s,role_id=%s WHERE user_id=%s",
          (d['full_name'],d.get('email',''),d['role_id'],d['user_id']), commit=True)
    return jsonify({'success': True})

@admin_bp.route('/admin/reset_password', methods=['POST'])
@login_required
def reset_password():
    d = request.get_json()
    hashed = hash_password(d['new_password'])
    query("UPDATE users SET password_hash=%s WHERE user_id=%s", (hashed, d['user_id']), commit=True)
    return jsonify({'success': True})

@admin_bp.route('/admin/toggle_user', methods=['POST'])
@login_required
def toggle_user():
    d = request.get_json()
    query("UPDATE users SET is_active=NOT is_active WHERE user_id=%s", (d['user_id'],), commit=True)
    return jsonify({'success': True})

@admin_bp.route('/admin/save_setting', methods=['POST'])
@login_required
def save_setting():
    d = request.get_json()
    query("INSERT INTO settings (key,value) VALUES (%s,%s) ON CONFLICT (key) DO UPDATE SET value=%s",
          (d['key'],d['value'],d['value']), commit=True)
    return jsonify({'success': True})

@admin_bp.route('/admin/add_table', methods=['POST'])
@login_required
def add_table():
    d = request.get_json()
    query("INSERT INTO restaurant_tables (table_number,capacity,location) VALUES (%s,%s,%s)",
          (d['table_number'],d.get('capacity',4),d.get('location','Main')), commit=True)
    return jsonify({'success': True})

@admin_bp.route('/admin/delete_table', methods=['POST'])
@login_required
def delete_table():
    d = request.get_json()
    query("UPDATE restaurant_tables SET is_active=false WHERE table_id=%s", (d['table_id'],), commit=True)
    return jsonify({'success': True})
