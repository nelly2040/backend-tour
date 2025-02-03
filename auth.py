from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User, bcrypt
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy import or_
import logging

auth_bp = Blueprint('auth', __name__)

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    age = fields.Int(required=True, validate=validate.Range(min=18, max=120))
    phone_number = fields.Str(required=False, allow_none=True)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = user_registration_schema.load(request.json)
    except ValidationError as err:
        logger.error(f"Validation error during registration: {err.messages}")
        return jsonify({"errors": err.messages}), 400

    existing_user = User.query.filter(
        or_(User.email == data['email'], User.username == data['username'])
    ).first()
    
    if existing_user:
        logger.info(f"Registration attempt for existing user: {data['email']}")
        return jsonify({"message": "User already exists"}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data['age'],
        phone_number=data.get('phone_number', '')
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User registered successfully: {new_user.email}")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "An error occurred during registration"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = user_login_schema.load(request.json)
    except ValidationError as err:
        logger.error(f"Validation error during login: {err.messages}")
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        logger.info(f"User logged in: {user.email}")
        return jsonify({
            "access_token": access_token,
            "user_id": user.id
        }), 200
    else:
        logger.info(f"Invalid login attempt for email: {data['email']}")
        return jsonify({"message": "Invalid credentials"}), 401
