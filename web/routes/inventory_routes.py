from flask import Blueprint, render_template, request, session, jsonify
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
@login_required
def index():
    ingredients = query(
        """SELECT i.ingredient_id, i.name, i.unit, i.current_stock,
                  i.minimum_stock, i.reorder_level, i.unit_cost, i.is_active,
                  COALESCE(s.supplier_name, '--') as supplier_name,
                  CASE WHEN i.current_stock<=0 THEN 'Out of Stock'
                       WHEN i.current_stock<=i.minimum_stock THEN 'Low Stock'
                       WHEN i.current_stock<=i.reorder_level THEN 'Reorder Soon'
                       ELSE 'In Stock' END as stock_status
           FROM ingredients i
           LEFT JOIN suppliers s ON i.supplier_id=s.supplier_id
           WHERE i.is_active=true ORDER BY i.name""",
        fetchall=True
    ) or []
    suppliers = query("SELECT supplier_id, supplier_name FROM suppliers WHERE is_active=true ORDER BY supplier_name",
                      fetchall=True) or []
    stats = {
        'total': query_scalar("SELECT COUNT(*) FROM ingredients WHERE is_active=true") or 0,
        'out_of_stock': query_scalar("SELECT COUNT(*) FROM ingredients WHERE current_stock<=0 AND is_active=true") or 0,
        'low_stock': query_scalar("SELECT COUNT(*) FROM ingredients WHERE current_stock>0 AND current_stock<=minimum_stock AND is_active=true") or 0,
        'total_value': float(query_scalar("SELECT COALESCE(SUM(current_stock*unit_cost),0) FROM ingredients WHERE is_active=true") or 0),
    }
    return render_template('inventory.html', ingredients=ingredients, suppliers=suppliers, stats=stats)

@inventory_bp.route('/inventory/add', methods=['POST'])
@login_required
def add():
    d = request.get_json()
    query("INSERT INTO ingredients (name,unit,minimum_stock,reorder_level,unit_cost,supplier_id) VALUES (%s,%s,%s,%s,%s,%s)",
          (d['name'],d['unit'],d.get('minimum_stock',0),d.get('reorder_level',0),d.get('unit_cost',0),d.get('supplier_id') or None),
          commit=True)
    return jsonify({'success': True})

@inventory_bp.route('/inventory/update', methods=['POST'])
@login_required
def update():
    d = request.get_json()
    query("UPDATE ingredients SET name=%s,unit=%s,minimum_stock=%s,reorder_level=%s,unit_cost=%s,supplier_id=%s,updated_at=NOW() WHERE ingredient_id=%s",
          (d['name'],d['unit'],d.get('minimum_stock',0),d.get('reorder_level',0),d.get('unit_cost',0),d.get('supplier_id') or None,d['ingredient_id']),
          commit=True)
    return jsonify({'success': True})

@inventory_bp.route('/inventory/stock_in', methods=['POST'])
@login_required
def stock_in():
    d = request.get_json()
    query("UPDATE ingredients SET current_stock=current_stock+%s, unit_cost=%s, updated_at=NOW() WHERE ingredient_id=%s",
          (d['quantity'],d.get('unit_cost',0),d['ingredient_id']), commit=True)
    query("INSERT INTO inventory_transactions (ingredient_id,transaction_type,quantity,unit_cost,reference_no,notes,performed_by) VALUES (%s,'Stock In',%s,%s,%s,%s,%s)",
          (d['ingredient_id'],d['quantity'],d.get('unit_cost',0),d.get('reference_no',''),d.get('notes',''),session['user_id']),
          commit=True)
    return jsonify({'success': True})

@inventory_bp.route('/inventory/stock_out', methods=['POST'])
@login_required
def stock_out():
    d = request.get_json()
    query("UPDATE ingredients SET current_stock=current_stock-%s, updated_at=NOW() WHERE ingredient_id=%s",
          (d['quantity'],d['ingredient_id']), commit=True)
    query("INSERT INTO inventory_transactions (ingredient_id,transaction_type,quantity,notes,performed_by) VALUES (%s,'Stock Out',%s,%s,%s)",
          (d['ingredient_id'],d['quantity'],d.get('notes',''),session['user_id']), commit=True)
    return jsonify({'success': True})

@inventory_bp.route('/inventory/delete', methods=['POST'])
@login_required
def delete():
    d = request.get_json()
    query("UPDATE ingredients SET is_active=false WHERE ingredient_id=%s", (d['ingredient_id'],), commit=True)
    return jsonify({'success': True})

@inventory_bp.route('/inventory/transactions')
@login_required
def transactions():
    txns = query(
        """SELECT t.transaction_id, i.name, t.transaction_type, t.quantity, i.unit,
                  t.unit_cost, t.reference_no, t.notes, u.full_name, t.created_at
           FROM inventory_transactions t
           JOIN ingredients i ON t.ingredient_id=i.ingredient_id
           JOIN users u ON t.performed_by=u.user_id
           ORDER BY t.created_at DESC LIMIT 100""",
        fetchall=True
    ) or []
    return render_template('inventory_transactions.html', transactions=txns)
