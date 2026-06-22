from flask import Blueprint, render_template, request, jsonify
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required
from datetime import date, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    return render_template('reports.html')

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
