from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config  
from models import db, bcrypt, Booking, User, Tour
from auth import auth_bp
from tours import tours_bp
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_migrate import Migrate
from datetime import datetime


def get_user_id_from_email(email):
    user = User.query.filter_by(email=email).first()
    return user.id if user else None


def calculate_total_price(tour_id, number_of_participants, start_date, end_date):
    tour = Tour.query.filter_by(id=tour_id).first()
    if not tour:
        return 0

    days = (end_date - start_date).days
    if days <= 0:
        return 0

    return tour.price * number_of_participants * days


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.logger.info("Starting Flask application...")

    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get(
        'SQLALCHEMY_DATABASE_URI', 'sqlite:///tour_company.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)
    bcrypt.init_app(app)
    JWTManager(app)
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tours_bp, url_prefix='/api')

    @app.route('/')
    def home():
        return "Hello, Flask is running!"
        

    @app.route('/api/bookings', methods=['POST'])
    def book_tour():
        try:
            data = request.json
            app.logger.info(f"Received Booking Data: {data}")

            user_id = data.get('user_id')
            tour_id = data.get('tour_id')
            safari_start_date = data.get('safari_start_date')
            safari_end_date = data.get('safari_end_date')
            number_of_participants = data.get('number_of_participants', 1)
            special_requests = data.get('special_requests', '')

            if not all([user_id, tour_id, safari_start_date, safari_end_date]):
                return jsonify({"error": "Missing required fields"}), 400

            try:
                safari_start_date = datetime.strptime(safari_start_date, "%Y-%m-%d")
                safari_end_date = datetime.strptime(safari_end_date, "%Y-%m-%d")
            except ValueError as e:
                app.logger.error(f"Date format error: {e}")
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

            if safari_start_date >= safari_end_date:
                return jsonify({"error": "Safari start date must be before end date"}), 400

            existing_booking = Booking.query.filter_by(user_id=user_id, tour_id=tour_id).first()
            if existing_booking:
                return jsonify({"error": "User already has a booking for this tour"}), 400

            tour = Tour.query.get(tour_id)
            if not tour:
                return jsonify({"error": "Tour not found"}), 404

            total_price = calculate_total_price(tour_id, number_of_participants, safari_start_date, safari_end_date)
            app.logger.info(f"Total Price Calculated: {total_price}")

            new_booking = Booking(
                user_id=user_id,
                tour_type_id=tour_id,
                safari_start_date=safari_start_date,
                safari_end_date=safari_end_date,
                number_of_participants=number_of_participants,
                special_requests=special_requests,
                total_price=total_price,
                status='Confirmed'
            )

            db.session.add(new_booking)
            db.session.commit()

            return jsonify({"message": "Booking successful", "booking": new_booking.to_dict()}), 201

        except Exception as e:
            app.logger.error(f"Server Error: {e}")
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "The requested resource could not be found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": "Something went wrong on the server"}), 500

    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/tour_company.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Tour Company Backend startup')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
