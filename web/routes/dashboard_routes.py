from flask import Blueprint, render_template, session, redirect, url_for
from web.db import query, query_scalar
from datetime import date
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()
    sales_today = query_scalar(
        "SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE DATE(created_at)=%s AND order_status='Completed'",
        (today,)
    ) or 0
    orders_today = query_scalar(
        "SELECT COUNT(*) FROM orders WHERE DATE(created_at)=%s AND order_status='Completed'",
        (today,)
    ) or 0
    active_items = query_scalar("SELECT COUNT(*) FROM menu_items WHERE is_available=true") or 0
    active_cats = query_scalar("SELECT COUNT(*) FROM menu_categories WHERE is_active=true") or 0
    low_stock = query_scalar(
        "SELECT COUNT(*) FROM ingredients WHERE current_stock<=reorder_level AND is_active=true"
    ) or 0
    pending_kitchen = query_scalar(
        "SELECT COUNT(*) FROM kitchen_orders WHERE status IN ('Pending','Preparing')"
    ) or 0
    today_reservations = query_scalar(
        "SELECT COUNT(*) FROM reservations WHERE reservation_date=%s AND status NOT IN ('Cancelled','No Show')",
        (today,)
    ) or 0
    recent_orders = query(
        """SELECT o.order_id, o.customer_name, o.total_amount, o.payment_method,
                  o.order_status, o.created_at, u.full_name as served_by
           FROM orders o JOIN users u ON o.served_by=u.user_id
           ORDER BY o.created_at DESC LIMIT 8""",
        fetchall=True
    ) or []
    stats = {
        'sales_today': float(sales_today),
        'orders_today': int(orders_today),
        'active_items': int(active_items),
        'active_categories': int(active_cats),
        'low_stock': int(low_stock),
        'pending_kitchen': int(pending_kitchen),
        'today_reservations': int(today_reservations),
    }
    return render_template('dashboard.html', stats=stats, recent_orders=recent_orders)
