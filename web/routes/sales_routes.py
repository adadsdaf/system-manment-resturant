from flask import Blueprint, render_template, request, jsonify, session
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required
from datetime import date

sales_bp = Blueprint('sales', __name__)

def next_invoice_no():
    last = query_scalar(
        "SELECT invoice_no FROM sales_invoices ORDER BY invoice_id DESC LIMIT 1"
    )
    if last:
        try:
            num = int(last.replace('INV-', '')) + 1
        except Exception:
            num = 1
    else:
        num = 1
    return f"INV-{num:05d}"

def next_return_no():
    last = query_scalar(
        "SELECT return_no FROM sales_returns ORDER BY return_id DESC LIMIT 1"
    )
    if last:
        try:
            num = int(last.replace('RET-', '')) + 1
        except Exception:
            num = 1
    else:
        num = 1
    return f"RET-{num:05d}"

# ======================== فواتير المبيعات ========================

@sales_bp.route('/sales/invoices')
@login_required
def invoices():
    invoices = query(
        """SELECT si.*, c.full_name as cust_name, b.arabic_name as branch_name,
                  u.full_name as creator_name
           FROM sales_invoices si
           LEFT JOIN customers c ON si.customer_id=c.customer_id
           LEFT JOIN branches b ON si.branch_id=b.branch_id
           LEFT JOIN users u ON si.created_by=u.user_id
           ORDER BY si.created_at DESC LIMIT 200""",
        fetchall=True
    ) or []
    customers = query("SELECT customer_id, full_name, phone FROM customers WHERE is_active=TRUE ORDER BY full_name", fetchall=True) or []
    branches = query("SELECT branch_id, arabic_name FROM branches WHERE is_active=TRUE ORDER BY arabic_name", fetchall=True) or []
    menu_items = query(
        """SELECT mi.item_id, mi.item_name, mi.price, mc.category_name
           FROM menu_items mi JOIN menu_categories mc ON mi.category_id=mc.category_id
           WHERE mi.is_available=TRUE ORDER BY mc.category_name, mi.item_name""",
        fetchall=True
    ) or []
    tax_rate = query_scalar("SELECT value FROM settings WHERE key='tax_rate'") or '15'
    currency = query_scalar("SELECT value FROM settings WHERE key='currency'") or 'ر.س'
    return render_template('sales_invoices.html',
                           invoices=invoices, customers=customers,
                           branches=branches, menu_items=menu_items,
                           tax_rate=tax_rate, currency=currency,
                           today=date.today().isoformat(),
                           next_no=next_invoice_no())

