from flask import Blueprint, render_template
from app.models import User

public_bp = Blueprint('public', __name__)

@public_bp.route('/drink')
def drink_table():
    users = User.query.all()
    return render_template('drink_table.html', users=users)