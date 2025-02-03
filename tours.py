from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy import or_
from models import db, Tour, User  
from functools import wraps
import logging
from datetime import datetime
import uuid

tours_bp = Blueprint('tours', __name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class ItineraryDaySchema(Schema):
    title = fields.Str(required=True)
    details = fields.Str(required=True)

class TourSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str(required=True)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    duration = fields.Str(required=True)
    difficulty_level = fields.Str(
        required=True,
        validate=validate.OneOf(['Easy', 'Moderate', 'Difficult'])
    )
    max_group_size = fields.Int(required=True, validate=validate.Range(min=1, max=50))
    created_at = fields.DateTime(dump_only=True)
    location = fields.Str(required=True)
    start_point = fields.Str(required=True)
    end_point = fields.Str(required=True)
    is_active = fields.Bool(required=True)
    itinerary = fields.List(fields.Nested(ItineraryDaySchema()), missing=[])

tour_schema = TourSchema()
tours_schema = TourSchema(many=True)

@tours_bp.route('/tours', methods=['POST'])
@jwt_required()
def create_tour():
    try:
        data = tour_schema.load(request.json)
        tour_id = str(uuid.uuid4())
        new_tour = Tour(id=tour_id, **data)
        db.session.add(new_tour)
        db.session.commit()
        logger.info(f"Tour created: {new_tour.name}")
        return jsonify({
            "message": "Tour created successfully",
            "tour": tour_schema.dump(new_tour)
        }), 201
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "An unexpected error occurred"}), 500

@tours_bp.route('/tours', methods=['GET'])
def get_tours():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        name = request.args.get('name')
        difficulty = request.args.get('difficulty')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        query = Tour.query

        if name:
            query = query.filter(Tour.name.ilike(f'%{name}%'))
        if difficulty:
            query = query.filter(Tour.difficulty_level == difficulty)
        if min_price is not None:
            query = query.filter(Tour.price >= min_price)
        if max_price is not None:
            query = query.filter(Tour.price <= max_price)

        if sort_order == 'desc':
            query = query.order_by(getattr(Tour, sort_by).desc())
        else:
            query = query.order_by(getattr(Tour, sort_by).asc())

        paginated_tours = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'tours': tours_schema.dump(paginated_tours.items),
            'total_tours': paginated_tours.total,
            'total_pages': paginated_tours.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Error in get_tours: {str(e)}")
        return jsonify({"message": "An error occurred while fetching tours"}), 500

@tours_bp.route('/tours/search', methods=['GET'])
def search_tours():
    try:
        query_param = request.args.get('query', '')
        tours = Tour.query.filter(
            or_(
                Tour.name.ilike(f'%{query_param}%'),
                Tour.description.ilike(f'%{query_param}%'),
                Tour.difficulty_level.ilike(f'%{query_param}%')
            )
        ).all()
        return jsonify(tours_schema.dump(tours))
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"message": "Search failed"}), 500

@tours_bp.route('/tours/<string:tour_id>', methods=['GET'])
def get_tour(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        return jsonify(tour_schema.dump(tour))
    except Exception as e:
        logger.error(f"Error fetching tour {tour_id}: {str(e)}")
        return jsonify({"message": "An error occurred while fetching the tour"}), 500

@tours_bp.route('/tours/<string:tour_id>', methods=['PUT'])
@jwt_required()
def update_tour(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        data = tour_schema.load(request.json, partial=True)
        for key, value in data.items():
            setattr(tour, key, value)
        db.session.commit()
        logger.info(f"Tour updated: {tour.name}")
        return jsonify({
            "message": "Tour updated successfully",
            "tour": tour_schema.dump(tour)
        })
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update error: {str(e)}")
        return jsonify({"message": "An error occurred while updating the tour"}), 500

@tours_bp.route('/tours/<string:tour_id>', methods=['DELETE'])
@jwt_required()
def delete_tour(tour_id):
    try:
        tour = Tour.query.get_or_404(tour_id)
        db.session.delete(tour)
        db.session.commit()
        logger.info(f"Tour deleted: {tour_id}")
        return jsonify({"message": "Tour deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete error: {str(e)}")
        return jsonify({"message": "An error occurred while deleting the tour"}), 500
