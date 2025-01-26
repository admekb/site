from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drink_name = db.Column(db.String(50), nullable=False)
    volume = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref=db.backref('drinks', lazy=True))