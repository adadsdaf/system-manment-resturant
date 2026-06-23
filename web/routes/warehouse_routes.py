from flask import Blueprint, render_template, request, jsonify, session
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required

warehouse_bp = Blueprint('warehouse', __name__)

@warehouse_bp.route('/warehouses')
@login_required
def index():
    warehouses = query(
        """SELECT w.*, b.arabic_name as branch_name
           FROM warehouses w
           LEFT JOIN branches b ON w.branch_id=b.branch_id
           ORDER BY w.is_main DESC, w.warehouse_code""",
        fetchall=True
    ) or []
    branches = query("SELECT branch_id, arabic_name FROM branches WHERE is_active=TRUE ORDER BY arabic_name", fetchall=True) or []
    stats = {
        'total': len(warehouses),
        'active': sum(1 for w in warehouses if w['is_active']),
        'main': sum(1 for w in warehouses if w['is_main']),
    }
    return render_template('warehouses.html', warehouses=warehouses, branches=branches, stats=stats)

@warehouse_bp.route('/warehouses/get/<int:wid>')
@login_required
def get_warehouse(wid):
    w = query("SELECT * FROM warehouses WHERE warehouse_id=%s", (wid,), fetchone=True)
    if w:
        return jsonify(dict(w))
    return jsonify({'error': 'not found'}), 404

@warehouse_bp.route('/warehouses/create', methods=['POST'])
@login_required
def create():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        query(
            """INSERT INTO warehouses
               (warehouse_code, arabic_name, foreign_name, warehouse_type, is_main,
                is_principal, is_sales_branch, has_raw_materials, city, country,
                delegate, supervisor, phone, email, address, account_no, tax_no,
                branch_id, is_active, notes)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (d.get('warehouse_code'), d.get('arabic_name'), d.get('foreign_name',''),
             d.get('warehouse_type','main'), d.get('is_main', False),
             d.get('is_principal', False), d.get('is_sales_branch', False),
             d.get('has_raw_materials', False), d.get('city',''), d.get('country',''),
             d.get('delegate',''), d.get('supervisor',''), d.get('phone',''),
             d.get('email',''), d.get('address',''), d.get('account_no',''),
             d.get('tax_no',''), d.get('branch_id') or None, d.get('is_active', True),
             d.get('notes','')),
            commit=True
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@warehouse_bp.route('/warehouses/update', methods=['POST'])
@login_required
def update():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        query(
            """UPDATE warehouses SET
               warehouse_code=%s, arabic_name=%s, foreign_name=%s, warehouse_type=%s,
               is_main=%s, is_principal=%s, is_sales_branch=%s, has_raw_materials=%s,
               city=%s, country=%s, delegate=%s, supervisor=%s, phone=%s, email=%s,
               address=%s, account_no=%s, tax_no=%s, branch_id=%s,
               is_active=%s, notes=%s, updated_at=NOW()
               WHERE warehouse_id=%s""",
            (d.get('warehouse_code'), d.get('arabic_name'), d.get('foreign_name',''),
             d.get('warehouse_type','main'), d.get('is_main', False),
             d.get('is_principal', False), d.get('is_sales_branch', False),
             d.get('has_raw_materials', False), d.get('city',''), d.get('country',''),
             d.get('delegate',''), d.get('supervisor',''), d.get('phone',''),
             d.get('email',''), d.get('address',''), d.get('account_no',''),
             d.get('tax_no',''), d.get('branch_id') or None,
             d.get('is_active', True), d.get('notes',''), d.get('warehouse_id')),
            commit=True
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@warehouse_bp.route('/warehouses/delete', methods=['POST'])
@login_required
def delete():
    if session.get('role') != 'Admin':
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        in_use = query_scalar("SELECT COUNT(*) FROM ingredients WHERE warehouse_id=%s", (d['warehouse_id'],))
        if in_use and int(in_use) > 0:
            return jsonify({'success': False, 'error': 'لا يمكن حذف مخزن يحتوي على أصناف — قم بتعطيله بدلاً من ذلك'})
        query("UPDATE warehouses SET is_active=FALSE WHERE warehouse_id=%s", (d['warehouse_id'],), commit=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
