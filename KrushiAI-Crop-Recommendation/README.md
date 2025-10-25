# KrushiAI — AI Crop Recommendation System

A simple Flask web app that recommends the most suitable crop based on soil and climate parameters using a pre-trained RandomForest model.

## Tech stack
- Python + Flask backend
- scikit-learn model (`RandomForest.pkl`)
- Vanilla HTML/CSS/JS frontend

## Quick start

1) Create a virtual environment (Windows PowerShell):

   - Python 3.14 (via py launcher):
     py -3.14 -m venv .venv

   - Or with the default python:
     python -m venv .venv

2) Install dependencies:

   .venv\Scripts\python -m pip install -U pip
   .venv\Scripts\python -m pip install -r requirements.txt

3) Run the app:

   .venv\Scripts\python app.py

The app starts on http://localhost:5000 (configurable via env vars below).

## Configuration
- HOST: default 0.0.0.0
- PORT: default 5000
- FLASK_DEBUG: set to "true" to enable debug mode

Example (PowerShell):

   $env:PORT = "8080"
   $env:FLASK_DEBUG = "false"
   .venv\Scripts\python app.py

## API
- POST /predict
  JSON body:
  {
    "nitrogen": 50,
    "phosphorus": 50,
    "potassium": 50,
    "temperature": 25,
    "humidity": 60,
    "ph": 6.5,
    "rainfall": 100
  }

  Response:
  {
    "prediction": "mango",
    "info": "..."
  }

- GET /health -> { "status": "ok" }

## Development notes
- Static files are served directly: `index.html`, `style.css`, `script.js`.
- The model is loaded from `RandomForest.pkl` at startup.
- If a `LabelEncoder.pkl` is present, it will be used to map integer predictions back to labels; otherwise, a fallback alphabetical mapping is used.

## Troubleshooting
- If you see a warning about "feature names" from scikit-learn during prediction, it is suppressed by default and can be safely ignored.
- Ensure `RandomForest.pkl` and `crop_info.json` are present in the project root.
- If ports conflict, set `$env:PORT` to another value.
