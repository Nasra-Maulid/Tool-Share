from config import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
import datetime

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    tools = db.relationship('Tool', backref='owner', lazy=True)
    bookings = db.relationship('Booking', backref='borrower', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    
    # Serialization rules
    serialize_rules = ('-tools.owner', '-bookings.borrower', '-reviews.reviewer')
    
    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError("Invalid email address")
        return email

class Tool(db.Model, SerializerMixin):
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    daily_rate = db.Column(db.Float, nullable=False)
    deposit = db.Column(db.Float, default=0)
    available = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='tool', lazy=True)
    reviews = db.relationship('Review', backref='tool', lazy=True)
    
    # Serialization rules
    serialize_rules = ('-owner.tools', '-bookings.tool', '-reviews.tool')

class Booking(db.Model, SerializerMixin):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected, completed
    total_price = db.Column(db.Float)
    
    # Foreign keys
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Serialization rules
    serialize_rules = ('-tool.bookings', '-borrower.bookings')

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Foreign keys
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    @validates('rating')
    def validate_rating(self, key, rating):
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return rating
    
    # Serialization rules
    serialize_rules = ('-tool.reviews', '-reviewer.reviews')