from flask import Blueprint, render_template, request, jsonify, session
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required
from datetime import date, timedelta

reports_bp = Blueprint('reports', __name__)

def get_date_range(period):
    today = date.today()
    if period == 'today':
        return today, today
    elif period == 'week':
        return today - timedelta(days=7), today
    elif period == 'month':
        return today.replace(day=1), today
    return today, today

@reports_bp.route('/reports')
@login_required
def index():
    cashiers = query(
        """SELECT u.user_id, u.full_name FROM users u
           JOIN roles r ON u.role_id=r.role_id
           WHERE r.role_name IN ('Cashier','Admin','Manager') AND u.is_active=TRUE
           ORDER BY u.full_name""",
        fetchall=True
    ) or []
    return render_template('reports.html', cashiers=cashiers)

@reports_bp.route('/reports/api/summary')
@login_required
def summary():
    period = request.args.get('period', 'today')
    today = date.today()
    if period == 'today':
        start = end = today
    elif period == 'week':
        start = today - timedelta(days=7)
        end = today
    elif period == 'month':
        start = today.replace(day=1)
        end = today
    else:
        start = end = today

    row = query(
        """SELECT COUNT(*) as total_orders,
                  COALESCE(SUM(total_amount),0) as total_revenue,
                  COALESCE(AVG(total_amount),0) as avg_order,
                  COALESCE(SUM(discount_amount),0) as total_discount,
                  COALESCE(SUM(tax_amount),0) as total_tax
           FROM orders WHERE DATE(created_at) BETWEEN %s AND %s AND order_status='Completed'""",
        (start, end), fetchone=True
    ) or {}

    daily = query(
        """SELECT DATE(created_at) as sale_date, COUNT(*) as orders,
                  COALESCE(SUM(total_amount),0) as revenue
           FROM orders WHERE DATE(created_at) BETWEEN %s AND %s AND order_status='Completed'
           GROUP BY DATE(created_at) ORDER BY sale_date""",
        (start, end), fetchall=True
    ) or []

    by_payment = query(
        """SELECT payment_method, COUNT(*) as orders, COALESCE(SUM(total_amount),0) as revenue
           FROM orders WHERE DATE(created_at) BETWEEN %s AND %s AND order_status='Completed'
           GROUP BY payment_method ORDER BY revenue DESC""",
        (start, end), fetchall=True
    ) or []

    top_items = query(
        """SELECT oi.item_name, SUM(oi.quantity) as total_qty, COALESCE(SUM(oi.subtotal),0) as revenue
           FROM order_items oi JOIN orders o ON oi.order_id=o.order_id
           WHERE DATE(o.created_at) BETWEEN %s AND %s AND o.order_status='Completed'
           GROUP BY oi.item_name ORDER BY total_qty DESC LIMIT 10""",
        (start, end), fetchall=True
    ) or []

    by_category = query(
        """SELECT mc.category_name, SUM(oi.quantity) as qty, COALESCE(SUM(oi.subtotal),0) as revenue
           FROM order_items oi
           JOIN orders o ON oi.order_id=o.order_id
           JOIN menu_items mi ON oi.menu_item_id=mi.item_id
           JOIN menu_categories mc ON mi.category_id=mc.category_id
           WHERE DATE(o.created_at) BETWEEN %s AND %s AND o.order_status='Completed'
           GROUP BY mc.category_name ORDER BY revenue DESC""",
        (start, end), fetchall=True
    ) or []

    low_stock = query(
        """SELECT i.name, i.unit, i.current_stock, i.minimum_stock, i.reorder_level,
                  COALESCE(s.supplier_name,'—') as supplier
           FROM ingredients i LEFT JOIN suppliers s ON i.supplier_id=s.supplier_id
           WHERE i.current_stock<=i.reorder_level AND i.is_active=true ORDER BY i.current_stock""",
        fetchall=True
    ) or []

    return jsonify({
        'summary': {k: float(v) if v else 0 for k, v in dict(row).items()},
        'daily': [{'date': str(r['sale_date']), 'orders': r['orders'], 'revenue': float(r['revenue'])} for r in daily],
        'by_payment': [{'method': r['payment_method'], 'orders': r['orders'], 'revenue': float(r['revenue'])} for r in by_payment],
        'top_items': [{'name': r['item_name'], 'qty': r['total_qty'], 'revenue': float(r['revenue'])} for r in top_items],
        'by_category': [{'name': r['category_name'], 'qty': r['qty'], 'revenue': float(r['revenue'])} for r in by_category],
        'low_stock': [dict(r) for r in low_stock],
    })


