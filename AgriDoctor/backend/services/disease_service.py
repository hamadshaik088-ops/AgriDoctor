from ..ml_models.disease_model.disease_predictor import DiseasePredictor
from .treatment_service import get_treatments_for_disease

disease_predictor = None


def predict_disease_from_image(image_path, expected_crop=None):
    global disease_predictor
    if disease_predictor is None:
        disease_predictor = DiseasePredictor()

    prediction = disease_predictor.predict(image_path, expected_crop=expected_crop)
    disease_name = prediction.get("disease", "").strip().lower()
    if disease_name not in {"uncertain", "healthy"}:
        catalog_treatments = get_treatments_for_disease(prediction.get("crop", ""), prediction["disease"])
        if catalog_treatments:
            prediction["treatments"] = catalog_treatments
        else:
            prediction.setdefault("treatments", [])
    elif "treatments" not in prediction:
        prediction["treatments"] = []
    return prediction
