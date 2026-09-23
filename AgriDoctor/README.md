# AgriDoctor

AgriDoctor is a mobile-first agriculture decision support platform for Indian farmers. It combines crop disease detection, soil analysis, weather data, crop recommendation, smart recommendations, farmer dashboard, and admin management in one project.

## Features
- Farmer registration and JWT-based login
- Farm profile management
- Mobile camera disease scan workflow
- AI disease prediction with explicit model coverage and uncertainty handling
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

The frontend uses `http://localhost:5001/api` in Vite development mode, matching the local Flask backend. If port 5173 is busy, Vite will select the next available port and print its URL.

## Environment variables
Backend uses .env for secrets. Frontend uses VITE_API_BASE_URL in frontend/.env.

For a local PostgreSQL database, create `backend/.env` and add a `DATABASE_URL`
using the PostgreSQL connection URL shown by pgAdmin. Without this variable,
the backend intentionally uses `backend/instance/agridoctor.db` (SQLite).
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
Production should use the single universal Plant.id provider. Add `PLANT_ID_API_KEY` to the Render service environment; the application selects Plant.id automatically and requests its complete plant-health assessment:

```text
PLANT_ID_API_KEY=your-api-key
PLANT_ID_HEALTH=all
```

Plant.id is one provider for many crops and diseases; the application does not need a separate model per crop. Its coverage is broad but not literally guaranteed for every disease, so the result must still be confirmed locally.

Without a provider key, the scanner can use the limited Hugging Face development fallback `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`. Install the API requirements and start Flask; Transformers downloads the model on its first prediction:

```powershell
cd backend
python -m pip install -r requirements.txt
python app.py
```

This model uses the PlantVillage 38-class label set. It includes tomato and potato, but not rice/false smut or groundnut/peanut. The repository contains no locally trained weights or training dataset. Configure `DISEASE_MODEL_ID` only when selecting another compatible pretrained image-classification model. Selecting Rice in the scanner does not add rice recognition to this fallback; it makes the API reject unrelated fallback labels instead of showing a misleading crop.

For broad crop coverage, configure the official Plant.id v3 provider. Plant.id documents support for more than 35,000 plant taxa and 548 plant-health conditions, and returns disease treatment details, including chemical guidance when available. This is broad coverage, not a guarantee for every crop or disease:

```powershell
$env:PLANT_ID_API_KEY = "your-api-key"
python app.py
```

The API key is read only from the environment and must not be committed. Plant.id requires an account and usage credits.

Pesticide suggestions are returned only for explicit crop-disease mappings in `backend/services/treatment_service.py`. Unsupported, healthy, viral, and uncertain results return no pesticide recommendation. A genuine all-crop system still requires a verified broader disease model or separate specialist models; the available pretrained model must not be presented as groundnut or all-crop coverage.

The application selects Plant.id automatically when `PLANT_ID_API_KEY` is set. Without that key, the optional Hugging Face fallback is limited to the PlantVillage 38-class label set. Never enable the fallback and describe it as all-crop coverage. Product approval, dosage, protective equipment, and pre-harvest interval must be verified against the current Indian product label before spraying.

## Notes
- The pretrained model is PlantVillage-based and does not include groundnut/peanut. It must not be used to claim groundnut coverage.
- The API refuses to invent a diagnosis when the pretrained model cannot load or is uncertain.
- Camera access on production requires HTTPS.
