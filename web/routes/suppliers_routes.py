from flask import Blueprint, render_template, request, jsonify, session
from web.db import query, query_scalar, get_db
from web.routes.dashboard_routes import login_required
import psycopg2.extras

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/suppliers')
@login_required
def index():
    suppliers = query(
        """SELECT s.supplier_id, s.supplier_name, s.contact_name, s.phone,
                  s.email, s.address, s.is_active, s.created_at,
                  COUNT(po.po_id) as total_orders,
                  COALESCE(SUM(po.total_amount),0) as total_value
           FROM suppliers s
           LEFT JOIN purchase_orders po ON s.supplier_id=po.supplier_id
           GROUP BY s.supplier_id,s.supplier_name,s.contact_name,s.phone,
                    s.email,s.address,s.is_active,s.created_at
           ORDER BY s.supplier_name""",
        fetchall=True
    ) or []
    purchase_orders = query(
        """SELECT po.po_id, s.supplier_name, po.status, po.total_amount,
                  po.expected_date, po.received_date, po.notes, po.created_at,
                  u.full_name as created_by
           FROM purchase_orders po
           JOIN suppliers s ON po.supplier_id=s.supplier_id
           JOIN users u ON po.created_by=u.user_id
           ORDER BY po.created_at DESC LIMIT 50""",
        fetchall=True
    ) or []
    ingredients = query("SELECT ingredient_id, name, unit FROM ingredients WHERE is_active=true ORDER BY name",
                        fetchall=True) or []
    stats = {
        'total': query_scalar("SELECT COUNT(*) FROM suppliers") or 0,
        'active': query_scalar("SELECT COUNT(*) FROM suppliers WHERE is_active=true") or 0,
    }
    return render_template('suppliers.html', suppliers=suppliers, purchase_orders=purchase_orders,
                           ingredients=ingredients, stats=stats)

@suppliers_bp.route('/suppliers/add', methods=['POST'])
@login_required
def add():
    d = request.get_json()
    query("INSERT INTO suppliers (supplier_name,contact_name,phone,email,address) VALUES (%s,%s,%s,%s,%s)",
          (d['supplier_name'],d.get('contact_name',''),d.get('phone',''),d.get('email',''),d.get('address','')), commit=True)
    return jsonify({'success': True})

@suppliers_bp.route('/suppliers/update', methods=['POST'])
@login_required
def update():
    d = request.get_json()
    query("UPDATE suppliers SET supplier_name=%s,contact_name=%s,phone=%s,email=%s,address=%s WHERE supplier_id=%s",
          (d['supplier_name'],d.get('contact_name',''),d.get('phone',''),d.get('email',''),d.get('address',''),d['supplier_id']), commit=True)
    return jsonify({'success': True})

@suppliers_bp.route('/suppliers/toggle', methods=['POST'])
@login_required
def toggle():
    d = request.get_json()
    query("UPDATE suppliers SET is_active=NOT is_active WHERE supplier_id=%s", (d['supplier_id'],), commit=True)
    return jsonify({'success': True})

@suppliers_bp.route('/suppliers/create_po', methods=['POST'])
@login_required
def create_po():
    d = request.get_json()
    items = d.get('items', [])
    total = sum(i['quantity']*i['unit_cost'] for i in items)
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("INSERT INTO purchase_orders (supplier_id,created_by,total_amount,notes,expected_date) VALUES (%s,%s,%s,%s,%s) RETURNING po_id",
                    (d['supplier_id'],session['user_id'],total,d.get('notes',''),d.get('expected_date') or None))
        po_id = cur.fetchone()['po_id']
        for item in items:
            sub = item['quantity']*item['unit_cost']
            cur.execute("INSERT INTO purchase_order_items (po_id,ingredient_id,quantity,unit_cost,subtotal) VALUES (%s,%s,%s,%s,%s)",
                        (po_id,item['ingredient_id'],item['quantity'],item['unit_cost'],sub))
        conn.commit()
        return jsonify({'success': True, 'po_id': po_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@suppliers_bp.route('/suppliers/receive_po', methods=['POST'])
@login_required
def receive_po():
    d = request.get_json()
    po_id = d['po_id']
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT ingredient_id,quantity,unit_cost FROM purchase_order_items WHERE po_id=%s", (po_id,))
        items = cur.fetchall()
        for item in items:
            cur.execute("UPDATE ingredients SET current_stock=current_stock+%s,unit_cost=%s,updated_at=NOW() WHERE ingredient_id=%s",
                        (item['quantity'],item['unit_cost'],item['ingredient_id']))
            cur.execute("INSERT INTO inventory_transactions (ingredient_id,transaction_type,quantity,unit_cost,reference_no,performed_by) VALUES (%s,'Stock In',%s,%s,%s,%s)",
                        (item['ingredient_id'],item['quantity'],item['unit_cost'],f"PO #{po_id}",session['user_id']))
        cur.execute("UPDATE purchase_orders SET status='Received',received_date=NOW() WHERE po_id=%s", (po_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()
