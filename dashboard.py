import streamlit as st
import base64
from PIL import Image
from lib.weather import get_weather_data, get_weather_icon_url
from lib import database as db

st.set_page_config(
    page_title="AgriSens - AI-Powered Smart Farming",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('css/streamlit_style.css')

# --- Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 0

# --- Sidebar ---
st.sidebar.title("Dashboard Controls")

# Authentication Logic
if st.session_state['logged_in']:
    st.sidebar.success(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['user_id'] = 0
        st.experimental_rerun()

    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/4_Farm_Profile.py", label="Your Farm Profile")


else:
    auth_choice = st.sidebar.radio("Login / Sign Up", ["Login", "Sign Up"])

    with st.sidebar.form(key='auth_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label=auth_choice)

        if submit_button:
            if auth_choice == "Login":
                user = db.check_user(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user['username']
                    st.session_state['user_id'] = user['id']
                    st.experimental_rerun()
                else:
                    st.sidebar.error("Invalid username or password")

            elif auth_choice == "Sign Up":
                if db.add_user(username, password):
                    st.sidebar.success("Account created! Please log in.")
                else:
                    st.sidebar.error("Username already exists.")

st.sidebar.markdown("---")

# Weather Section in Sidebar
city = st.sidebar.text_input("Enter City for Weather", "New Delhi")
if st.sidebar.button("Get Weather", use_container_width=True):
    st.session_state['weather_city'] = city

# --- Main Content Area ---
st.markdown("""
<div class="main-header">
    <h1>🌾 AgriSens</h1>
    <p>Your AI-Powered Smart Farming Assistant</p>
</div>
""", unsafe_allow_html=True)

# Display weather if city is set
if 'weather_city' in st.session_state and st.session_state['weather_city']:
    weather_data = get_weather_data(st.session_state['weather_city'])
    if weather_data:
        st.markdown(f"### Current Weather in {weather_data['name']}, {weather_data['sys']['country']}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image(get_weather_icon_url(weather_data['weather'][0]['icon']), width=100)
            st.markdown(f"**{weather_data['weather'][0]['description'].title()}**")
        with col2:
            st.metric(label="Temperature", value=f"{weather_data['main']['temp']} °C", delta=f"Feels like {weather_data['main']['feels_like']} °C")
        with col3:
            st.metric(label="Humidity", value=f"{weather_data['main']['humidity']}%")
        with col4:
            st.metric(label="Wind Speed", value=f"{weather_data['wind']['speed']} m/s")
        st.markdown("---")

# Default Home Page Content
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.markdown("""
<div class="info-card" style="text-align: center;">
    <h2 style="color: white; font-weight: 700;">Welcome to the Future of Farming</h2>
    <p style="font-size: 1.2rem; line-height: 1.6;">
        AgriSens combines the power of Artificial Intelligence with agricultural science to bring you a suite of tools designed to boost your productivity, increase yields, and promote sustainable farming practices.
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #667eea; margin: 2rem 0;'>🚀 Our Features</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""<div class="stat-card"><h3>🌱</h3><h4>Crop Recommendation</h4><p>Get intelligent recommendations for the best crops to plant based on your soil and climate conditions.</p></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class="stat-card"><h3>🌿</h3><h4>Fertilizer Advice</h4><p>Receive precise fertilizer recommendations to optimize nutrient management for your selected crops.</p></div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="stat-card"><h3>🔬</h3><h4>Disease Detection</h4><p>Upload an image of a plant leaf to instantly detect diseases and get treatment advice.</p></div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
