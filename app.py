import os
from flask import Flask, redirect, url_for

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.secret_key = os.environ.get('SECRET_KEY', 'itqansoft-restaurant-2024-secret')

from web.routes.auth_routes import auth_bp
from web.routes.dashboard_routes import dashboard_bp
from web.routes.pos_routes import pos_bp
from web.routes.menu_routes import menu_bp
from web.routes.inventory_routes import inventory_bp
from web.routes.kitchen_routes import kitchen_bp
from web.routes.customers_routes import customers_bp
from web.routes.reports_routes import reports_bp
from web.routes.reservations_routes import reservations_bp
from web.routes.suppliers_routes import suppliers_bp
from web.routes.admin_routes import admin_bp
from web.routes.branches_routes import branches_bp
from web.routes.sales_routes import sales_bp
from web.routes.license_routes import license_bp
from web.routes.print_routes import print_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(pos_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(kitchen_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(reservations_bp)
app.register_blueprint(suppliers_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(branches_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(license_bp)
app.register_blueprint(print_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
