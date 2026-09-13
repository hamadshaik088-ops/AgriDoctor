# AgriDoctor

AgriDoctor is a mobile-first agriculture decision support platform for Indian farmers. It combines crop disease detection, soil analysis, weather data, crop recommendation, smart recommendations, farmer dashboard, and admin management in one project.

## Features
- Farmer registration and JWT-based login
- Farm profile management
- Mobile camera disease scan workflow
- AI disease prediction demo interface with clear disclaimers
- Soil analysis and crop recommendation forms
- Weather and climate-driven risk suggestions
- Smart recommendation engine combining soil, disease, weather, and crop context
- History and notification views
- Admin dashboard placeholders for disease and treatment management

## Stack
- Frontend: React + Vite + JavaScript
- Backend: Flask + SQLAlchemy + JWT + PostgreSQL-ready config
- ML: lightweight model interfaces plus demo prediction mode

## Folder structure
- backend/
- frontend/
- docs/
- ml/
- tests/

## Quick start

### Backend
Open a terminal in the backend directory before running these commands:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run.py
```

The local backend runs on `http://localhost:5001` by default. Set the `PORT`
environment variable to use another available port.

For Render, use this start command from the repository root:

```text
gunicorn --chdir backend --bind 0.0.0.0:$PORT app:app
```

If the Render service root directory is set to `backend`, use:

```text
gunicorn --bind 0.0.0.0:$PORT app:app
```

On Windows, use `python` after activating `.venv`; `py` can bypass the activated environment.

### Frontend
Open a second terminal in the frontend directory:

```powershell
cd frontend
npm install
npm run dev
```

The frontend uses `http://localhost:5000/api` by default. If port 5173 is busy, Vite will select the next available port and print its URL.

## Environment variables
Backend uses .env for secrets. Frontend uses VITE_API_BASE_URL in frontend/.env.

For the Render backend, add a `DATABASE_URL` environment variable using the
PostgreSQL database's **External Database URL**. Do not commit the URL or its
password. The backend also accepts Render's legacy `postgres://` URL format.
Set `JWT_SECRET_KEY` to a long random value and optionally set
`JWT_ACCESS_TOKEN_EXPIRES` in seconds (the default is 86400 seconds).

The backend creates these PostgreSQL tables on startup: users, farmers, farms,
soil_records, disease_predictions, crop_recommendations, weather_records,
notifications, diseases, and treatments. Registration and all farmer data
endpoints use the JWT returned by `/api/auth/register` or `/api/auth/login`.

### Disease model
The scanner identifies the crop and disease from the image; it does not use a manually selected crop. Add the trained Keras model at:

```text
backend/ml_models/disease_model/disease_model.keras
```

Its output classes must match `backend/ml_models/disease_model/class_names.json` in the same order. The model must accept RGB images in `(batch, height, width, 3)` format and return one probability per class. Without this model, the upload works but the API correctly refuses to invent a diagnosis.

To train the model, create one folder per class under a separate dataset directory. Each folder must contain many labelled images:

```text
dataset/
	Tomato___Early_Blight/
	Tomato___Late_Blight/
	Tomato___Healthy/
	Potato___Early_Blight/
	Potato___Late_Blight/
	Groundnut___Tikka_Leaf_Spot/
	Groundnut___Rust/
	Groundnut___Healthy/
```

Install the training dependencies from `backend/training_requirements.txt`, then run:

```powershell
cd backend
..\.venv-training\Scripts\Activate.ps1
uv pip install --python .venv-training\Scripts\python.exe -r training_requirements.txt
python ml_models/disease_model/train_disease_model.py --dataset C:\path\to\dataset --output ml_models/disease_model/disease_model.keras
```

Training uses Python 3.12 because TensorFlow is not available for the project's Python 3.14 runtime. The separate `.venv-training` environment does not affect the Flask runtime environment.

Because the scanner loads TensorFlow at runtime, start Flask with the same environment after training:

```powershell
cd backend
.\.venv-training\Scripts\python.exe app.py
```

The script refuses to train when any required class is missing and writes the model consumed by the scanner.

## Notes
- Real ML models and treatment databases are not shipped; the app is structured for production use and clearly marks demo behavior until trained models and verified data are added.
- TensorFlow is intentionally excluded from the Render runtime requirements because Render's default Python 3.14 runtime does not provide a compatible TensorFlow wheel. The API uses the documented Pillow/NumPy fallback until a model is deployed. Install TensorFlow only from `training_requirements.txt` in the separate Python 3.12 training environment.
- Camera access on production requires HTTPS.
