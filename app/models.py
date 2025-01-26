from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Связь с таблицей Drink
    drinks = db.relationship('Drink', backref='owner', lazy=True)

class Drink(db.Model):
    __tablename__ = 'drink'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Float, nullable=False)
    
    # Внешний ключ, указывающий на владельца напитка (пользователя)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)

    def __repr__(self):
        return f"<Drink(name={self.name}, volume={self.volume}, people_id={self.people_id})>"