@reports_bp.route('/reports/api/by_cashier')
@login_required
def by_cashier():
    period = request.args.get('period', 'today')
    cashier_id = request.args.get('cashier_id', '')
    start, end = get_date_range(period)

    cashier_filter = ""
    params_all = [start, end]
    if cashier_id:
        cashier_filter = "AND o.served_by=%s"
        params_all = [start, end, cashier_id]

    cashiers_perf = query(
        f"""SELECT u.user_id, u.full_name,
                  COUNT(o.order_id) as total_orders,
                  COALESCE(SUM(o.total_amount),0) as total_revenue,
                  COALESCE(AVG(o.total_amount),0) as avg_order,
                  COALESCE(SUM(o.discount_amount),0) as total_discount,
                  COALESCE(SUM(o.tax_amount),0) as total_tax,
                  MIN(o.created_at) as first_order,
                  MAX(o.created_at) as last_order
           FROM orders o
           JOIN users u ON o.served_by=u.user_id
           WHERE DATE(o.created_at) BETWEEN %s AND %s
             AND o.order_status='Completed'
             {cashier_filter}
           GROUP BY u.user_id, u.full_name
           ORDER BY total_revenue DESC""",
        params_all, fetchall=True
    ) or []

    top_items_by_cashier = []
    if cashier_id:
        top_items_by_cashier = query(
            """SELECT oi.item_name, SUM(oi.quantity) as qty,
                      COALESCE(SUM(oi.subtotal),0) as revenue
               FROM order_items oi
               JOIN orders o ON oi.order_id=o.order_id
               WHERE DATE(o.created_at) BETWEEN %s AND %s
                 AND o.order_status='Completed'
                 AND o.served_by=%s
               GROUP BY oi.item_name
               ORDER BY qty DESC LIMIT 10""",
            [start, end, cashier_id], fetchall=True
        ) or []

    hourly = []
    if cashier_id:
        hourly = query(
            """SELECT EXTRACT(HOUR FROM o.created_at)::int as hr,
                      COUNT(*) as orders,
                      COALESCE(SUM(o.total_amount),0) as revenue
               FROM orders o
               WHERE DATE(o.created_at) BETWEEN %s AND %s
                 AND o.order_status='Completed'
                 AND o.served_by=%s
               GROUP BY EXTRACT(HOUR FROM o.created_at)
               ORDER BY hr""",
            [start, end, cashier_id], fetchall=True
        ) or []

    return jsonify({
        'cashiers': [
            {
                'user_id': r['user_id'],
                'name': r['full_name'],
                'orders': r['total_orders'],
                'revenue': float(r['total_revenue']),
                'avg': float(r['avg_order']),
                'discount': float(r['total_discount']),
                'tax': float(r['total_tax']),
                'first_order': str(r['first_order']) if r['first_order'] else None,
                'last_order': str(r['last_order']) if r['last_order'] else None,
            }
            for r in cashiers_perf
        ],
        'top_items': [{'name': r['item_name'], 'qty': r['qty'], 'revenue': float(r['revenue'])} for r in top_items_by_cashier],
        'hourly': [{'hr': r['hr'], 'orders': r['orders'], 'revenue': float(r['revenue'])} for r in hourly],
    })


@reports_bp.route('/reports/api/cashier_orders')
@login_required
def cashier_orders():
    cashier_id = request.args.get('cashier_id', '')
    period = request.args.get('period', 'today')
    start, end = get_date_range(period)
    if not cashier_id:
        return jsonify([])
    orders = query(
        """SELECT o.order_id, o.customer_name, o.total_amount, o.discount_amount,
                  o.tax_amount, o.payment_method, o.order_status, o.created_at,
                  o.table_number
           FROM orders o
           WHERE DATE(o.created_at) BETWEEN %s AND %s
             AND o.order_status='Completed'
             AND o.served_by=%s
           ORDER BY o.created_at DESC LIMIT 100""",
        [start, end, cashier_id], fetchall=True
    ) or []
    return jsonify([
        {**dict(r), 'created_at': str(r['created_at'])} for r in orders
    ])
