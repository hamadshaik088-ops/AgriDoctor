from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..database.db import db
from ..models.user import User
from ..models.farmer import Farmer
from ..models.disease_prediction import DiseasePrediction
from ..services.disease_service import predict_disease_from_image
from ..utils.image_processing import save_uploaded_image

disease_bp = Blueprint("disease", __name__)


@disease_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    file = request.files["image"]
    if not file.filename:
        return jsonify({"error": "Empty image file"}), 400
    crop = request.form.get("crop", "").strip()
    if not crop:
        return jsonify({"error": "Select the crop before scanning the image."}), 400
    try:
        filepath = save_uploaded_image(file)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        prediction = predict_disease_from_image(filepath)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    user = User.query.get(get_jwt_identity())
    farmer = user.farmer_profile
    if not farmer:
        farmer = Farmer(user_id=user.id)
        db.session.add(farmer)
        db.session.flush()

    record = DiseasePrediction(
        farmer_id=farmer.id,
        crop_name=prediction.get("crop"),
        disease_name=prediction.get("disease"),
        confidence=float(prediction.get("confidence", "0").replace("%", "")) / 100 if isinstance(prediction.get("confidence"), str) else float(prediction.get("confidence", 0)),
        severity=prediction.get("severity", "Moderate"),
        symptoms=prediction.get("symptoms"),
        management=prediction.get("management"),
        treatment=prediction.get("treatment"),
        risk_level=prediction.get("weather_risk", "MEDIUM"),
        image_path=filepath
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({"message": "Prediction generated successfully", "result": prediction, "record_id": record.id})


@disease_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user = User.query.get(get_jwt_identity())
    if not user or not user.farmer_profile:
        return jsonify({"history": []})
    records = DiseasePrediction.query.filter_by(farmer_id=user.farmer_profile.id).order_by(DiseasePrediction.created_at.desc()).all()
    return jsonify({"history": [{
        "id": r.id,
        "crop": r.crop_name,
        "disease": r.disease_name,
        "confidence": f"{r.confidence * 100:.1f}%",
        "severity": r.severity,
        "created_at": r.created_at.isoformat()
    } for r in records]})


@disease_bp.route("/<int:prediction_id>", methods=["GET"])
@jwt_required()
def detail(prediction_id):
    record = DiseasePrediction.query.get_or_404(prediction_id)
    return jsonify({
        "id": record.id,
        "crop_name": record.crop_name,
        "disease_name": record.disease_name,
        "confidence": f"{record.confidence * 100:.1f}%",
        "severity": record.severity,
        "symptoms": record.symptoms,
        "management": record.management,
        "treatment": record.treatment,
        "risk_level": record.risk_level
    })
