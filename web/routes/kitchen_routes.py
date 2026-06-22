from flask import Blueprint, render_template, request, jsonify
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required

kitchen_bp = Blueprint('kitchen', __name__)

@kitchen_bp.route('/kitchen')
@login_required
def index():
    orders = query(
        """SELECT ko.kitchen_order_id, ko.order_id, ko.table_number,
                  ko.customer_name, ko.status, ko.priority, ko.notes,
                  ko.created_at, ko.updated_at
           FROM kitchen_orders ko
           WHERE ko.status != 'Served'
           ORDER BY CASE ko.priority WHEN 'High' THEN 1 WHEN 'Normal' THEN 2 ELSE 3 END,
                    ko.created_at ASC""",
        fetchall=True
    ) or []
    orders_with_items = []
    for o in orders:
        items = query("SELECT item_name, quantity, status FROM kitchen_order_items WHERE kitchen_order_id=%s",
                      (o['kitchen_order_id'],), fetchall=True) or []
        orders_with_items.append({'order': dict(o), 'items': [dict(i) for i in items]})
    stats = {
        'pending': query_scalar("SELECT COUNT(*) FROM kitchen_orders WHERE status='Pending'") or 0,
        'preparing': query_scalar("SELECT COUNT(*) FROM kitchen_orders WHERE status='Preparing'") or 0,
        'ready': query_scalar("SELECT COUNT(*) FROM kitchen_orders WHERE status='Ready'") or 0,
    }
    return render_template('kitchen.html', orders=orders_with_items, stats=stats)

@kitchen_bp.route('/kitchen/update_status', methods=['POST'])
@login_required
def update_status():
    d = request.get_json()
    query("UPDATE kitchen_orders SET status=%s, updated_at=NOW() WHERE kitchen_order_id=%s",
          (d['status'], d['kitchen_order_id']), commit=True)
    return jsonify({'success': True})

@kitchen_bp.route('/kitchen/api/orders')
@login_required
def api_orders():
    orders = query(
        """SELECT ko.kitchen_order_id, ko.order_id, ko.table_number,
                  ko.customer_name, ko.status, ko.priority, ko.created_at
           FROM kitchen_orders ko WHERE ko.status != 'Served'
           ORDER BY ko.created_at ASC""",
        fetchall=True
    ) or []
    result = []
    for o in orders:
        items = query("SELECT item_name, quantity FROM kitchen_order_items WHERE kitchen_order_id=%s",
                      (o['kitchen_order_id'],), fetchall=True) or []
        od = dict(o)
        od['created_at'] = str(od['created_at'])
        result.append({'order': od, 'items': [dict(i) for i in items]})
    return jsonify(result)
