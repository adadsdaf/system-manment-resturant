from flask import Blueprint, render_template, request, jsonify, session
from web.db import query
from web.routes.dashboard_routes import login_required

branches_bp = Blueprint('branches', __name__)

@branches_bp.route('/branches')
@login_required
def index():
    if session.get('role') not in ('Admin', 'Manager'):
        return render_template('403.html')
    branches = query(
        "SELECT * FROM branches ORDER BY branch_code",
        fetchall=True
    ) or []
    return render_template('branches.html', branches=branches)

@branches_bp.route('/branches/create', methods=['POST'])
@login_required
def create():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        query(
            """INSERT INTO branches
               (branch_code, arabic_name, foreign_name, arabic_address, foreign_address,
                arabic_address2, foreign_address2, phone, fax, box_no, email,
                internet_location, financial_year, is_main, is_active)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                d.get('branch_code',''), d.get('arabic_name',''),
                d.get('foreign_name',''), d.get('arabic_address',''),
                d.get('foreign_address',''), d.get('arabic_address2',''),
                d.get('foreign_address2',''), d.get('phone',''),
                d.get('fax',''), d.get('box_no',''), d.get('email',''),
                d.get('internet_location',''), d.get('financial_year', 1),
                d.get('is_main', False), d.get('is_active', True)
            ), commit=True
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@branches_bp.route('/branches/update', methods=['POST'])
@login_required
def update():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        query(
            """UPDATE branches SET
               branch_code=%s, arabic_name=%s, foreign_name=%s, arabic_address=%s,
               foreign_address=%s, arabic_address2=%s, foreign_address2=%s, phone=%s,
               fax=%s, box_no=%s, email=%s, internet_location=%s, financial_year=%s,
               is_main=%s, is_active=%s, updated_at=NOW()
               WHERE branch_id=%s""",
            (
                d.get('branch_code'), d.get('arabic_name'), d.get('foreign_name'),
                d.get('arabic_address'), d.get('foreign_address'),
                d.get('arabic_address2'), d.get('foreign_address2'),
                d.get('phone'), d.get('fax'), d.get('box_no'), d.get('email'),
                d.get('internet_location'), d.get('financial_year', 1),
                d.get('is_main', False), d.get('is_active', True),
                d.get('branch_id')
            ), commit=True
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@branches_bp.route('/branches/delete', methods=['POST'])
@login_required
def delete():
    if session.get('role') != 'Admin':
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        query("UPDATE branches SET is_active=FALSE WHERE branch_id=%s",
              (d['branch_id'],), commit=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@branches_bp.route('/branches/get/<int:branch_id>')
@login_required
def get_branch(branch_id):
    branch = query("SELECT * FROM branches WHERE branch_id=%s", (branch_id,), fetchone=True)
    if branch:
        return jsonify(dict(branch))
    return jsonify({'error': 'Branch not found'}), 404
