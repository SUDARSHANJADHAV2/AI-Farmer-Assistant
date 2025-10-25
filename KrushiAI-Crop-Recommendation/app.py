from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import pickle
import json
import os
import warnings
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS (allow all by default or set ALLOWED_ORIGINS env CSV)
_allowed = os.environ.get('ALLOWED_ORIGINS', '*')
if _allowed == '*' or _allowed.strip() == '':
    CORS(app)
else:
    CORS(app, resources={r"/*": {"origins": [o.strip() for o in _allowed.split(',') if o.strip()]}})

# Suppress noisy sklearn feature-name warnings during prediction
warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names, but .* was fitted with feature names",
    category=UserWarning,
)

# Load the model
with open('RandomForest.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Load crop info from JSON
with open('crop_info.json', 'r', encoding='utf-8') as info_file:
    crop_info = json.load(info_file)

# Try to load LabelEncoder if available
label_encoder = None
if os.path.exists('LabelEncoder.pkl'):
    try:
        with open('LabelEncoder.pkl', 'rb') as le_file:
            label_encoder = pickle.load(le_file)
    except Exception:
        label_encoder = None

# Build a fallback mapping (assumes alphabetical encoding)
alphabetical_classes = sorted(crop_info.keys())  # keys are lowercase crop names
int_to_class = {i: cls for i, cls in enumerate(alphabetical_classes)}

def to_crop_name(pred_val):
    """Robustly convert model output to a crop name string."""
    # Unwrap numpy arrays
    if isinstance(pred_val, (np.ndarray, list)) and len(pred_val) == 1:
        pred_val = pred_val[0]

    # If it's an integer label, map back to class name
    if isinstance(pred_val, (np.integer, int)):
        # Try LabelEncoder if present
        if label_encoder is not None:
            try:
                return str(label_encoder.inverse_transform([int(pred_val)])[0])
            except Exception:
                pass
        # Fallback to alphabetical mapping
        return str(int_to_class.get(int(pred_val), str(pred_val)))

    # If it's already a string-like label
    if isinstance(pred_val, (np.str_, str)):
        return str(pred_val)

    # Last resort
    return str(pred_val)

def map_class_label(cls_val):
    """Map a class value from model.classes_ to a human-readable crop name."""
    # If it's string-like, return as-is
    if isinstance(cls_val, (np.str_, str)):
        return str(cls_val)
    # If numeric, try label encoder then fallback mapping
    if isinstance(cls_val, (np.integer, int)):
        if label_encoder is not None:
            try:
                return str(label_encoder.inverse_transform([int(cls_val)])[0])
            except Exception:
                pass
        return str(int_to_class.get(int(cls_val), str(cls_val)))
    # Else, stringify
    return str(cls_val)

def top_k_predictions(features, k=3):
    if not hasattr(model, 'predict_proba'):
        return None
    proba = model.predict_proba(features)
    if not hasattr(model, 'classes_'):
        return None
    classes = getattr(model, 'classes_')
    # Handle binary classifier where proba is shape (1, 2)
    probs = np.array(proba[0])
    indices = np.argsort(probs)[::-1][:k]
    results = []
    for idx in indices:
        label = map_class_label(classes[idx])
        p = float(probs[idx])
        info = crop_info.get(label.lower(), 'No information available for this crop.')
        results.append({'label': label, 'probability': p, 'info': info})
    return results

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON body'}), 400

    try:
        # Validate and cast inputs
        required = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']
        for key in required:
            if key not in data:
                return jsonify({'error': f'Missing field: {key}'}), 400

        features = np.array([
            float(data['nitrogen']),
            float(data['phosphorus']),
            float(data['potassium']),
            float(data['temperature']),
            float(data['humidity']),
            float(data['ph']),
            float(data['rainfall'])
        ], dtype=float).reshape(1, -1)

        prediction = model.predict(features)
        label_str = to_crop_name(prediction[0])
        crop_key = str(label_str).lower()

        top3 = top_k_predictions(features, k=3)

        resp = {
            'prediction': label_str,
            'info': crop_info.get(crop_key, 'No information available for this crop.')
        }
        if top3:
            resp['top_3'] = top3
        return jsonify(resp)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Optional: graceful shutdown helpers (for dev use)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    # Use_reloader False to keep shutdown working
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    port = int(os.environ.get('PORT', '5000'))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=debug, use_reloader=False)
