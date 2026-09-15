import os
import base64
from pathlib import Path
from time import monotonic


class DiseasePredictor:
    def __init__(self):
        self.plant_id_api_key = os.getenv("PLANT_ID_API_KEY", "").strip()
        self.allow_model_download = os.getenv("ALLOW_MODEL_DOWNLOAD", "0").lower() in {"1", "true", "yes"}
        self.provider = "plant_id" if self.plant_id_api_key else "huggingface"
        self.model_id = os.getenv(
            "DISEASE_MODEL_ID",
            "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification",
        )
        self.model_load_error = None
        local_model_available = Path(self.model_id).exists()
        if self.provider == "huggingface" and not self.allow_model_download and not local_model_available:
            self.model_load_error = (
                "No local disease model is configured. Set PLANT_ID_API_KEY, "
                "deploy the Hugging Face model files, or set ALLOW_MODEL_DOWNLOAD=1."
            )
            self.processor, self.model, self.class_names = None, None, []
        else:
            self.processor, self.model, self.class_names = self._load_model() if self.provider == "huggingface" else (None, None, [])
        self.confidence_threshold = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.35"))

    def _load_model(self):
        started_at = monotonic()
        try:
            from transformers import AutoImageProcessor, AutoModelForImageClassification
        except ImportError:
            self.model_load_error = "The transformers package is not installed in the API environment."
            return None, None, []
        try:
            model_options = {} if self.allow_model_download else {"local_files_only": True}
            processor = AutoImageProcessor.from_pretrained(self.model_id, **model_options)
            model = AutoModelForImageClassification.from_pretrained(self.model_id, **model_options)
            model.eval()
            class_names = [model.config.id2label[index] for index in range(model.config.num_labels)]
            return processor, model, class_names
        except Exception as exc:
            self.model_load_error = f"Could not load pretrained model '{self.model_id}': {exc}"
            return None, None, []
        finally:
            load_seconds = monotonic() - started_at
            if load_seconds > 30:
                self.model_load_error = (
                    self.model_load_error
                    or f"Model loading took {load_seconds:.0f} seconds. Configure a cached model for faster scans."
                )

    def _model_unavailable(self):
        detail = self.model_load_error or "The pretrained disease model could not be loaded."
        raise RuntimeError(
            "The pretrained disease model is unavailable. "
            f"{detail} Install the API requirements and allow the model to download from Hugging Face."
        )

    def _uncertain_prediction(self, confidence):
        return {
            "crop": "Unknown",
            "disease": "Uncertain",
            "confidence": f"{confidence * 100:.1f}%",
            "severity": "Unknown",
            "symptoms": "The model could not identify this image with enough confidence.",
            "causes": "No cause can be determined from an uncertain prediction.",
            "management": "Capture a clear photo of one affected leaf and consult an agricultural expert.",
            "treatment": "Do not spray based on this result.",
            "weather_risk": "UNKNOWN",
            "is_demo": False,
            "message": "The model was uncertain. No crop or disease was assigned.",
        }

    def _plant_id_prediction(self, image_path):
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("The requests package is required for Plant.id inference.") from exc

        image_data = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        response = requests.post(
            "https://api.plant.id/v3/identification",
            headers={"Api-Key": self.plant_id_api_key, "Content-Type": "application/json"},
            json={
                "images": [image_data],
                "health": "all",
                "similar_images": False,
                "language": "en",
                "details": ["local_name", "description", "treatment", "common_names"],
            },
            timeout=(5, 20),
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Plant.id returned HTTP {response.status_code}: {response.text[:300]}")
        payload = response.json().get("result", {})
        classification = payload.get("classification", {}).get("suggestions", [])
        disease_suggestions = payload.get("disease", {}).get("suggestions", [])
        if not classification or not disease_suggestions:
            raise RuntimeError("Plant.id could not identify a crop and disease from this image.")

        crop_result = max(classification, key=lambda item: item.get("probability", 0))
        disease_result = max(disease_suggestions, key=lambda item: item.get("probability", 0))
        crop = crop_result.get("name", "Unknown")
        disease = disease_result.get("name", "Uncertain")
        confidence = float(disease_result.get("probability", 0))
        details = disease_result.get("details") or {}
        treatment_details = details.get("treatment") or {}
        chemical = treatment_details.get("chemical")
        biological = treatment_details.get("biological")
        treatments = []
        if chemical:
            treatments.append({
                "crop": crop,
                "disease": disease,
                "treatment_category": "Chemical treatment guidance",
                "active_ingredient": chemical,
                "product_name": "Use a locally registered product",
                "application_guidance": "Follow the chemical treatment guidance and the registered product label for this crop.",
                "safety_precautions": "Verify local approval, dose, protective equipment, and pre-harvest interval before spraying.",
                "pre_harvest_interval": "As stated on the registered product label",
                "region": "India",
                "source": "Plant.id expert-compiled disease treatment guidance",
                "last_updated": "2026-01-15",
            })
        if biological:
            treatments.append({
                "crop": crop,
                "disease": disease,
                "treatment_category": "Biological treatment guidance",
                "active_ingredient": biological,
                "product_name": "Use a locally registered biological product",
                "application_guidance": "Follow the product label and local agricultural guidance.",
                "safety_precautions": "Verify local approval before application.",
                "pre_harvest_interval": "As stated on the registered product label",
                "region": "India",
                "source": "Plant.id expert-compiled disease treatment guidance",
                "last_updated": "2026-01-15",
            })
        healthy = payload.get("is_healthy", {}).get("binary", False)
        return {
            "crop": crop,
            "disease": "Healthy" if healthy else disease,
            "confidence": f"{confidence * 100:.1f}%",
            "severity": "Healthy" if healthy else "Moderate",
            "symptoms": "No disease symptoms detected." if healthy else details.get("description", "Visible symptoms should be confirmed in the field."),
            "causes": "No disease causes apply to a healthy result." if healthy else "See the provider disease report and confirm in the field.",
            "management": treatment_details.get("prevention", "Follow local agricultural guidance."),
            "treatment": treatment_details.get("chemical") or treatment_details.get("biological") or "No treatment details were returned.",
            "treatments": [] if healthy else treatments,
            "weather_risk": "LOW" if healthy else "MEDIUM",
            "is_demo": False,
            "message": "Plant.id AI result. Verify diagnosis and product approval with a local agricultural expert before spraying.",
        }

    def predict(self, image_path):
        if getattr(self, "provider", "huggingface") == "plant_id":
            return self._plant_id_prediction(image_path)
        if self.model is None or self.processor is None:
            self._model_unavailable()

        try:
            from PIL import Image
            import numpy as np
            import torch
        except ImportError as exc:
            raise RuntimeError("Pillow, NumPy, PyTorch, and Transformers are required for disease inference.") from exc

        image = Image.open(image_path).convert("RGB")
        processed = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            logits = self.model(**processed).logits
        probabilities = torch.softmax(logits, dim=-1)[0].cpu().numpy()
        if len(probabilities) != len(self.class_names):
            raise RuntimeError("The pretrained model output count does not match its label configuration.")
        class_index = int(np.argmax(probabilities))
        class_name = self.class_names[class_index]
        confidence = float(probabilities[class_index])
        if confidence < self.confidence_threshold:
            return self._uncertain_prediction(confidence)

        if "___" in class_name:
            crop, disease = class_name.split("___", 1)
        else:
            crop, disease = "Tomato", class_name

        disease_label = disease.replace("_", " ")
        healthy = "healthy" in disease.lower()
        return {
            "crop": crop,
            "disease": disease_label,
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
