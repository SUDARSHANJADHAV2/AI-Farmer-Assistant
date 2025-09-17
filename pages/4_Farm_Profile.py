import streamlit as st
from lib import database as db

st.set_page_config(
    page_title="Your Farm Profile - AgriSens",
    page_icon="🧑‍🌾",
    layout="wide"
)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('css/streamlit_style.css')


st.markdown("""
<div class="main-header">
    <h1 style="color: white;">🧑‍🌾 Your Farm Profile</h1>
    <p>Manage your farm's details for personalized recommendations</p>
</div>
""", unsafe_allow_html=True)

# --- Check Login Status ---
if not st.session_state.get('logged_in'):
    st.warning("Please log in to manage your farm profile.")
    st.stop()

# --- Load Farm Details ---
user_id = st.session_state.get('user_id')
farm_details = db.get_farm_details(user_id)

# Set default values for the form
default_name = farm_details['farm_name'] if farm_details else "My Farm"
default_location = farm_details['location'] if farm_details else "New Delhi"
default_soil = farm_details['soil_type'] if farm_details else "Loamy" # A common default

# --- Profile Management Form ---
st.markdown("### Edit Your Farm's Information")

with st.form("farm_profile_form"):
    farm_name = st.text_input("Farm Name", value=default_name)
    location = st.text_input("Default Location (City)", value=default_location, help="This will be used for weather forecasts.")

    # Get available soil types from the fertilizer recommendation model's encoder
    # This is a bit of a hack, but it ensures consistency.
    # A better solution would be a centralized config file.
    try:
        import pickle
        soil_encoder = pickle.load(open("KrushiAI-Fertilizer-Recommendation/soil_encoder.pkl", "rb"))
        soil_types = soil_encoder.classes_

        # Find the index of the default soil type
        try:
            default_index = list(soil_types).index(default_soil)
        except ValueError:
            default_index = 0 # Default to the first item if not found

        soil_type = st.selectbox(
            "Default Soil Type",
            options=soil_types,
            index=default_index,
            help="This will be pre-selected in the recommendation tools."
        )
    except Exception as e:
        st.error(f"Could not load soil types: {e}")
        soil_type = st.text_input("Default Soil Type", value=default_soil)


    submitted = st.form_submit_button("Save Profile", use_container_width=True)

    if submitted:
        if db.update_farm_details(user_id, farm_name, location, soil_type):
            st.success("Your farm profile has been updated successfully!")
        else:
            st.error("There was an error saving your profile. Please try again.")

st.markdown("---")
st.info("The information saved here will be used to pre-fill inputs in the Crop and Fertilizer recommendation tools, saving you time.")
