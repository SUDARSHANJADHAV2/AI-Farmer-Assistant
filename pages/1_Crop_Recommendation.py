## Importing necessary libraries for the web app
import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from PIL import Image
from lib import database as db # Import database module

warnings.filterwarnings('ignore')

# Note: st.set_page_config and global CSS are handled in the main dashboard.py

# --- Page Configuration ---
st.markdown("""
<div class="main-header">
    <h1 style="color: white;">🌱 Smart Crop Recommendation</h1>
    <p>Get data-driven crop suggestions based on soil and climate conditions</p>
</div>
""", unsafe_allow_html=True)


# --- Model and Data Loading ---
@st.cache_data
def load_data():
    """Loads the crop recommendation dataset."""
    path = 'KrushiAI-Crop-Recommendation/Crop_recommendation.csv'
    if not os.path.exists(path):
        st.error(f"Dataset not found at {path}")
        return None
    return pd.read_csv(path)

@st.cache_resource
def load_model():
    """Loads the pre-trained Random Forest model."""
    path = 'KrushiAI-Crop-Recommendation/RF.pkl'
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as file:
        model = pickle.load(file)
    return model

# --- Prediction Function ---
def predict_crop(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
    """Makes a crop prediction based on input parameters."""
    model = load_model()
    if model is None:
        return None
    prediction = model.predict(np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]]))
    return prediction

# --- Crop Information ---
crop_info = {
    'rice': "Rice thrives in warm, humid conditions with abundant water. Ideal for lowland areas with good irrigation.",
    'maize': "Maize (corn) grows well in well-drained soils with moderate rainfall and warm temperatures.",
    'chickpea': "Chickpeas prefer cool, dry conditions and can tolerate drought. They enrich soil with nitrogen.",
    'kidneybeans': "Kidney beans need warm temperatures and moderate rainfall. They prefer well-drained, fertile soil.",
    'pigeonpeas': "Pigeon peas are drought-resistant and grow well in semi-arid regions with minimal rainfall.",
    'mothbeans': "Moth beans are extremely drought-tolerant and thrive in hot, dry conditions with minimal water.",
    'mungbean': "Mung beans prefer warm temperatures and moderate rainfall. They have a short growing season.",
    'blackgram': "Black gram thrives in warm, humid conditions and can tolerate some drought.",
    'lentil': "Lentils prefer cool growing conditions and moderate rainfall. They're adaptable to various soil types.",
    'pomegranate': "Pomegranates thrive in hot, dry climates and are drought-tolerant once established.",
    'banana': "Bananas need consistent warmth, high humidity, and abundant water. They're sensitive to frost.",
    'mango': "Mangoes require tropical conditions with a distinct dry season for flowering. They're frost-sensitive.",
    'grapes': "Grapes grow best in temperate climates with warm, dry summers and mild winters.",
    'watermelon': "Watermelons need hot temperatures, plenty of sunlight, and moderate water during growth.",
    'muskmelon': "Muskmelons require warm temperatures, full sun, and moderate, consistent moisture.",
    'apple': "Apples need a cold winter period for dormancy and moderate summers. They prefer well-drained soil.",
    'orange': "Oranges thrive in subtropical climates with mild winters and warm summers.",
    'papaya': "Papayas need consistent warmth and moisture. They're very frost-sensitive.",
    'coconut': "Coconuts require tropical conditions with high humidity, warm temperatures, and regular rainfall.",
    'cotton': "Cotton thrives in warm climates with long growing seasons and moderate rainfall.",
    'jute': "Jute needs warm, humid conditions with high rainfall during the growing season.",
    'coffee': "Coffee grows best in tropical highlands with moderate temperatures and regular rainfall."
}


