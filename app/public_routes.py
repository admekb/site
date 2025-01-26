import os
from flask import Blueprint, render_template
from app.models import People  # Заменили User на People

public_bp = Blueprint('public', __name__, url_prefix='/')

@public_bp.route('/')
def home():
    return render_template('index.html')

# Вы можете добавить другие маршруты, если необходимо
