import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
