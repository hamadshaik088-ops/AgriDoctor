import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image
import torch

from ml_models.disease_model.disease_predictor import DiseasePredictor


class DummyModel:
    class Config:
        id2label = {0: "Apple___healthy", 1: "Tomato___Early_blight"}
        num_labels = 2

    config = Config()

    def __call__(self, **inputs):
        return type("Output", (), {"logits": torch.tensor([[0.05, 0.95]])})()


class DummyProcessor:
    def __call__(self, images, return_tensors):
        self.last_image = images
        return {"pixel_values": torch.zeros((1, 3, 224, 224))}


class DiseasePredictorPreprocessingTest(unittest.TestCase):
    def test_plant_id_returns_healthy_when_no_disease_suggestion_exists(self):
        class Response:
            status_code = 200

            def json(self):
                return {"result": {
                    "classification": {"suggestions": [{"name": "Tomato", "probability": 0.92}]},
                    "disease": {"suggestions": []},
                    "is_healthy": {"binary": True, "probability": 0.88},
                }}

        predictor = DiseasePredictor.__new__(DiseasePredictor)
        predictor.plant_id_api_key = "test-key"
        predictor.plant_id_api_url = "https://api.plant.id/v3/identification"
        predictor.plant_id_health = "all"
        predictor.provider = "plant_id"

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "leaf.jpg"
            image_path.write_bytes(b"image")
            with patch("requests.post", return_value=Response()):
                result = predictor._plant_id_prediction(str(image_path))

        self.assertEqual(result["crop"], "Tomato")
        self.assertEqual(result["disease"], "Healthy")
        self.assertEqual(result["treatments"], [])

    def test_plant_id_v3_request_uses_query_options(self):
        class Response:
            status_code = 200

            def json(self):
                return {"result": {
                    "classification": {"suggestions": [{"name": "Tomato", "probability": 0.9}]},
                    "disease": {"suggestions": [{"name": "Early blight", "probability": 0.9, "details": {}}]},
                    "is_healthy": {"binary": False},
                }}

        predictor = DiseasePredictor.__new__(DiseasePredictor)
        predictor.plant_id_api_key = "test-key"
        predictor.plant_id_api_url = "https://api.plant.id/v3/identification"
        predictor.plant_id_health = "all"
        predictor.provider = "plant_id"

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "leaf.jpg"
            image_path.write_bytes(b"image")
            with patch("requests.post", return_value=Response()) as post:
                predictor._plant_id_prediction(str(image_path))

        self.assertEqual(post.call_args.kwargs["json"], {"images": ["aW1hZ2U="]})
        self.assertEqual(post.call_args.kwargs["params"]["health"], "all")
        self.assertEqual(post.call_args.kwargs["params"]["similar_images"], "false")

    def test_predict_uses_pretrained_model_labels(self):
        predictor = DiseasePredictor.__new__(DiseasePredictor)
        predictor.processor = DummyProcessor()
        predictor.model = DummyModel()
        predictor.class_names = ["Apple___healthy", "Tomato___Early_blight"]
        predictor.confidence_threshold = 0.35

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "leaf.jpg"
            Image.new("RGB", (224, 224), color=(255, 255, 255)).save(image_path)

            result = predictor.predict(str(image_path))

        self.assertEqual(result["crop"], "Tomato")
        self.assertEqual(result["disease"], "Early blight")
        self.assertGreater(float(result["confidence"].rstrip("%")), 35.0)

    def test_predict_refuses_to_invent_disease_when_model_missing(self):
        predictor = DiseasePredictor.__new__(DiseasePredictor)
        predictor.processor = None
        predictor.model = None
        predictor.model_load_error = "The pretrained model could not be loaded."
        predictor.class_names = ["Tomato___Early_blight", "Potato___Late_blight"]
        predictor.confidence_threshold = 0.35

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "leaf.jpg"
            Image.new("RGB", (224, 224), color=(100, 180, 80)).save(image_path)

            with self.assertRaisesRegex(RuntimeError, "pretrained disease model is unavailable"):
                predictor.predict(str(image_path))

    def test_plant_id_rejects_non_plant_images(self):
        class Response:
            status_code = 200

            def json(self):
                return {"result": {
                    "classification": {"suggestions": [{"name": "Laptop", "probability": 0.92}]},
                    "disease": {"suggestions": []},
                    "is_healthy": {"binary": False, "probability": 0.2},
                }}

        predictor = DiseasePredictor.__new__(DiseasePredictor)
        predictor.plant_id_api_key = "test-key"
        predictor.plant_id_api_url = "https://api.plant.id/v3/identification"
        predictor.plant_id_health = "all"
        predictor.provider = "plant_id"

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "laptop.jpg"
            image_path.write_bytes(b"image")
            with patch("requests.post", return_value=Response()):
                with self.assertRaisesRegex(RuntimeError, "NON_PLANT_IMAGE"):
                    predictor._plant_id_prediction(str(image_path))


if __name__ == "__main__":
    unittest.main()