@sales_bp.route('/sales/invoices/create', methods=['POST'])
@login_required
def create_invoice():
    d = request.get_json()
    try:
        inv_no = d.get('invoice_no') or next_invoice_no()
        query(
            """INSERT INTO sales_invoices
               (invoice_no, invoice_date, customer_id, customer_name, branch_id,
                sales_rep_id, payment_method, payment_type, store_no, center_no,
                invoice_type, price_type, salesman_name, salesman_commission,
                subtotal, discount_pct, discount_amount, tax_pct, tax_amount,
                total_amount, paid_amount, remaining_amount, notes, status, created_by)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                inv_no, d.get('invoice_date', date.today().isoformat()),
                d.get('customer_id'), d.get('customer_name',''),
                d.get('branch_id') or session.get('branch_id'),
                session.get('user_id'), d.get('payment_method','نقدي'),
                d.get('payment_type','آجل'), d.get('store_no',''), d.get('center_no',''),
                d.get('invoice_type','فاتورة مبيعات'), d.get('price_type','سعر البيع'),
                d.get('salesman_name',''), d.get('salesman_commission', 0),
                d.get('subtotal', 0), d.get('discount_pct', 0), d.get('discount_amount', 0),
                d.get('tax_pct', 0), d.get('tax_amount', 0), d.get('total_amount', 0),
                d.get('paid_amount', 0), d.get('remaining_amount', 0),
                d.get('notes',''), d.get('status','مكتملة'), session.get('user_id')
            ), commit=True
        )
        invoice_id = query_scalar("SELECT invoice_id FROM sales_invoices WHERE invoice_no=%s", (inv_no,))
        items = d.get('items', [])
        for it in items:
            query(
                """INSERT INTO sales_invoice_items
                   (invoice_id, menu_item_id, item_name, item_code, quantity,
                    unit, unit_price, discount_pct, tax_pct, subtotal)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    invoice_id, it.get('menu_item_id'), it.get('item_name',''),
                    it.get('item_code',''), it.get('quantity', 1),
                    it.get('unit',''), it.get('unit_price', 0),
                    it.get('discount_pct', 0), it.get('tax_pct', 0), it.get('subtotal', 0)
                ), commit=True
            )
        return jsonify({'success': True, 'invoice_no': inv_no, 'invoice_id': invoice_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sales_bp.route('/sales/invoices/<int:invoice_id>')
@login_required
def get_invoice(invoice_id):
    inv = query("SELECT * FROM sales_invoices WHERE invoice_id=%s", (invoice_id,), fetchone=True)
    if not inv:
        return jsonify({'error': 'not found'}), 404
    items = query("SELECT * FROM sales_invoice_items WHERE invoice_id=%s", (invoice_id,), fetchall=True) or []
    return jsonify({'invoice': dict(inv), 'items': [dict(i) for i in items]})

@sales_bp.route('/sales/invoices/delete', methods=['POST'])
@login_required
def delete_invoice():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        query("DELETE FROM sales_invoice_items WHERE invoice_id=%s", (d['invoice_id'],), commit=True)
        query("DELETE FROM sales_invoices WHERE invoice_id=%s", (d['invoice_id'],), commit=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ======================== مردود المبيعات ========================

@sales_bp.route('/sales/returns')
@login_required
def returns():
    returns_list = query(
        """SELECT sr.*, c.full_name as cust_name, b.arabic_name as branch_name,
                  si.invoice_no as orig_inv_no, u.full_name as creator_name
           FROM sales_returns sr
           LEFT JOIN customers c ON sr.customer_id=c.customer_id
           LEFT JOIN branches b ON sr.branch_id=b.branch_id
           LEFT JOIN sales_invoices si ON sr.original_invoice_id=si.invoice_id
           LEFT JOIN users u ON sr.created_by=u.user_id
           ORDER BY sr.created_at DESC LIMIT 200""",
        fetchall=True
    ) or []
    customers = query("SELECT customer_id, full_name, phone FROM customers WHERE is_active=TRUE ORDER BY full_name", fetchall=True) or []
    branches = query("SELECT branch_id, arabic_name FROM branches WHERE is_active=TRUE ORDER BY arabic_name", fetchall=True) or []
    invoices = query("SELECT invoice_id, invoice_no, customer_name, total_amount FROM sales_invoices ORDER BY created_at DESC LIMIT 100", fetchall=True) or []
    menu_items = query(
        """SELECT mi.item_id, mi.item_name, mi.price, mc.category_name
           FROM menu_items mi JOIN menu_categories mc ON mi.category_id=mc.category_id
           WHERE mi.is_available=TRUE ORDER BY mc.category_name, mi.item_name""",
        fetchall=True
    ) or []
    currency = query_scalar("SELECT value FROM settings WHERE key='currency'") or 'ر.س'
    return render_template('sales_returns.html',
                           returns=returns_list, customers=customers,
                           branches=branches, invoices=invoices,
                           menu_items=menu_items, currency=currency,
                           today=date.today().isoformat(),
                           next_no=next_return_no())

@sales_bp.route('/sales/returns/create', methods=['POST'])
@login_required
def create_return():
    d = request.get_json()
    try:
        ret_no = d.get('return_no') or next_return_no()
        query(
            """INSERT INTO sales_returns
               (return_no, return_date, original_invoice_id, original_invoice_no,
                customer_id, customer_name, branch_id, store_no, center_no,
                payment_method, return_reason, subtotal, discount_amount,
                tax_amount, total_amount, status, notes, created_by)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                ret_no, d.get('return_date', date.today().isoformat()),
                d.get('original_invoice_id'), d.get('original_invoice_no',''),
                d.get('customer_id'), d.get('customer_name',''),
                d.get('branch_id') or session.get('branch_id'),
                d.get('store_no',''), d.get('center_no',''),
                d.get('payment_method','نقدي'), d.get('return_reason',''),
                d.get('subtotal', 0), d.get('discount_amount', 0),
                d.get('tax_amount', 0), d.get('total_amount', 0),
                d.get('status','معلقة'), d.get('notes',''), session.get('user_id')
            ), commit=True
        )
        return_id = query_scalar("SELECT return_id FROM sales_returns WHERE return_no=%s", (ret_no,))
        for it in d.get('items', []):
            query(
                """INSERT INTO sales_return_items
                   (return_id, menu_item_id, item_name, item_code, quantity,
                    unit, unit_price, tax_pct, quantity_invoiced, discount_pct, subtotal)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    return_id, it.get('menu_item_id'), it.get('item_name',''),
                    it.get('item_code',''), it.get('quantity', 1),
                    it.get('unit',''), it.get('unit_price', 0),
                    it.get('tax_pct', 0), it.get('quantity_invoiced', 0),
                    it.get('discount_pct', 0), it.get('subtotal', 0)
                ), commit=True
            )
        return jsonify({'success': True, 'return_no': ret_no, 'return_id': return_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sales_bp.route('/sales/returns/<int:return_id>')
@login_required
def get_return(return_id):
    ret = query("SELECT * FROM sales_returns WHERE return_id=%s", (return_id,), fetchone=True)
    if not ret:
        return jsonify({'error': 'not found'}), 404
    items = query("SELECT * FROM sales_return_items WHERE return_id=%s", (return_id,), fetchall=True) or []
    return jsonify({'return': dict(ret), 'items': [dict(i) for i in items]})

@sales_bp.route('/sales/returns/approve', methods=['POST'])
@login_required
def approve_return():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        query("UPDATE sales_returns SET status='مكتملة', updated_at=NOW() WHERE return_id=%s",
              (d['return_id'],), commit=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sales_bp.route('/sales/returns/delete', methods=['POST'])
@login_required
def delete_return():
    if session.get('role') not in ('Admin', 'Manager'):
        return jsonify({'success': False, 'error': 'غير مصرح'})
    d = request.get_json()
    try:
        query("DELETE FROM sales_return_items WHERE return_id=%s", (d['return_id'],), commit=True)
        query("DELETE FROM sales_returns WHERE return_id=%s", (d['return_id'],), commit=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sales_bp.route('/sales/sessions')
@login_required
def user_sessions():
    if session.get('role') not in ('Admin', 'Manager'):
        return render_template('403.html')
    sessions_data = query(
        """SELECT us.*, u.full_name, b.arabic_name as branch_name
           FROM user_sessions us
           LEFT JOIN users u ON us.user_id=u.user_id
           LEFT JOIN branches b ON us.branch_id=b.branch_id
           ORDER BY us.login_time DESC LIMIT 200""",
        fetchall=True
    ) or []
    return render_template('user_sessions.html', sessions=sessions_data)
