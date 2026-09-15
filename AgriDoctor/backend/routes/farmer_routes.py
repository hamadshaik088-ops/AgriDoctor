from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..database.db import db
from ..models.user import User
from ..models.farmer import Farmer
from ..models.farm import Farm
from ..services.notification_service import create_notification

farmer_bp = Blueprint("farmer", __name__)


@farmer_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "state": user.state,
        "district": user.district,
        "village": user.village,
        "farm_area": user.farm_area
    })


@farmer_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user = User.query.get(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    if data.get("name"):
        user.name = data["name"]
    if data.get("email"):
        user.email = data["email"]
    if data.get("state"):
        user.state = data["state"]
    if data.get("district"):
        user.district = data["district"]
        if user.farmer_profile:
            user.farmer_profile.district = data["district"]
    if data.get("village"):
        user.village = data["village"]
        if user.farmer_profile:
            user.farmer_profile.village = data["village"]
    if data.get("farm_area"):
        user.farm_area = float(data["farm_area"])
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"})


@farmer_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user = User.query.get(get_jwt_identity())
    return jsonify({
        "welcome": f"Welcome {user.name} 👨‍🌾",
        "weather": None,
        "disease_risk": None,
        "quick_actions": ["Scan Disease", "Soil Analysis", "Recommend Crop", "Weather"],
        "notifications": None,
        "recent_scan": "Tomato leaf scan - 2 days ago",
        "recent_recommendation": "Rice rotation recommended"
    })


@farmer_bp.route("/details", methods=["GET"])
@jwt_required()
def details():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    farmer = user.farmer_profile
    return jsonify({
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile_number": user.mobile_number,
            "role": user.role,
            "state": user.state,
            "district": user.district,
            "village": user.village,
            "farm_area": user.farm_area,
        },
        "farmer": {
            "id": farmer.id,
            "district": farmer.district,
            "village": farmer.village,
            "latitude": farmer.latitude,
            "longitude": farmer.longitude,
        } if farmer else None,
        "farms": [{
            "id": farm.id,
            "farm_name": farm.farm_name,
            "location": farm.location,
            "state": farm.state,
            "district": farm.district,
            "village": farm.village,
            "area": farm.area,
            "soil_type": farm.soil_type,
            "irrigation_type": farm.irrigation_type,
            "current_crop": farm.current_crop,
        } for farm in (farmer.farms if farmer else [])],
    })


@farmer_bp.route("/farm", methods=["POST"])
@jwt_required()
def create_farm():
    user = User.query.get(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    farmer = user.farmer_profile or Farmer(user_id=user.id)
    if not user.farmer_profile:
        db.session.add(farmer)
        db.session.flush()
    farm = Farm(
        farmer_id=farmer.id,
        farm_name=data.get("farm_name", "My Farm"),
        location=data.get("location", "Farm site"),
        state=data.get("state", user.state),
        district=data.get("district", user.district),
        village=data.get("village", user.village),
        area=data.get("area", user.farm_area),
        soil_type=data.get("soil_type", "Loam"),
        irrigation_type=data.get("irrigation_type", "Drip"),
        current_crop=data.get("current_crop", "Tomato"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude")
    )
    db.session.add(farm)
    db.session.commit()
    create_notification(farmer, "Farm profile created", "Your farm profile was saved successfully.", "info")
    return jsonify({"message": "Farm saved", "farm": farm.__dict__}), 201


@farmer_bp.route("/farm", methods=["GET"])
@jwt_required()
def get_farm():
    user = User.query.get(get_jwt_identity())
    farmer = user.farmer_profile
    if not farmer or not farmer.farms:
        return jsonify({"farm": None})
    farm = farmer.farms[0]
    return jsonify({
        "farm": {
            "id": farm.id,
            "farm_name": farm.farm_name,
            "location": farm.location,
            "state": farm.state,
            "district": farm.district,
            "village": farm.village,
            "area": farm.area,
            "soil_type": farm.soil_type,
            "irrigation_type": farm.irrigation_type,
            "current_crop": farm.current_crop
        }
    })


@farmer_bp.route("/farm", methods=["PUT"])
@jwt_required()
def update_farm():
    user = User.query.get(get_jwt_identity())
    farmer = user.farmer_profile
    if not farmer or not farmer.farms:
        return jsonify({"error": "No farm record found"}), 404
    data = request.get_json(silent=True) or {}
    farm = farmer.farms[0]
    for key in ["farm_name", "location", "state", "district", "village", "area", "soil_type", "irrigation_type", "current_crop"]:
        if key in data:
            setattr(farm, key, data[key])
    db.session.commit()
    return jsonify({"message": "Farm updated", "farm": farm.__dict__})
