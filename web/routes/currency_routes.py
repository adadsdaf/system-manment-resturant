from flask import Blueprint, render_template, request, jsonify, session
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required

currency_bp = Blueprint('currency', __name__)

@currency_bp.route('/currencies')
@login_required
def index():
    if session.get('role') not in ('Admin', 'Manager'):
        return render_template('403.html')
    currencies = query("SELECT * FROM currencies ORDER BY is_local DESC, currency_name", fetchall=True) or []
    return render_template('currencies.html', currencies=currencies)

@currency_bp.route('/currencies/create', methods=['POST'])
@login_required
def create():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        if d.get('is_local'):
            query("UPDATE currencies SET is_local=FALSE", commit=True)
        query(
            """INSERT INTO currencies (currency_name, currency_code, symbol, is_local, exchange_rate, is_active)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (d.get('currency_name'), d.get('currency_code'), d.get('symbol',''),
             d.get('is_local', False), d.get('exchange_rate', 1.0), d.get('is_active', True)),
            commit=True
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@currency_bp.route('/currencies/update', methods=['POST'])
@login_required
def update():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        if d.get('is_local'):
            query("UPDATE currencies SET is_local=FALSE WHERE currency_id != %s", (d['currency_id'],), commit=True)
        query(
            """UPDATE currencies SET currency_name=%s, currency_code=%s, symbol=%s,
               is_local=%s, exchange_rate=%s, is_active=%s WHERE currency_id=%s""",
            (d.get('currency_name'), d.get('currency_code'), d.get('symbol',''),
             d.get('is_local', False), d.get('exchange_rate', 1.0),
             d.get('is_active', True), d.get('currency_id')),
            commit=True
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@currency_bp.route('/currencies/delete', methods=['POST'])
@login_required
def delete():
    if session.get('role') != 'Admin':
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        is_local = query_scalar("SELECT is_local FROM currencies WHERE currency_id=%s", (d['currency_id'],))
        if is_local:
            return jsonify({'success': False, 'error': 'لا يمكن حذف العملة المحلية'})
        query("DELETE FROM currencies WHERE currency_id=%s", (d['currency_id'],), commit=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@currency_bp.route('/currencies/list')
@login_required
def list_currencies():
    curs = query("SELECT currency_id, currency_name, currency_code, symbol, is_local, exchange_rate FROM currencies WHERE is_active=TRUE ORDER BY is_local DESC, currency_name", fetchall=True) or []
    return jsonify([dict(c) for c in curs])