# --- Main Page UI ---
def show_page():
    """Renders the Crop Recommendation page."""

    # Load model and data
    model = load_model()
    df = load_data()

    if model is None or df is None:
        st.error("Model or data not found. Please ensure the necessary files are in the 'KrushiAI-Crop-Recommendation' directory.")
        return

    # Personalize if user is logged in
    if st.session_state.get('logged_in'):
        farm_details = db.get_farm_details(st.session_state['user_id'])
        farm_name = farm_details['farm_name'] if farm_details and farm_details['farm_name'] else st.session_state['username'] + "'s Farm"
        st.info(f"Welcome, {st.session_state['username']}! Using settings for {farm_name}.")

    # Create tabs for different sections
    tab1, tab2 = st.tabs(["🔮 Prediction", "📊 Dataset Insights"])

    with tab1:
        st.markdown("#### Enter your farm's conditions to get a recommendation:")

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("##### Soil Parameters")
            nitrogen = st.number_input("🧪 Nitrogen (N) in kg/ha", min_value=0.0, max_value=140.0, value=50.0, step=1.0)
            phosphorus = st.number_input("🧪 Phosphorus (P) in kg/ha", min_value=0.0, max_value=145.0, value=50.0, step=1.0)
            potassium = st.number_input("🧪 Potassium (K) in kg/ha", min_value=0.0, max_value=205.0, value=50.0, step=1.0)
            ph = st.number_input("🧪 Soil pH Level", min_value=0.0, max_value=14.0, value=6.5, step=0.1)

            st.markdown("##### Climate Parameters")
            temperature = st.number_input("🌡️ Temperature in °C", min_value=0.0, max_value=51.0, value=25.0, step=0.1)
            humidity = st.number_input("💧 Relative Humidity in %", min_value=0.0, max_value=100.0, value=60.0, step=0.1)
            rainfall = st.number_input("🌧️ Rainfall in mm", min_value=0.0, max_value=500.0, value=100.0, step=0.1)

            predict_button = st.button("🔮 Predict Crop", use_container_width=True)

        with col2:
            st.markdown("##### Recommendation Result")
            if predict_button:
                with st.spinner('Analyzing your parameters...'):
                    prediction = predict_crop(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)

                    if prediction is not None:
                        recommended_crop = prediction[0]

                        st.markdown(f"""
                        <div class="prediction-result" style="border-left-color: #4CAF50;">
                            <h3 style="color: white; text-align:center; margin-bottom:10px;">Recommended Crop</h3>
                            <h2 style="color: white; text-align:center; text-transform:uppercase; font-size:2.5rem; margin:0;">{recommended_crop}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                        if recommended_crop.lower() in crop_info:
                             st.markdown(f"""
                            <div class="info-card" style="background: linear-gradient(135deg, #2E7D32, #4CAF50);">
                                <h4>About {recommended_crop}</h4>
                                <p>{crop_info[recommended_crop.lower()]}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("##### Your Input Parameters")
                        param_names = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']
                        param_values = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]

                        plt.style.use('dark_background')
                        fig, ax = plt.subplots(figsize=(10, 5), facecolor='#0e1117')
                        bars = ax.bar(param_names, param_values, color=['#1976D2', '#4CAF50', '#FFC107', '#F44336', '#9C27B0', '#00BCD4', '#3F51B5'])
                        ax.set_title('Input Parameter Visualization', color='white', fontsize=14, fontweight='bold')
                        ax.set_ylabel('Value', color='white', fontweight='bold')
                        ax.set_facecolor('rgba(255, 255, 255, 0.05)')
                        ax.tick_params(colors='white')
                        ax.spines['bottom'].set_color('white')
                        ax.spines['top'].set_color('white')
                        ax.spines['right'].set_color('white')
                        ax.spines['left'].set_color('white')
                        plt.xticks(rotation=45, color='white')
                        plt.yticks(color='white')
                        plt.tight_layout()
                        st.pyplot(fig)
            else:
                 st.markdown("""
                <div class="info-card" style="background: linear-gradient(135deg, #1e3c72, #2a5298); text-align: center;">
                    <p style="font-size: 1.1rem; margin: 0;">Fill in the parameters on the left and click the button to get your personalized crop recommendation.</p>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Dataset Insights")
        st.write("This application is powered by a dataset containing the following characteristics:")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="metric-card"><h4>Records</h4><h2>{df.shape[0]}</h2></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card"><h4>Features</h4><h2>{df.shape[1]-1}</h2></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card"><h4>Crop Varieties</h4><h2>{df['label'].nunique()}</h2></div>""", unsafe_allow_html=True)

        st.markdown("##### Sample Data")
        st.dataframe(df.head())

        st.markdown("##### Crop Distribution in Dataset")
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0e1117')
        crop_counts = df['label'].value_counts()
        sns.barplot(x=crop_counts.index, y=crop_counts.values, ax=ax, palette='viridis')
        ax.set_facecolor('rgba(255, 255, 255, 0.05)')
        ax.set_title('Distribution of Crops', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel('Crop Type', color='white', fontweight='bold')
        ax.set_ylabel('Number of Records', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        plt.xticks(rotation=90, color='white')
        plt.yticks(color='white')
        plt.tight_layout()
        st.pyplot(fig)

show_page()
