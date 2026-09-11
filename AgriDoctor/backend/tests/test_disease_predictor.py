import sys
import tempfile
import types
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from ml_models.disease_model.disease_predictor import DiseasePredictor


class DummyModel:
    input_shape = (None, 224, 224, 3)

    def predict(self, images, verbose=0):
        arr = np.asarray(images)
        if np.max(arr) > 1.0 or np.min(arr) < -1.0:
            raise AssertionError("Model received unpreprocessed image data")
        return np.array([[0.05, 0.95]])


class DummyKerasModule(types.SimpleNamespace):
    class applications:
        class mobilenet_v2:
            @staticmethod
            def preprocess_input(image_array):
                return image_array / 127.5 - 1.0


class DiseasePredictorPreprocessingTest(unittest.TestCase):
    def test_predict_uses_mobilenet_preprocessing(self):
        module = types.ModuleType("tensorflow")
        module.keras = DummyKerasModule()
        sys.modules["tensorflow"] = module

        predictor = DiseasePredictor.__new__(DiseasePredictor)
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

    def test_predict_returns_fallback_disease_when_model_missing(self):
        predictor = DiseasePredictor.__new__(DiseasePredictor)
        predictor.model = None
        predictor.class_names = ["Tomato___Early_blight", "Potato___Late_blight"]
        predictor.confidence_threshold = 0.35

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "leaf.jpg"
            Image.new("RGB", (224, 224), color=(100, 180, 80)).save(image_path)

            result = predictor.predict(str(image_path))

        self.assertIn(result["disease"], {"Early blight", "Late blight", "Leaf Mold", "Rust"})
        self.assertIn(result["crop"], {"Tomato", "Potato", "Groundnut"})
        self.assertTrue(float(result["confidence"].rstrip("%")) > 0)


if __name__ == "__main__":
    unittest.main()
