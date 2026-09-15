from flask import Blueprint, jsonify
from ..utils.auth import admin_required
from ..models.user import User
from ..models.farmer import Farmer
from ..models.disease_prediction import DiseasePrediction
from ..models.disease import Disease
from ..models.treatment import Treatment

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    total_farmers = User.query.count()
    total_scans = DiseasePrediction.query.count()
    total_diseases = Disease.query.count()
    total_treatments = Treatment.query.count()
    return jsonify({
        "stats": {
            "total_farmers": total_farmers,
            "total_scans": total_scans,
            "total_disease_predictions": total_scans,
            "most_detected_disease": "Early Blight",
            "most_recommended_crop": "Rice",
            "recent_activity": [{"type": "new_scan", "detail": "Tomato disease scan completed"}],
            "total_diseases": total_diseases,
            "total_treatments": total_treatments
        }
    })


@admin_bp.route("/farmers", methods=["GET"])
@admin_required
def farmers():
    rows = Farmer.query.join(User).order_by(User.created_at.desc()).all()
    return jsonify({"farmers": [{
        "id": farmer.id,
        "user_id": farmer.user.id,
        "name": farmer.user.name,
        "email": farmer.user.email,
        "mobile_number": farmer.user.mobile_number,
        "role": farmer.user.role,
        "state": farmer.user.state,
        "district": farmer.district or farmer.user.district,
        "village": farmer.village or farmer.user.village,
        "farm_area": farmer.user.farm_area,
        "latitude": farmer.latitude,
        "longitude": farmer.longitude,
        "created_at": farmer.created_at.isoformat() if farmer.created_at else None,
    } for farmer in rows]})


@admin_bp.route("/diseases", methods=["GET"])
@admin_required
def diseases():
    rows = Disease.query.all()
    return jsonify({"diseases": [{"id": d.id, "crop": d.crop, "disease_name": d.disease_name, "severity": d.severity} for d in rows]})


@admin_bp.route("/diseases", methods=["POST"])
@admin_required
def create_disease():
    return jsonify({"message": "Disease record created (demo mode)"})


@admin_bp.route("/diseases/<int:disease_id>", methods=["PUT"])
@admin_required
def update_disease(disease_id):
    return jsonify({"message": "Disease record updated (demo mode)"})


@admin_bp.route("/diseases/<int:disease_id>", methods=["DELETE"])
@admin_required
def delete_disease(disease_id):
    return jsonify({"message": "Disease record deleted (demo mode)"})


@admin_bp.route("/treatments", methods=["GET"])
@admin_required
def treatments():
    rows = Treatment.query.all()
    return jsonify({"treatments": [{"id": t.id, "crop": t.crop, "disease": t.disease, "product_name": t.product_name} for t in rows]})


@admin_bp.route("/treatments", methods=["POST"])
@admin_required
def create_treatment():
    return jsonify({"message": "Treatment record created (demo mode)"})


@admin_bp.route("/treatments/<int:treatment_id>", methods=["PUT"])
@admin_required
def update_treatment(treatment_id):
    return jsonify({"message": "Treatment record updated (demo mode)"})


@admin_bp.route("/treatments/<int:treatment_id>", methods=["DELETE"])
@admin_required
def delete_treatment(treatment_id):
    return jsonify({"message": "Treatment record deleted (demo mode)"})
