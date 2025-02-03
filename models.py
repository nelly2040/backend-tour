from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import uuid
from sqlalchemy.orm import relationship

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    bookings = relationship('Booking', back_populates='user', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='user', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'phone_number': self.phone_number,
            'is_active': self.is_active
        }

class Tour(db.Model):
    __tablename__ = 'tours'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    max_group_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    location = db.Column(db.String(100), nullable=False)
    start_point = db.Column(db.String(100), nullable=False)
    end_point = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    bookings = relationship('Booking', back_populates='tour', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='tour', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration': self.duration,
            'difficulty_level': self.difficulty_level,
            'max_group_size': self.max_group_size,
            'location': self.location,
            'start_point': self.start_point,
            'end_point': self.end_point,
            'is_active': self.is_active
        }

class TourType(db.Model):
    __tablename__ = 'tourtypes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = relationship('Booking', back_populates='tour_type', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price
        }

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    tour_id = db.Column(db.String(36), db.ForeignKey('tours.id'), nullable=False)
    tour_type_id = db.Column(db.String(36), db.ForeignKey('tourtypes.id'), nullable=False)  # ForeignKey for TourType
    
    safari_start_date = db.Column(db.DateTime, nullable=False)
    safari_end_date = db.Column(db.DateTime, nullable=False)
    number_of_participants = db.Column(db.Integer, nullable=False, default=1)
    special_requests = db.Column(db.Text, nullable=True)
    
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='bookings')
    tour = relationship('Tour', back_populates='bookings')
    tour_type = relationship('TourType', back_populates='bookings')  # Correct relationship for TourType

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tour_id': self.tour_id,
            'tour_type_id': self.tour_type_id,
            'safari_start_date': self.safari_start_date.isoformat(),
            'safari_end_date': self.safari_end_date.isoformat(),
            'number_of_participants': self.number_of_participants,
            'special_requests': self.special_requests,
            'status': self.status,
            'total_price': self.total_price
        }

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    tour_id = db.Column(db.String(36), db.ForeignKey('tours.id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='reviews')
    tour = relationship('Tour', back_populates='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tour_id': self.tour_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }
