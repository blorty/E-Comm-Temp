#models.py

import os
from cryptography.fernet import Fernet
from . import db, bcrypt
from flask_login import UserMixin

DB_ENCRYPTION_KEY = os.environ.get('DB_ENCRYPTION_KEY')

def encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.decrypt(data.encode()).decode()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    user_orders = db.relationship('Order', back_populates='user', lazy='dynamic')
    user_cart = db.relationship('Cart', back_populates='user', uselist=False, lazy='joined')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    _address_line_1 = db.Column(db.String, nullable=True)
    _address_line_2 = db.Column(db.String, nullable=True)
    _city = db.Column(db.String, nullable=True)
    _state = db.Column(db.String, nullable=True)
    _zip_code = db.Column(db.String, nullable=True)

    is_default = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship('User', backref='addresses', lazy=True)

    @property
    def address_line_1(self):
        return decrypt_data(self._address_line_1, DB_ENCRYPTION_KEY)

    @address_line_1.setter
    def address_line_1(self, value):
        self._address_line_1 = encrypt_data(value, DB_ENCRYPTION_KEY)
        
    @property
    def address_line_2(self):
        return decrypt_data(self._address_line_2, DB_ENCRYPTION_KEY)
    
    @address_line_2.setter
    def address_line_2(self, value):
        self._address_line_2 = encrypt_data(value, DB_ENCRYPTION_KEY)
        
    @property
    def city(self):
        return decrypt_data(self._city, DB_ENCRYPTION_KEY)
    
    @city.setter
    def city(self, value):
        self._city = encrypt_data(value, DB_ENCRYPTION_KEY)
        
    @property
    def state(self):
        return decrypt_data(self._state, DB_ENCRYPTION_KEY)
    
    @state.setter
    def state(self, value):
        self._state = encrypt_data(value, DB_ENCRYPTION_KEY)
        
    @property
    def zip_code(self):
        return decrypt_data(self._zip_code, DB_ENCRYPTION_KEY)
    
    @zip_code.setter
    def zip_code(self, value):
        self._zip_code = encrypt_data(value, DB_ENCRYPTION_KEY)
        
    def encrypt_field(self, value):
        return AddressEncryptionService.encrypt_data(value, DB_ENCRYPTION_KEY)
    
    def decrypt_field(self, value):
        return AddressEncryptionService.decrypt_data(value, DB_ENCRYPTION_KEY)
    
    def __repr__(self):
        return f'<Address {self.id}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(128), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(128), nullable=False)
    
    cart_items = db.relationship('CartItem', back_populates='product', lazy=True)
    order_items = db.relationship('OrderItem', back_populates='product', lazy=True)


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image': self.image,
            'stock': self.stock,
            'category': self.category
        }

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(128), nullable=False)
    total = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', back_populates='user_orders')
    order_items = db.relationship('OrderItem', back_populates='order', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'total': self.total,
            'date_created': self.date_created.strftime('%Y-%m-%d %H:%M:%S') if self.date_created else None
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', back_populates='order_items')
    order = db.relationship('Order', back_populates='order_items')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'date_created': self.date_created.strftime('%Y-%m-%d %H:%M:%S') if self.date_created else None
        }

class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='user_cart')
    cart_items = db.relationship('CartItem', back_populates='cart', lazy='dynamic')

    def calculate_total(self):
        return sum(item.quantity * item.price for item in self.cart_items)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total': self.calculate_total()
        }

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    cart = db.relationship('Cart', back_populates='cart_items')
    product = db.relationship('Product', back_populates='cart_items')

    def update_price(self):
        self.price = self.product.price 

    def to_dict(self):
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }