import streamlit as st
import pickle
import numpy as np
import os
from datetime import datetime
from lib import database as db # Import database module

# Note: st.set_page_config and global CSS are handled in the main dashboard.py

# --- Page Configuration ---
st.markdown("""
<div class="main-header">
    <h1 style="color: white;">🌿 Smart Fertilizer Recommendation</h1>
    <p>Optimize crop nutrition with AI-powered fertilizer advice</p>
</div>
""", unsafe_allow_html=True)


# --- Model and Data Loading ---
@st.cache_resource
def load_model_components():
    """Load all model components with error handling"""
    base_path = "KrushiAI-Fertilizer-Recommendation/"
    try:
        model = pickle.load(open(os.path.join(base_path, "Fertilizer_RF.pkl"), "rb"))
        soil_encoder = pickle.load(open(os.path.join(base_path, "soil_encoder.pkl"), "rb"))
        crop_encoder = pickle.load(open(os.path.join(base_path, "crop_encoder.pkl"), "rb"))
        fertilizer_encoder = pickle.load(open(os.path.join(base_path, "fertilizer_encoder.pkl"), "rb"))

        try:
            scaler = pickle.load(open(os.path.join(base_path, "feature_scaler.pkl"), "rb"))
            model_metrics = pickle.load(open(os.path.join(base_path, "model_metrics.pkl"), "rb"))
        except FileNotFoundError:
            scaler = None
            model_metrics = None

        return model, soil_encoder, crop_encoder, fertilizer_encoder, scaler, model_metrics
    except Exception as e:
        st.error(f"❌ Error loading model components: {str(e)}")
        return None, None, None, None, None, None

# --- Helper Functions ---
def validate_inputs(temp, humidity, moisture, nitrogen, potassium, phosphorous):
    """Validate user inputs"""
    errors = []
    if not (0 <= temp <= 60): errors.append("Temperature should be between 0°C and 60°C")
    if not (0 <= humidity <= 100): errors.append("Humidity should be between 0% and 100%")
    if not (0 <= moisture <= 100): errors.append("Soil moisture should be between 0% and 100%")
    if not (0 <= nitrogen <= 300): errors.append("Nitrogen should be between 0 and 300 mg/kg")
    if not (0 <= potassium <= 300): errors.append("Potassium should be between 0 and 300 mg/kg")
    if not (0 <= phosphorous <= 300): errors.append("Phosphorous should be between 0 and 300 mg/kg")
    return errors

def get_fertilizer_info(fertilizer_name):
    """Get detailed information about the recommended fertilizer"""
    fertilizer_info = {
        "Urea": {"description": "High nitrogen content (46% N).", "benefits": ["Promotes leafy growth", "Improves protein content"], "rate": "100-200 kg/ha"},
        "DAP": {"description": "Di-ammonium Phosphate (18% N, 46% P₂O₅).", "benefits": ["Root development", "Early plant growth"], "rate": "50-100 kg/ha"},
        "14-35-14": {"description": "NPK complex (14% N, 35% P₂O₅, 14% K₂O).", "benefits": ["Balanced nutrition", "Root development"], "rate": "150-250 kg/ha"},
        "28-28": {"description": "NPK fertilizer (28% N, 28% P₂O₅).", "benefits": ["Balanced N-P nutrition", "Strong root system"], "rate": "100-150 kg/ha"},
        "17-17-17": {"description": "Balanced NPK (17% each N, P₂O₅, K₂O).", "benefits": ["Complete balanced nutrition", "All-round growth"], "rate": "150-200 kg/ha"},
        "20-20": {"description": "NPK fertilizer (20% N, 20% P₂O₅).", "benefits": ["Good N-P balance", "Vigorous growth"], "rate": "125-175 kg/ha"},
        "10-26-26": {"description": "NPK fertilizer (10% N, 26% P₂O₅, 26% K₂O).", "benefits": ["High P-K content", "Disease resistance"], "rate": "100-200 kg/ha"}
    }
    return fertilizer_info.get(fertilizer_name, {"description": "Specialized blend.", "benefits": ["Optimized nutrition"], "rate": "As per soil test"})

# --- Main Page UI ---
def show_page():
    model, soil_encoder, crop_encoder, fertilizer_encoder, scaler, model_metrics = load_model_components()

    if not all([model, soil_encoder, crop_encoder, fertilizer_encoder]):
        st.error("Failed to load all model components. The page cannot be displayed.")
        return

    # --- Get Farm Details for Logged-in User ---
    farm_details = None
    default_soil_index = 0
    if st.session_state.get('logged_in'):
        farm_details = db.get_farm_details(st.session_state['user_id'])
        if farm_details and farm_details['soil_type']:
            try:
                # Find the index of the user's default soil type
                default_soil_index = list(soil_encoder.classes_).index(farm_details['soil_type'])
            except ValueError:
                default_soil_index = 0 # Default to first if not found
        st.info(f"Welcome, {st.session_state['username']}! Your saved farm details are being used.")

    # --- Sidebar for Inputs ---
    st.sidebar.header("Input Parameters")
    temp = st.sidebar.number_input("🌡️ Temperature (°C)", 0.0, 60.0, 26.0, 0.5)
    humidity = st.sidebar.number_input("💧 Humidity (%)", 0.0, 100.0, 52.0, 1.0)
    moisture = st.sidebar.number_input("🌿 Soil Moisture (%)", 0.0, 100.0, 38.0, 1.0)
    soil = st.sidebar.selectbox("🟤 Soil Type", soil_encoder.classes_, index=default_soil_index)
    crop = st.sidebar.selectbox("🌾 Crop Type", crop_encoder.classes_)
    nitrogen = st.sidebar.number_input("🔵 Nitrogen (N)", 0.0, 300.0, 37.0, 1.0)
    potassium = st.sidebar.number_input("🟡 Potassium (K)", 0.0, 300.0, 0.0, 1.0)
    phosphorous = st.sidebar.number_input("🔴 Phosphorous (P)", 0.0, 300.0, 0.0, 1.0)

    predict_button = st.sidebar.button("🔮 Recommend Fertilizer", use_container_width=True)

    # --- Main Content Area ---
    st.markdown("##### Recommendation")

    if predict_button:
        validation_errors = validate_inputs(temp, humidity, moisture, nitrogen, potassium, phosphorous)
        if validation_errors:
            for error in validation_errors:
                st.warning(error)
        else:
            with st.spinner("🔍 Analyzing your data..."):
                try:
                    soil_encoded = soil_encoder.transform([soil])[0]
                    crop_encoded = crop_encoder.transform([crop])[0]
                    features = np.array([[temp, humidity, moisture, soil_encoded, crop_encoded, nitrogen, potassium, phosphorous]])
                    if scaler:
                        features = scaler.transform(features)

                    pred = model.predict(features)[0]
                    fertilizer_name = fertilizer_encoder.inverse_transform([pred])[0]
                    pred_proba = model.predict_proba(features)[0]
                    confidence = np.max(pred_proba) * 100

                    fert_info = get_fertilizer_info(fertilizer_name)

                    st.markdown(f"""
                    <div class="prediction-result" style="border-left-color: #667eea;">
                        <h3 style="color: white; text-align:center;">Recommended Fertilizer</h3>
                        <h2 style="color: white; text-align:center; text-transform:uppercase;">{fertilizer_name}</h2>
                        <p style="text-align:center; font-size: 1.1rem;">Confidence: {confidence:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="info-card">
                        <h4>📋 Details for {fertilizer_name}</h4>
                        <p><strong>Description:</strong> {fert_info['description']}</p>
                        <p><strong>Key Benefits:</strong> {', '.join(fert_info['benefits'])}</p>
                        <p><strong>Typical Application Rate:</strong> {fert_info['rate']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"An error occurred during prediction: {e}")
    else:
        st.markdown("""
        <div class="info-card" style="background: linear-gradient(135deg, #1e3c72, #2a5298); text-align: center;">
            <p style="font-size: 1.1rem; margin: 0;">Your fertilizer recommendation will appear here. Please provide your farm's details in the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### Model Information")

    if model_metrics:
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.markdown(f"""<div class="metric-card"><h4>Model Accuracy</h4><h2>{model_metrics['accuracy']:.1%}</h2></div>""", unsafe_allow_html=True)
        with metric_col2:
            st.markdown(f"""<div class="metric-card"><h4>Cross-Validation Score</h4><h2>{model_metrics['cv_mean']:.1%} (±{model_metrics['cv_std']:.1%})</h2></div>""", unsafe_allow_html=True)
    else:
        st.info("Detailed model metrics are not available for this version.")

show_page()
