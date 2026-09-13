from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..services.weather_service import get_weather_current, get_weather_forecast

weather_bp = Blueprint("weather", __name__)


def coordinates_from_request():
    try:
        return float(request.args.get("lat", 17.3850)), float(request.args.get("lon", 78.4867))
    except (TypeError, ValueError):
        return None


@weather_bp.route("/current", methods=["GET"])
@jwt_required()
def current():
    coordinates = coordinates_from_request()
    if coordinates is None:
        return jsonify({"error": "lat and lon must be valid numbers"}), 400
    lat, lon = coordinates
    return jsonify(get_weather_current(lat, lon))


@weather_bp.route("/forecast", methods=["GET"])
@jwt_required()
def forecast():
    coordinates = coordinates_from_request()
    if coordinates is None:
        return jsonify({"error": "lat and lon must be valid numbers"}), 400
    lat, lon = coordinates
    return jsonify(get_weather_forecast(lat, lon))
