"""
KrushiAI - Advanced Plant Disease Detection System
A comprehensive AI-powered solution for identifying plant diseases
with detailed analysis, treatment recommendations, and expert insights.
"""

import streamlit as st
import sys
import logging
import traceback
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from PIL import Image
from streamlit_option_menu import option_menu
import base64
from io import BytesIO

# Configure logging for deployment debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Import custom modules from the centralized 'lib' directory
    logger.info("Loading custom modules...")
    from lib.utils import ImageProcessor, ModelPredictor, ModelAnalyzer, format_disease_name, get_severity_color, create_confidence_message
    from lib.disease_info import get_disease_info, get_all_diseases, get_diseases_by_plant, get_severity_stats
    logger.info("All modules loaded successfully")

except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    st.error(f"Failed to import required modules: {str(e)}")
    st.error("Please check if all dependencies are installed correctly and the 'lib' directory is accessible.")
    st.stop()
except Exception as e:
    logger.error(f"Unexpected error during import: {str(e)}")
    st.error(f"Unexpected error: {str(e)}")
    st.stop()

# Note: Global CSS is loaded in dashboard.py

# ============================
# HELPER FUNCTIONS
# ============================

BASE_PATH = "KrushiAI-Disease-Recognition/"

@st.cache_data
def load_image_as_base64(image_path):
    """Load image and convert to base64 for display"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

@st.cache_resource
def load_model_predictor():
    """Load the model predictor (cached)"""
    try:
        logger.info("Attempting to load model predictor...")

        model_path = os.path.join(BASE_PATH, "trained_plant_disease_model.keras")
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            st.error(f"Model file '{model_path}' not found. Please ensure the model file is in the project directory.")
            return None

        file_size = os.path.getsize(model_path)
        logger.info(f"Model file size: {file_size / (1024*1024):.1f} MB")

        if file_size < 1000:
            logger.error("Model file appears to be corrupted (too small)")
            st.error("Model file appears to be corrupted. Please check the file.")
            return None

        predictor = ModelPredictor(model_path)
        logger.info("Model predictor loaded successfully")
        return predictor

    except Exception as e:
        logger.error(f"Error loading model predictor: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        st.error("❌ Failed to load the AI model")
        st.error(f"Error details: {str(e)}")
        with st.expander("🔧 Troubleshooting Information"):
            st.write("**Possible solutions:**")
            st.write("1. Ensure the model file 'trained_plant_disease_model.keras' exists")
            st.write("2. Check if TensorFlow is properly installed")
            st.write("3. Verify the model file is not corrupted")
            st.write("4. Try restarting the application")
        return None

@st.cache_resource
def load_model_analyzer():
    """Load the model analyzer (cached)"""
    try:
        logger.info("Loading model analyzer...")
        hist_path = os.path.join(BASE_PATH, "training_hist.json")
        if not os.path.exists(hist_path):
            logger.warning(f"Training history file not found: {hist_path}")
            return None

        analyzer = ModelAnalyzer(hist_path)
        logger.info("Model analyzer loaded successfully")
        return analyzer

    except Exception as e:
        logger.error(f"Error loading model analyzer: {str(e)}")
        return None

def create_feature_comparison_chart(features):
    """Create a feature comparison chart"""
    if not features:
        return None

    categories = ['Brightness', 'Contrast', 'Edge Density']
    values = [
        features.get('brightness', 0) / 255,
        features.get('contrast', 0) / 100,
        features.get('edge_density', 0) * 10
    ]

    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', name='Image Features', line_color='#667eea'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False, title="Image Feature Analysis", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    return fig

def create_confidence_chart(top_predictions):
    """Create a confidence comparison chart"""
    if not top_predictions:
        return None

    classes = [format_disease_name(pred['class']) for pred in top_predictions]
    confidences = [pred['percentage'] for pred in top_predictions]

    fig = go.Figure(data=[go.Bar(x=confidences, y=classes, orientation='h', marker_color=['#667eea' if i == 0 else '#a8b3f0' for i in range(len(classes))], text=[f"{conf:.1f}%" for conf in confidences], textposition='auto')])
    fig.update_layout(title="Top 5 Predictions Confidence", xaxis_title="Confidence (%)", yaxis_title="Disease/Condition", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=400)
    return fig

def display_model_performance():
    """Display model performance metrics"""
    analyzer = load_model_analyzer()
    if not analyzer:
        st.warning("Model training history not available.")
        return

    stats = analyzer.get_training_stats()
    performance = analyzer.get_performance_analysis()

    if stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="metric-card"><h3>🎯 Accuracy</h3><h2>{stats['final_val_accuracy']:.1%}</h2><p>Validation Accuracy</p></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card"><h3>📊 Loss</h3><h2>{stats['final_val_loss']:.3f}</h2><p>Validation Loss</p></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card"><h3>🔄 Epochs</h3><h2>{stats['total_epochs']}</h2><p>Training Epochs</p></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="metric-card"><h3>🏆 Best</h3><h2>{stats['best_val_accuracy']:.1%}</h2><p>Best Val Accuracy</p></div>""", unsafe_allow_html=True)

        if analyzer.history:
            fig = make_subplots(rows=1, cols=2, subplot_titles=('Model Accuracy', 'Model Loss'))
            epochs = list(range(1, len(analyzer.history['accuracy']) + 1))
            fig.add_trace(go.Scatter(x=epochs, y=analyzer.history['accuracy'], name='Training Accuracy', line=dict(color='#667eea')), row=1, col=1)
            fig.add_trace(go.Scatter(x=epochs, y=analyzer.history['val_accuracy'], name='Validation Accuracy', line=dict(color='#764ba2')), row=1, col=1)
            fig.add_trace(go.Scatter(x=epochs, y=analyzer.history['loss'], name='Training Loss', line=dict(color='#ff7b7b')), row=1, col=2)
            fig.add_trace(go.Scatter(x=epochs, y=analyzer.history['val_loss'], name='Validation Loss', line=dict(color='#ffa07a')), row=1, col=2)
            fig.update_layout(title="Training History", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=500)
            st.plotly_chart(fig, use_container_width=True)

        if 'analysis' in performance:
            st.markdown(f"""<div class="info-card"><h3>📈 Performance Analysis</h3><p>{performance['analysis']}</p><h4>💡 Recommendation</h4><p>{performance['recommendation']}</p></div>""", unsafe_allow_html=True)

