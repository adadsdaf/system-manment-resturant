from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from web.db import query, query_scalar, get_db
from web.routes.dashboard_routes import login_required
from datetime import datetime
import psycopg2.extras

pos_bp = Blueprint('pos', __name__)

@pos_bp.route('/pos')
@login_required
def index():
    categories = query(
        """SELECT DISTINCT mc.category_id, mc.category_name
           FROM menu_categories mc
           JOIN menu_items mi ON mc.category_id=mi.category_id
           WHERE mi.is_available=true ORDER BY mc.category_name""",
        fetchall=True
    ) or []
    items = query(
        """SELECT mi.item_id, mi.item_name, mc.category_name, mc.category_id,
                  mi.price, mi.description
           FROM menu_items mi
           JOIN menu_categories mc ON mi.category_id=mc.category_id
           WHERE mi.is_available=true
           ORDER BY mc.category_name, mi.item_name""",
        fetchall=True
    ) or []
    tax_rate = query_scalar("SELECT value FROM settings WHERE key='tax_rate'") or '0'
    tax_enabled = query_scalar("SELECT value FROM settings WHERE key='tax_enabled'") or '0'
    currency = query_scalar("SELECT value FROM settings WHERE key='currency'") or 'USD'
    return render_template('pos.html',
        categories=categories, items=items,
        tax_rate=float(tax_rate), tax_enabled=(tax_enabled=='1'),
        currency=currency)

@pos_bp.route('/pos/search_customer')
@login_required
def search_customer():
    phone = request.args.get('phone', '')
    if not phone:
        return jsonify(None)
    customer = query(
        """SELECT c.customer_id, c.full_name, c.phone,
                  COALESCE(la.points_balance, 0) as points
           FROM customers c
           LEFT JOIN loyalty_accounts la ON c.customer_id=la.customer_id
           WHERE c.phone=%s""",
        (phone,), fetchone=True
    )
    if customer:
        return jsonify(dict(customer))
    return jsonify(None)

@pos_bp.route('/pos/save_order', methods=['POST'])
@login_required
def save_order():
    data = request.get_json()
    cart = data.get('cart', [])
    customer_name = data.get('customer_name', 'Guest')
    customer_id = data.get('customer_id')
    discount_pct = float(data.get('discount_pct', 0))
    payment_method = data.get('payment_method', 'Cash')
    reference_no = data.get('reference_no', '')
    table_number = data.get('table_number', '')
    notes = data.get('notes', '')

    tax_rate = float(query_scalar("SELECT value FROM settings WHERE key='tax_rate'") or 0)
    tax_enabled = query_scalar("SELECT value FROM settings WHERE key='tax_enabled'") == '1'

    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    discount_amount = round(subtotal * (discount_pct / 100), 2)
    taxable = subtotal - discount_amount
    tax_amount = round(taxable * (tax_rate / 100), 2) if tax_enabled else 0
    total_amount = round(taxable + tax_amount, 2)

    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            """INSERT INTO orders (customer_name, customer_id, served_by, subtotal,
               discount_amount, tax_amount, total_amount, payment_method,
               payment_status, order_status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Paid', 'Completed')
               RETURNING order_id""",
            (customer_name or 'Guest', customer_id, session['user_id'],
             subtotal, discount_amount, tax_amount, total_amount, payment_method)
        )
        order_id = cur.fetchone()['order_id']

        for item in cart:
            cur.execute(
                """INSERT INTO order_items (order_id, menu_item_id, item_name, quantity, unit_price, subtotal)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (order_id, item['item_id'], item['name'], item['quantity'],
                 item['price'], item['price'] * item['quantity'])
            )

        cur.execute(
            """INSERT INTO payments (order_id, amount_paid, payment_method, reference_no)
               VALUES (%s, %s, %s, %s)""",
            (order_id, total_amount, payment_method, reference_no)
        )

        # Kitchen order
        if cart:
            cur.execute(
                """INSERT INTO kitchen_orders (order_id, table_number, customer_name, notes)
                   VALUES (%s, %s, %s, %s) RETURNING kitchen_order_id""",
                (order_id, table_number, customer_name, notes)
            )
            kitchen_id = cur.fetchone()['kitchen_order_id']
            for item in cart:
                cur.execute(
                    """INSERT INTO kitchen_order_items (kitchen_order_id, item_name, quantity)
                       VALUES (%s, %s, %s)""",
                    (kitchen_id, item['name'], item['quantity'])
                )

        conn.commit()
        return jsonify({
            'success': True,
            'order_id': order_id,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'tax_amount': tax_amount,
            'total_amount': total_amount
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@pos_bp.route('/pos/recent_orders')
@login_required
def recent_orders():
    orders = query(
        """SELECT o.order_id, o.customer_name, o.total_amount, o.payment_method,
                  o.order_status, o.created_at, u.full_name as served_by
           FROM orders o JOIN users u ON o.served_by=u.user_id
           ORDER BY o.created_at DESC LIMIT 20""",
        fetchall=True
    ) or []
    return render_template('pos_orders.html', orders=orders)
