from flask import Blueprint, render_template, request, session, redirect, url_for
from web.auth import authenticate_user, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        ip = request.remote_addr or ''
        user, err = authenticate_user(username, password, ip_address=ip)
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['branch_id'] = user['branch_id']
            session['session_id'] = user['session_id']
            return redirect(url_for('dashboard.index'))
        error = err
    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def logout():
    logout_user(session.get('session_id'))
    session.clear()
    return redirect(url_for('auth.login'))
