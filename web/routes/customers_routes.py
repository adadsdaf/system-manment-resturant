from flask import Blueprint, render_template, request, jsonify
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers')
@login_required
def index():
    customers = query(
        """SELECT c.customer_id, c.full_name, c.phone, c.email, c.address,
                  c.is_active, c.created_at,
                  COALESCE(la.points_balance, 0) as points,
                  COUNT(o.order_id) as total_orders,
                  COALESCE(SUM(o.total_amount), 0) as total_spent
           FROM customers c
           LEFT JOIN loyalty_accounts la ON c.customer_id=la.customer_id
           LEFT JOIN orders o ON c.customer_id=o.customer_id
           GROUP BY c.customer_id, c.full_name, c.phone, c.email,
                    c.address, c.is_active, c.created_at, la.points_balance
           ORDER BY c.full_name""",
        fetchall=True
    ) or []
    stats = {
        'total': query_scalar("SELECT COUNT(*) FROM customers") or 0,
        'active': query_scalar("SELECT COUNT(*) FROM customers WHERE is_active=true") or 0,
        'total_points': query_scalar("SELECT COALESCE(SUM(points_balance),0) FROM loyalty_accounts") or 0,
    }
    return render_template('customers.html', customers=customers, stats=stats)

@customers_bp.route('/customers/add', methods=['POST'])
@login_required
def add():
    d = request.get_json()
    from web.db import get_db
    import psycopg2.extras
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("INSERT INTO customers (full_name,phone,email,address) VALUES (%s,%s,%s,%s) RETURNING customer_id",
                    (d['full_name'], d.get('phone',''), d.get('email',''), d.get('address','')))
        cid = cur.fetchone()['customer_id']
        cur.execute("INSERT INTO loyalty_accounts (customer_id) VALUES (%s)", (cid,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@customers_bp.route('/customers/update', methods=['POST'])
@login_required
def update():
    d = request.get_json()
    query("UPDATE customers SET full_name=%s,phone=%s,email=%s,address=%s WHERE customer_id=%s",
          (d['full_name'],d.get('phone',''),d.get('email',''),d.get('address',''),d['customer_id']), commit=True)
    return jsonify({'success': True})

@customers_bp.route('/customers/toggle', methods=['POST'])
@login_required
def toggle():
    d = request.get_json()
    query("UPDATE customers SET is_active=NOT is_active WHERE customer_id=%s", (d['customer_id'],), commit=True)
    return jsonify({'success': True})
