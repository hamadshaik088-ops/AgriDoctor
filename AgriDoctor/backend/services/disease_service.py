from ..ml_models.disease_model.disease_predictor import DiseasePredictor
from .treatment_service import get_treatments_for_disease

disease_predictor = None


def predict_disease_from_image(image_path, expected_crop=None):
    global disease_predictor
    if disease_predictor is None:
        disease_predictor = DiseasePredictor()

    prediction = disease_predictor.predict(image_path, expected_crop=expected_crop)
    if "treatments" not in prediction:
        prediction["treatments"] = get_treatments_for_disease(prediction["crop"], prediction["disease"])
    return prediction
