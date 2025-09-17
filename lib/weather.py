import requests
import streamlit as st

API_KEY = "10932ac8ddf82cfc65e0741c31f0897e"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city):
    """
    Fetches weather data for a given city from the OpenWeatherMap API.
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  # For Celsius
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            st.error(f"City not found: {city}. Please check the spelling.")
        elif response.status_code == 401:
            st.error("Invalid API key. Please check your OpenWeatherMap API key.")
        else:
            st.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"An error occurred: {req_err}")
    return None

def get_weather_icon_url(icon_code):
    """
    Returns the URL for a weather icon.
    """
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
