from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from web.db import query, query_scalar
from web.routes.dashboard_routes import login_required

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu')
@login_required
def index():
    categories = query("SELECT * FROM menu_categories ORDER BY category_name", fetchall=True) or []
    items = query(
        """SELECT mi.item_id, mi.item_name, mc.category_name, mc.category_id,
                  mi.price, mi.cost_price, mi.description, mi.is_available
           FROM menu_items mi JOIN menu_categories mc ON mi.category_id=mc.category_id
           ORDER BY mc.category_name, mi.item_name""",
        fetchall=True
    ) or []
    return render_template('menu.html', categories=categories, items=items)

@menu_bp.route('/menu/add_item', methods=['POST'])
@login_required
def add_item():
    data = request.get_json()
    query(
        """INSERT INTO menu_items (category_id, item_name, description, price, cost_price)
           VALUES (%s, %s, %s, %s, %s)""",
        (data['category_id'], data['item_name'], data.get('description',''),
         data['price'], data.get('cost_price', 0)),
        commit=True
    )
    return jsonify({'success': True})

@menu_bp.route('/menu/update_item', methods=['POST'])
@login_required
def update_item():
    data = request.get_json()
    query(
        """UPDATE menu_items SET category_id=%s, item_name=%s, description=%s,
           price=%s, cost_price=%s, updated_at=NOW()
           WHERE item_id=%s""",
        (data['category_id'], data['item_name'], data.get('description',''),
         data['price'], data.get('cost_price', 0), data['item_id']),
        commit=True
    )
    return jsonify({'success': True})

@menu_bp.route('/menu/toggle_item', methods=['POST'])
@login_required
def toggle_item():
    data = request.get_json()
    query("UPDATE menu_items SET is_available=NOT is_available WHERE item_id=%s",
          (data['item_id'],), commit=True)
    return jsonify({'success': True})

@menu_bp.route('/menu/delete_item', methods=['POST'])
@login_required
def delete_item():
    data = request.get_json()
    query("DELETE FROM menu_items WHERE item_id=%s", (data['item_id'],), commit=True)
    return jsonify({'success': True})

@menu_bp.route('/menu/add_category', methods=['POST'])
@login_required
def add_category():
    data = request.get_json()
    query("INSERT INTO menu_categories (category_name, description) VALUES (%s, %s)",
          (data['category_name'], data.get('description','')), commit=True)
    return jsonify({'success': True})

@menu_bp.route('/menu/delete_category', methods=['POST'])
@login_required
def delete_category():
    data = request.get_json()
    query("DELETE FROM menu_categories WHERE category_id=%s", (data['category_id'],), commit=True)
    return jsonify({'success': True})
