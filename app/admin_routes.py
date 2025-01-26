import os
from flask import Blueprint, request, render_template, redirect, url_for, session
from app.models import db, User, Drink

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Получение данных администратора из переменных окружения
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "default_admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "default_password")

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin.dashboard'))
        return "Неверный логин или пароль", 401
    return render_template('login.html')

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    users = User.query.all()
    return render_template('dashboard.html', users=users)
