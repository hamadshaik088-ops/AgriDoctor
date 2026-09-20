from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
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
    try:
        filepath = save_uploaded_image(file)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        expected_crop = request.form.get("expected_crop", "").strip() or None
        prediction = predict_disease_from_image(filepath, expected_crop=expected_crop)
    except (OSError, ValueError) as exc:
        return jsonify({"error": "The uploaded file is not a valid readable image.", "message": str(exc)}), 400
    except RuntimeError as exc:
        if str(exc).startswith("CROP_MISMATCH:"):
            return jsonify({"error": str(exc).removeprefix("CROP_MISMATCH: ").strip(), "code": "CROP_MISMATCH"}), 422
        error_code = "MODEL_NOT_CONFIGURED" if "pretrained disease model is unavailable" in str(exc) else "MODEL_INFERENCE_FAILED"
        return jsonify({
            "error": str(exc),
            "code": error_code,
            "message": "Automatic crop and disease prediction is unavailable for this image."
        }), 503
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 401
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
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            "error": "The diagnosis was generated but could not be saved.",
            "message": "Check the database schema and connection, then try again.",
        }), 503

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
