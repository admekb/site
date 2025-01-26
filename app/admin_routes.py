import os
from flask import Blueprint, request, render_template, redirect, url_for, session
from app.models import db, People, Drink

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
        
        # Сообщение об ошибке
        return render_template('login.html', error="Неверный логин или пароль"), 401
    
    return render_template('login.html')

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    
    # Получаем список всех людей из базы данных
    people = People.query.all()
    
    # Делаем сбор данных о напитках для каждого человека
    return render_template('dashboard.html', people=people)
