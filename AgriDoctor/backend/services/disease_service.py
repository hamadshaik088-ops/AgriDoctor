from ..ml_models.disease_model.disease_predictor import DiseasePredictor
from .treatment_service import get_treatments_for_disease

disease_predictor = DiseasePredictor()


def predict_disease_from_image(image_path):
    prediction = disease_predictor.predict(image_path)
    if "treatments" not in prediction:
        prediction["treatments"] = get_treatments_for_disease(prediction["crop"], prediction["disease"])
    return prediction