# ============================
# UI COMPONENTS
# ============================

def show_home_page():
    """Display the home page"""
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class="info-card"><h2 style="text-align: center; margin-bottom: 1rem;">🎯 Welcome to KrushiAI</h2><p style="font-size: 1.1rem; text-align: center; line-height: 1.6;">Your AI-powered agricultural assistant for plant disease detection and management. Upload a photo of your plant, and our advanced deep learning model will identify potential diseases with detailed treatment recommendations.</p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #667eea; margin: 2rem 0;'>🚀 Key Features</h2>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""<div class="stat-card"><h3>🔬</h3><h4>AI Detection</h4><p>Advanced deep learning model trained on 38 plant diseases</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="stat-card"><h3>📈</h3><h4>96.5% Accuracy</h4><p>High-precision predictions with confidence scoring</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="stat-card"><h3>💡</h3><h4>Smart Recommendations</h4><p>Detailed treatment and prevention strategies</p></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class="stat-card"><h3>🌱</h3><h4>Multiple Crops</h4><p>Supports 15+ crop types including fruits and vegetables</p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #667eea; margin: 2rem 0;'>📊 Disease Statistics</h2>", unsafe_allow_html=True)
    severity_stats = get_severity_stats()
    if severity_stats:
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(values=list(severity_stats.values()), names=list(severity_stats.keys()), title="Disease Severity Distribution", color_discrete_map={'Critical': '#FF4B4B', 'High': '#FF8C42', 'Medium': '#FFD93D', 'Low': '#6BCF7F', 'None': '#4CAF50'})
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            for severity, count in severity_stats.items():
                color = get_severity_color(severity)
                st.markdown(f"""<div style="background: linear-gradient(135deg, {color}, {color}99); color: white; padding: 1rem; margin: 0.5rem 0; border-radius: 10px; text-align: center;"><h3 style="margin: 0;">{count}</h3><p style="margin: 0; opacity: 0.9;">{severity} Severity Diseases</p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #667eea; margin: 2rem 0;'>🚀 Quick Start Guide</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="info-card"><h3 style="text-align: center;">1️⃣ Upload Image</h3><p>Take or upload a clear photo of the affected plant part</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="info-card"><h3 style="text-align: center;">2️⃣ AI Analysis</h3><p>Our AI model analyzes the image and identifies diseases</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="info-card"><h3 style="text-align: center;">3️⃣ Get Results</h3><p>Receive detailed diagnosis and treatment recommendations</p></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_detection_page():
    """Display the disease detection page"""
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #667eea;'>🔬 Plant Disease Detection</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; margin-bottom: 2rem;'>Upload an image of your plant for AI-powered disease analysis</p>", unsafe_allow_html=True)
    predictor = load_model_predictor()
    if not predictor:
        st.error("Model could not be loaded. Please check if the model file exists.")
        return
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], help="Upload a clear image of the plant leaf or affected area")
    if uploaded_file is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyze_btn = st.button("🔍 Analyze Image", use_container_width=True)
        if analyze_btn:
            with st.spinner("🧠 AI is analyzing your image..."):
                try:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    processor = ImageProcessor()
                    image_array = processor.preprocess_image(temp_path)
                    features = processor.extract_features(temp_path)
                    result = predictor.predict(image_array)
                    disease_info = get_disease_info(result['primary_prediction']['class'])
                    os.remove(temp_path)
                    st.markdown("---")
                    primary = result['primary_prediction']
                    confidence_msg = create_confidence_message(primary['confidence'], result['confidence_level'])
                    severity_color = get_severity_color(disease_info.get('severity', 'Unknown'))
                    st.markdown(f"""<div class="prediction-result"><h2 style="text-align: center; margin-bottom: 1rem;">🎯 Diagnosis Result</h2><h3 style="color: white; text-align: center;">{format_disease_name(primary['class'])}</h3><p style="text-align: center; font-size: 1.2rem; margin: 1rem 0;">{confidence_msg}</p><div class="confidence-bar"><div class="confidence-fill" style="width: {primary['percentage']:.1f}%; background: linear-gradient(90deg, #4CAF50, #45a049);"></div></div><p style="text-align: center; margin-top: 0.5rem;">Confidence: {primary['percentage']:.1f}%</p></div>""", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""<div class="disease-info"><h3>🦠 Disease Information</h3><p><strong>Plant:</strong> {disease_info.get('plant', 'N/A')}</p><p><strong>Scientific Name:</strong> <em>{disease_info.get('scientific_name', 'N/A')}</em></p><p><strong>Severity:</strong> <span style="color: {severity_color}; font-weight: bold;">{disease_info.get('severity', 'Unknown')}</span></p><p><strong>Description:</strong> {disease_info.get('description', 'N/A')}</p></div>""", unsafe_allow_html=True)
                        if disease_info.get('symptoms'):
                            st.markdown("""<div class="disease-info"><h3>🔍 Symptoms</h3></div>""", unsafe_allow_html=True)
                            for symptom in disease_info['symptoms']:
                                st.markdown(f"• {symptom}")
                    with col2:
                        if disease_info.get('treatment'):
                            st.markdown("""<div class="disease-info"><h3>💊 Treatment Recommendations</h3></div>""", unsafe_allow_html=True)
                            for treatment in disease_info['treatment']:
                                st.markdown(f"• {treatment}")
                        if disease_info.get('prevention'):
                            st.markdown("""<div class="disease-info"><h3>🛡️ Prevention Methods</h3></div>""", unsafe_allow_html=True)
                            for prevention in disease_info['prevention']:
                                st.markdown(f"• {prevention}")
                    st.markdown("---")
                    st.markdown("<h3 style='color: #667eea;'>📊 Advanced Analysis</h3>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        confidence_chart = create_confidence_chart(result['top_predictions'])
                        if confidence_chart:
                            st.plotly_chart(confidence_chart, use_container_width=True)
                    with col2:
                        feature_chart = create_feature_comparison_chart(features)
                        if feature_chart:
                            st.plotly_chart(feature_chart, use_container_width=True)
                    if features:
                        st.markdown("### 🔬 Image Analysis Metrics")
                        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                        with metric_col1:
                            st.metric("Image Size", f"{features['dimensions'][0]}x{features['dimensions'][1]}")
                        with metric_col2:
                            st.metric("Brightness", f"{features['brightness']:.1f}")
                        with metric_col3:
                            st.metric("Contrast", f"{features['contrast']:.1f}")
                        with metric_col4:
                            st.metric("Edge Density", f"{features['edge_density']:.3f}")
                    st.markdown("### 🎲 Alternative Possibilities")
                    entropy = result.get('prediction_entropy', 0)
                    if entropy > 2.5:
                        st.warning("⚠️ The model detected multiple possible conditions. Consider taking another photo or consulting an expert.")
                    with st.expander("View All Top 5 Predictions"):
                        for i, pred in enumerate(result['top_predictions']):
                            disease_name = format_disease_name(pred['class'])
                            st.write(f"{i+1}. **{disease_name}** - {pred['percentage']:.1f}% confidence")
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
                    st.error("Please try uploading a different image or contact support.")
    else:
        st.markdown("""<div class="info-card"><h3>📸 Tips for Better Results</h3><ul><li>Use clear, well-lit photos</li><li>Focus on the affected plant parts (leaves, fruits, stems)</li><li>Avoid blurry or low-resolution images</li><li>Ensure the plant disease symptoms are clearly visible</li><li>Use natural lighting when possible</li></ul></div>""", unsafe_allow_html=True)
        st.markdown("### 🖼️ Try with Sample Images")
        st.markdown("Don't have a plant image? Try these sample images to see how the system works:")
        test_dir = os.path.join(BASE_PATH, "test")
        if os.path.exists(test_dir):
            sample_files = [f for f in os.listdir(test_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if sample_files:
                selected_sample = st.selectbox("Choose a sample image:", [""] + sample_files)
                if selected_sample:
                    sample_path = os.path.join(test_dir, selected_sample)
                    if os.path.exists(sample_path):
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            sample_image = Image.open(sample_path)
                            st.image(sample_image, caption=f"Sample: {selected_sample}", use_column_width=True)
                            if st.button("🔍 Analyze Sample Image", use_container_width=True):
                                with st.spinner("🧠 AI is analyzing the sample image..."):
                                    try:
                                        processor = ImageProcessor()
                                        image_array = processor.preprocess_image(sample_path)
                                        result = predictor.predict(image_array)
                                        disease_info = get_disease_info(result['primary_prediction']['class'])
                                        primary = result['primary_prediction']
                                        st.success(f"**Prediction:** {format_disease_name(primary['class'])} ({primary['percentage']:.1f}% confidence)")
                                        st.info(f"**Description:** {disease_info.get('description', 'N/A')}")
                                    except Exception as e:
                                        st.error(f"Error analyzing sample: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

def show_analytics_page():
    """Display the analytics and model performance page"""
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #667eea;'>📊 Model Analytics & Performance</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; margin-bottom: 2rem;'>Detailed insights into model performance and training metrics</p>", unsafe_allow_html=True)
    display_model_performance()
    st.markdown('</div>', unsafe_allow_html=True)

def show_database_page():
    """Display the disease database page"""
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #667eea;'>📚 Plant Disease Database</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; margin-bottom: 2rem;'>Comprehensive database of plant diseases with detailed information</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        plant_types = ['All'] + sorted(list(set([info.get('plant', '') for info in [get_disease_info(disease) for disease in get_all_diseases()] if info.get('plant')])))
        selected_plant = st.selectbox("Filter by Plant Type:", plant_types)
    with col2:
        severity_levels = ['All', 'Critical', 'High', 'Medium', 'Low', 'None']
        selected_severity = st.selectbox("Filter by Severity:", severity_levels)
    with col3:
        search_term = st.text_input("🔍 Search diseases:", placeholder="Enter disease name...")
    all_diseases = get_all_diseases()
    filtered_diseases = []
    for disease_key in all_diseases:
        disease_info = get_disease_info(disease_key)
        if selected_plant != 'All' and disease_info.get('plant', '') != selected_plant:
            continue
        if selected_severity != 'All' and disease_info.get('severity', '') != selected_severity:
            continue
        if search_term and search_term.lower() not in disease_info.get('name', '').lower():
            continue
        filtered_diseases.append((disease_key, disease_info))
    st.markdown(f"<p style='text-align: center; margin: 1rem 0;'>Found {len(filtered_diseases)} diseases</p>", unsafe_allow_html=True)
    if filtered_diseases:
        diseases_per_page = 12
        total_pages = (len(filtered_diseases) - 1) // diseases_per_page + 1
        if 'page' not in st.session_state:
            st.session_state.page = 1
        col1, col2, col3, col4, col5 = st.columns(5)
        with col3:
            page = st.selectbox("Page:", range(1, total_pages + 1), index=st.session_state.page - 1)
            st.session_state.page = page
        start_idx = (page - 1) * diseases_per_page
        end_idx = min(start_idx + diseases_per_page, len(filtered_diseases))
        for i in range(start_idx, end_idx, 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < end_idx:
                    disease_key, disease_info = filtered_diseases[i + j]
                    with col:
                        severity_color = get_severity_color(disease_info.get('severity', 'Unknown'))
                        st.markdown(f"""<div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; height: 400px; border-left: 4px solid {severity_color}; display: flex; flex-direction: column;"><h4 style="margin-top: 0; color: white;">{disease_info.get('name', 'Unknown')}</h4><p><strong>Plant:</strong> {disease_info.get('plant', 'N/A')}</p><p><strong>Severity:</strong> <span style="color: {severity_color}; font-weight: bold;">{disease_info.get('severity', 'Unknown')}</span></p><p style="flex-grow: 1; overflow: hidden;"><strong>Description:</strong> {disease_info.get('description', 'N/A')[:100]}{'...' if len(disease_info.get('description', '')) > 100 else ''}</p></div>""", unsafe_allow_html=True)
                        with st.expander(f"View Details - {disease_info.get('name', 'Unknown')}"):
                            if disease_info.get('symptoms'):
                                st.markdown("**🔍 Symptoms:**")
                                for symptom in disease_info['symptoms']:
                                    st.markdown(f"• {symptom}")
                            if disease_info.get('treatment'):
                                st.markdown("**💊 Treatment:**")
                                for treatment in disease_info['treatment']:
                                    st.markdown(f"• {treatment}")
                            if disease_info.get('prevention'):
                                st.markdown("**🛡️ Prevention:**")
                                for prevention in disease_info['prevention']:
                                    st.markdown(f"• {prevention}")
    else:
        st.info("No diseases found matching your search criteria.")
    st.markdown('</div>', unsafe_allow_html=True)

def show_about_page():
    """Display the about page"""
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #667eea;'>ℹ️ About KrushiAI</h2>", unsafe_allow_html=True)
    st.markdown("""<div class="info-card"><h3>🌾 Project Overview</h3><p style="font-size: 1.1rem; line-height: 1.6;">KrushiAI is an advanced plant disease detection system powered by deep learning and computer vision. Our mission is to help farmers, gardeners, and agricultural professionals quickly identify plant diseases and receive expert treatment recommendations.</p><p style="font-size: 1.1rem; line-height: 1.6;">Using state-of-the-art convolutional neural networks trained on thousands of plant images, KrushiAI can identify 38 different plant diseases across 15+ crop types with over 96 percent accuracy.</p></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="info-card"><h3>🔬 Technical Specifications</h3><ul style="font-size: 1.1rem; line-height: 1.8;"><li><strong>Model Architecture:</strong> Convolutional Neural Network</li><li><strong>Training Dataset:</strong> 50,000+ labeled plant images</li><li><strong>Accuracy:</strong> 96.5% validation accuracy</li><li><strong>Diseases Covered:</strong> 38 different diseases</li><li><strong>Crop Types:</strong> 15+ including fruits & vegetables</li><li><strong>Image Processing:</strong> Advanced preprocessing & enhancement</li><li><strong>Response Time:</strong> < 3 seconds per analysis</li></ul></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="info-card"><h3>🌱 Supported Crops</h3><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 1.1rem;"><div>🍎 Apple</div><div>🫐 Blueberry</div><div>🍒 Cherry</div><div>🌽 Corn</div><div>🍇 Grape</div><div>🍊 Orange</div><div>🍑 Peach</div><div>🫑 Bell Pepper</div><div>🥔 Potato</div><div>🍓 Strawberry</div><div>🍅 Tomato</div><div>🥒 Squash</div><div>🫘 Soybean</div><div>🫐 Raspberry</div><div>➕ And more...</div></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="info-card"><h3>⚙️ How It Works</h3><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;"><div style="text-align: center; padding: 1rem;"><h4>📸 Image Upload</h4><p>Users upload clear images of affected plant parts</p></div><div style="text-align: center; padding: 1rem;"><h4>🔍 Preprocessing</h4><p>Advanced image enhancement and normalization</p></div><div style="text-align: center; padding: 1rem;"><h4>🧠 AI Analysis</h4><p>Deep learning model analyzes visual patterns</p></div><div style="text-align: center; padding: 1rem;"><h4>📊 Results</h4><p>Detailed diagnosis with confidence scores</p></div><div style="text-align: center; padding: 1rem;"><h4>💡 Recommendations</h4><p>Expert treatment and prevention advice</p></div></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="info-card"><h3>🛠️ Technology Stack</h3><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;"><div><h4>🤖 Machine Learning</h4><ul><li>TensorFlow 2.13+</li><li>Keras</li><li>NumPy</li><li>OpenCV</li></ul></div><div><h4>🖥️ Frontend</h4><ul><li>Streamlit</li><li>Plotly</li><li>PIL (Pillow)</li><li>Custom CSS</li></ul></div><div><h4>📊 Data Science</h4><ul><li>Pandas</li><li>Matplotlib</li><li>Seaborn</li><li>Scikit-learn</li></ul></div></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="info-card"><h3>📋 Usage Guidelines</h3><div style="font-size: 1.1rem; line-height: 1.6;"><h4>✅ Best Practices:</h4><ul><li>Use high-resolution, clear images (minimum 224x224 pixels)</li><li>Ensure good lighting conditions</li><li>Focus on the affected plant parts</li><li>Avoid heavily processed or filtered images</li><li>Take multiple angles if symptoms are unclear</li></ul><h4>⚠️ Important Notes:</h4><ul><li>This tool is for guidance only - consult agricultural experts for critical decisions</li><li>Results may vary based on image quality and disease severity</li><li>Not all plant diseases may be covered in the current model</li><li>Environmental factors may affect accuracy</li></ul></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="info-card"><h3>📞 Support & Contact</h3><p style="font-size: 1.1rem; line-height: 1.6;">For technical support, feature requests, or general inquiries, please contact our team:</p><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;"><div style="text-align: center;"><h4>📧 Email</h4><p>support@krushiai.com</p></div><div style="text-align: center;"><h4>🐙 GitHub</h4><p>github.com/krushiai/plant-disease-detection</p></div><div style="text-align: center;"><h4>📚 Documentation</h4><p>docs.krushiai.com</p></div></div></div>""", unsafe_allow_html=True)
    analyzer = load_model_analyzer()
    stats = analyzer.get_training_stats() if analyzer else None
    st.markdown(f"""<div class="info-card" style="text-align: center;"><h3>ℹ️ Version Information</h3><p><strong>KrushiAI Version:</strong> 2.0.0</p><p><strong>Model Version:</strong> 1.0.0</p><p><strong>Last Updated:</strong> {datetime.now().strftime('%B %Y')}</p>{f'<p><strong>Model Accuracy:</strong> {stats.get("final_val_accuracy", 0):.1%}</p>' if stats else ''}</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================
# MAIN APPLICATION
# ============================

def show_page():
    """Main application runner"""
    st.markdown("""<div class="main-header"><h1>🌿 KrushiAI</h1><p>Advanced Plant Disease Detection System</p><p>Powered by Deep Learning & Computer Vision</p></div>""", unsafe_allow_html=True)

    # Check critical files exist before showing menu
    critical_files = [os.path.join(BASE_PATH, 'trained_plant_disease_model.keras')]
    missing_files = [f for f in critical_files if not os.path.exists(f)]

    if missing_files:
        st.error("❌ Critical files missing:")
        for file in missing_files:
            st.error(f"• {file}")
        st.error("Please ensure all required files are present in the project directory.")
        return

    selected = option_menu(
        menu_title=None,
        options=["🏠 Home", "🔬 Disease Detection", "📊 Analytics", "📚 Disease Database", "ℹ️ About"],
        icons=["house", "search", "graph-up", "book", "info-circle"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#667eea", "background-color": "rgba(255,255,255,0.1)", "color": "white", "border-radius": "10px", "margin": "5px"},
            "nav-link-selected": {"background-color": "#667eea"},
        }
    )

    if selected == "🏠 Home":
        show_home_page()
    elif selected == "🔬 Disease Detection":
        show_detection_page()
    elif selected == "📊 Analytics":
        show_analytics_page()
    elif selected == "📚 Disease Database":
        show_database_page()
    elif selected == "ℹ️ About":
        show_about_page()

show_page()
