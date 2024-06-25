from werkzeug.security import generate_password_hash, check_password_hash
from main import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy(app)

# models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    dicebear_image = db.Column(db.String(50), nullable=True, default="lorelei")
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    carts = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError("password cannot be RHS")

    @password.setter
    def password(self,password):
        self.passhash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.passhash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(250), nullable=True)

    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    dom = db.Column(db.Date, nullable=True)
    best_before = db.Column(db.Integer, nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    carts = db.relationship('Cart', backref='product', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='product', lazy=True, cascade='all, delete-orphan')


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    mode = db.Column(db.String(20), nullable=False)

    orders = db.relationship('Order', backref='transaction', lazy=True, cascade='all, delete-orphan')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(username='admin', password=password, name='Admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()
