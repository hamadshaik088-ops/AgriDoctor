import json
from pathlib import Path
import os


class DiseasePredictor:
    def __init__(self):
        self.model_dir = Path(__file__).resolve().parent
        self.class_names = self._load_class_names()
        self.model = self._load_model()

    def _load_model(self):
        model_path = Path(os.getenv("DISEASE_MODEL_PATH", self.model_dir / "disease_model.keras"))
        if not model_path.exists():
            return None
        try:
            from tensorflow.keras.models import load_model
        except ImportError as exc:
            raise RuntimeError("A disease model was configured, but TensorFlow is not installed.") from exc
        return load_model(model_path)

    def _load_class_names(self):
        path = self.model_dir / "class_names.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        return [
            "Tomato___Early_Blight", "Tomato___Late_Blight", "Tomato___Healthy",
            "Potato___Early_Blight", "Potato___Late_Blight", "Groundnut___Tikka_Leaf_Spot",
            "Groundnut___Rust", "Groundnut___Healthy"
        ]

    def predict(self, image_path):
        if self.model is None:
            raise RuntimeError(
                "No trained disease model is configured. Add disease_model.keras to "
                f"{self.model_dir} or set DISEASE_MODEL_PATH."
            )

        try:
            from PIL import Image
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("Pillow and NumPy are required for disease model inference.") from exc

        height, width = self.model.input_shape[1:3]
        image = Image.open(image_path).convert("RGB").resize((width, height))
        probabilities = self.model.predict(np.asarray(image, dtype="float32")[None, ...] / 255.0, verbose=0)[0]
        class_index = int(np.argmax(probabilities))
        class_name = self.class_names[class_index]
        confidence = float(probabilities[class_index])
        crop, disease = class_name.split("___") if "___" in class_name else ("Tomato", "Early Blight")
        healthy = disease.lower() == "healthy"
        return {
            "crop": crop,
            "disease": disease.replace("_", " "),
            "confidence": f"{confidence * 100:.1f}%",
            "severity": "Healthy" if healthy else "Moderate",
            "symptoms": "No disease symptoms detected." if healthy else "Visible symptoms should be confirmed in the field.",
            "causes": "No disease causes apply to a healthy result." if healthy else "Confirm the diagnosis with an agricultural expert before treatment.",
            "management": "Continue monitoring the crop." if healthy else "Remove severely affected material and follow verified crop-specific guidance.",
            "treatment": "No pesticide is recommended for a healthy crop." if healthy else "Use only a registered product listed for this crop and disease.",
            "weather_risk": "LOW" if healthy else "MEDIUM",
            "is_demo": False,
            "message": "AI result. Verify the diagnosis and product label with a local agricultural expert before spraying."
        }
