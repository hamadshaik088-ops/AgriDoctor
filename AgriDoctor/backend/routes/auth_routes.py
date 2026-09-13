from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from ..database.db import db
from ..models.user import User
from ..models.farmer import Farmer
from ..utils.validation import validate_email, error_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    mobile_number = str(data.get("mobile_number", "")).strip()
    required = ["name", "mobile_number", "email", "password", "state", "district", "village", "farm_area"]
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}")
    if not validate_email(email):
        return error_response("Invalid email format")
    if len(str(data["password"])) < 8:
        return error_response("Password must be at least 8 characters")
    try:
        farm_area = float(data["farm_area"])
    except (TypeError, ValueError):
        return error_response("Farm area must be a valid number")
    if farm_area < 0:
        return error_response("Farm area cannot be negative")
    if User.query.filter_by(email=email).first():
        return error_response("Email already registered", 409)
    if User.query.filter_by(mobile_number=mobile_number).first():
        return error_response("Mobile number already registered", 409)

    user = User(
        name=data["name"],
        email=email,
        mobile_number=mobile_number,
        state=data.get("state"),
        district=data.get("district"),
        village=data.get("village"),
        farm_area=farm_area
    )
    user.set_password(data["password"])
    try:
        db.session.add(user)
        db.session.flush()
        farmer = Farmer(user_id=user.id, district=data.get("district"), village=data.get("village"))
        db.session.add(farmer)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response("Email or mobile number is already registered", 409)
    except SQLAlchemyError:
        db.session.rollback()
        return error_response("Unable to save registration. Please try again.", 503)

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Registration successful", "token": token, "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role}}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password")
    if not email or not password:
        return error_response("Email and password are required")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response("Invalid email or password", 401)
    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Login successful", "token": token, "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role}})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    return jsonify({"id": user.id, "name": user.name, "email": user.email, "role": user.role, "state": user.state, "district": user.district, "village": user.village, "farm_area": user.farm_area})
