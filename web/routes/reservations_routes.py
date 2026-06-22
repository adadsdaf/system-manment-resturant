from flask import Blueprint, render_template, request, jsonify, session
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required
from datetime import date

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/reservations')
@login_required
def index():
    today = date.today()
    reservations = query(
        """SELECT r.reservation_id, r.customer_name, r.phone, r.guests,
                  r.reservation_date, r.reservation_time, r.status,
                  r.special_requests, COALESCE(t.table_number,'—') as table_number,
                  r.created_at
           FROM reservations r
           LEFT JOIN restaurant_tables t ON r.table_id=t.table_id
           ORDER BY r.reservation_date DESC, r.reservation_time""",
        fetchall=True
    ) or []
    tables = query("SELECT table_id, table_number, capacity, location FROM restaurant_tables WHERE is_active=true ORDER BY table_number",
                   fetchall=True) or []
    stats = {
        'total_today': query_scalar("SELECT COUNT(*) FROM reservations WHERE reservation_date=%s", (today,)) or 0,
        'confirmed': query_scalar("SELECT COUNT(*) FROM reservations WHERE reservation_date=%s AND status='Confirmed'", (today,)) or 0,
        'pending': query_scalar("SELECT COUNT(*) FROM reservations WHERE reservation_date=%s AND status='Pending'", (today,)) or 0,
    }
    return render_template('reservations.html', reservations=reservations, tables=tables, stats=stats)

@reservations_bp.route('/reservations/add', methods=['POST'])
@login_required
def add():
    d = request.get_json()
    query("""INSERT INTO reservations (customer_name,phone,table_id,guests,reservation_date,reservation_time,special_requests,created_by)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
          (d['customer_name'],d.get('phone',''),d.get('table_id') or None,
           d.get('guests',1),d['reservation_date'],d.get('reservation_time',''),
           d.get('special_requests',''),session['user_id']), commit=True)
    return jsonify({'success': True})

@reservations_bp.route('/reservations/update_status', methods=['POST'])
@login_required
def update_status():
    d = request.get_json()
    query("UPDATE reservations SET status=%s, updated_at=NOW() WHERE reservation_id=%s",
          (d['status'], d['reservation_id']), commit=True)
    return jsonify({'success': True})

@reservations_bp.route('/reservations/delete', methods=['POST'])
@login_required
def delete():
    d = request.get_json()
    query("DELETE FROM reservations WHERE reservation_id=%s", (d['reservation_id'],), commit=True)
    return jsonify({'success': True})
