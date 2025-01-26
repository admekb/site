import os
from flask import Flask
from app.models import db
from app.admin_routes import admin_bp
from app.public_routes import public_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")
    
    # Конфигурация SQLAlchemy на основе переменных окружения
    db_username = os.getenv("DB_USERNAME", "default_user")
    db_password = os.getenv("DB_PASSWORD", "default_password")
    db_name = os.getenv("DB_NAME", "default_db")
    db_host = "db"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_username}:{db_password}@{db_host}:5432/{db_name}"
    db.init_app(app)

    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)

    return app
