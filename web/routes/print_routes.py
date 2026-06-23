from flask import Blueprint, render_template, jsonify, session
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required

print_bp = Blueprint('print', __name__)

def get_receipt_settings():
    rows = query("SELECT key, value FROM settings WHERE key LIKE 'receipt_%' OR key LIKE 'kitchen_%' OR key LIKE '%_copy_label'", fetchall=True) or []
    return {r['key']: r['value'] for r in rows}

@print_bp.route('/print/order/<int:order_id>/customer')
@login_required
def customer_receipt(order_id):
    order = query(
        """SELECT o.*, u.full_name as cashier_name, b.arabic_name as branch_name,
                  b.arabic_address, b.phone as branch_phone
           FROM orders o
           LEFT JOIN users u ON o.served_by=u.user_id
           LEFT JOIN branches b ON o.branch_id=b.branch_id
           WHERE o.order_id=%s""",
        (order_id,), fetchone=True
    )
    if not order:
        return "طلب غير موجود", 404
    items = query(
        "SELECT * FROM order_items WHERE order_id=%s ORDER BY order_item_id",
        (order_id,), fetchall=True
    ) or []
    settings = get_receipt_settings()
    rest_name = query_scalar("SELECT value FROM settings WHERE key='restaurant_name'") or 'مطعم إتقان'
    rest_address = query_scalar("SELECT value FROM settings WHERE key='restaurant_address'") or ''
    rest_phone = query_scalar("SELECT value FROM settings WHERE key='restaurant_phone'") or ''
    currency = query_scalar("SELECT value FROM settings WHERE key='currency'") or 'ر.س'
    tax_rate = query_scalar("SELECT value FROM settings WHERE key='tax_rate'") or '15'
    return render_template('print/customer_receipt.html',
        order=order, items=items, settings=settings,
        rest_name=rest_name, rest_address=rest_address,
        rest_phone=rest_phone, currency=currency, tax_rate=tax_rate,
        copy_type='customer')

@print_bp.route('/print/order/<int:order_id>/worker')
@login_required
def worker_receipt(order_id):
    order = query(
        """SELECT o.*, u.full_name as cashier_name, b.arabic_name as branch_name
           FROM orders o
           LEFT JOIN users u ON o.served_by=u.user_id
           LEFT JOIN branches b ON o.branch_id=b.branch_id
           WHERE o.order_id=%s""",
        (order_id,), fetchone=True
    )
    if not order:
        return "طلب غير موجود", 404
    items = query(
        "SELECT * FROM order_items WHERE order_id=%s ORDER BY order_item_id",
        (order_id,), fetchall=True
    ) or []
    settings = get_receipt_settings()
    currency = query_scalar("SELECT value FROM settings WHERE key='currency'") or 'ر.س'
    return render_template('print/worker_receipt.html',
        order=order, items=items, settings=settings, currency=currency,
        copy_type='worker')

@print_bp.route('/print/order/<int:order_id>/kitchen')
@login_required
def kitchen_ticket(order_id):
    order = query(
        """SELECT o.*, u.full_name as cashier_name
           FROM orders o LEFT JOIN users u ON o.served_by=u.user_id
           WHERE o.order_id=%s""",
        (order_id,), fetchone=True
    )
    if not order:
        return "طلب غير موجود", 404
    items = query(
        """SELECT oi.*, mc.category_name
           FROM order_items oi
           LEFT JOIN menu_items mi ON oi.menu_item_id=mi.item_id
           LEFT JOIN menu_categories mc ON mi.category_id=mc.category_id
           WHERE oi.order_id=%s
           ORDER BY mc.category_name, oi.item_name""",
        (order_id,), fetchall=True
    ) or []
    settings = get_receipt_settings()
    # تجميع الأصناف حسب التصنيف
    categories = {}
    for it in items:
        cat = it.get('category_name') or 'عام'
        categories.setdefault(cat, []).append(it)
    return render_template('print/kitchen_ticket.html',
        order=order, categories=categories, settings=settings,
        ticket_per_cat=settings.get('kitchen_ticket_per_category','1') == '1')

@print_bp.route('/print/invoice/<int:invoice_id>/customer')
@login_required
def invoice_customer(invoice_id):
    invoice = query(
        """SELECT si.*, u.full_name as creator_name, b.arabic_name as branch_name,
                  b.arabic_address, b.phone as branch_phone
           FROM sales_invoices si
           LEFT JOIN users u ON si.created_by=u.user_id
           LEFT JOIN branches b ON si.branch_id=b.branch_id
           WHERE si.invoice_id=%s""",
        (invoice_id,), fetchone=True
    )
    if not invoice:
        return "فاتورة غير موجودة", 404
    items = query("SELECT * FROM sales_invoice_items WHERE invoice_id=%s ORDER BY item_id", (invoice_id,), fetchall=True) or []
    settings = get_receipt_settings()
    currency = query_scalar("SELECT value FROM settings WHERE key='currency'") or 'ر.س'
    rest_name = query_scalar("SELECT value FROM settings WHERE key='restaurant_name'") or 'مطعم إتقان'
    return render_template('print/invoice_receipt.html',
        invoice=invoice, items=items, settings=settings,
        currency=currency, rest_name=rest_name)
