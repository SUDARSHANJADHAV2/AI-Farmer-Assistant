<div align="center">
    <h1>AgriSens : AI-POWERED SMART FARMING ASSISTANT</h1>
    <p>A unified, next-generation platform for intelligent agriculture.</p>
</div>

<div align="center">
    <h3>Live Demo Link : https://agrisens.netlify.app/ </h3>
</div>

![New Dashboard Screenshot](https://github.com/user-attachments/assets/5b945e7d-bbb0-4463-b06f-681445e102bd)

## Overview

AgriSens is an innovative, AI-powered solution that provides a unified dashboard for smart farming. It integrates multiple advanced tools to help farmers improve productivity and make data-driven decisions. The platform has been refactored into a single, cohesive Streamlit application, offering a seamless user experience.

Core features include a Smart Crop Recommendation system, a state-of-the-art Plant Disease Identification tool, tailored Fertilizer Recommendations, and a dynamic Weather Forecast dashboard. The latest version introduces **User Profiles**, allowing farmers to save their farm's data for a personalized experience.

## ✨ Key Features

- [x] **Unified Dashboard**: A single, easy-to-navigate interface for all agricultural tools.
- [x] **User Profiles & Farm Management**: Create an account to save your farm's location and soil type for personalized recommendations.
- [x] **Smart Crop Recommendation**: Leverages machine learning to suggest the most suitable crops based on soil nutrients and climate data.
- [x] **Plant Disease Identification**: Uses a powerful CNN to accurately detect 38 different plant diseases from uploaded images.
- [x] **Fertilizer Recommendation**: Offers customized fertilizer recommendations based on soil quality and crop needs.
- [x] **Dynamic Weather Forecast**: A real-time weather dashboard integrated into the home page.
- [x] **Consistent, Professional UI/UX**: A modern, dark-themed interface applied across the entire application.

## 🚀 Getting Started

Follow these steps to run the AgriSens dashboard on your local machine.

### Prerequisites
- Python 3.8+
- Pip for package management

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/AgriSens.git
    cd AgriSens
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
    *Note: You may need to install separate `requirements.txt` files from the sub-directories as well, or consolidate them.*

### Running the Application

1.  **Launch the Streamlit Dashboard:**
    The entire application is now run from a single entry point.
    ```bash
    streamlit run dashboard.py
    ```

2.  **Access the Dashboard:**
    Open your web browser and go to the local URL provided by Streamlit (usually `http://localhost:8501`).

## ⚙️ System Architecture

The application is a multi-page Streamlit app with a centralized structure.

- **`dashboard.py`**: The main entry point and home page.
- **`pages/`**: Contains the individual tool pages (Crop Recommendation, Fertilizer, Disease).
- **`lib/`**: A centralized library for shared code, including database operations and helper functions.
- **`css/`**: Contains the global stylesheet for a consistent UI.
- **`agrisens.db`**: An SQLite database for storing user and farm profile data.

<details>
<summary>💻 View System Architecture Diagram</summary>

![20250124_135249](https://github.com/user-attachments/assets/1c660b6b-5b70-440e-a453-bf802b490bdc)

</details>

## 👨‍💻 Contributors
- [Ravikant Diwakar](https://github.com/ravikant-diwakar)
- [Amit Kumar](https://github.com/AMITKUMAR7970)
- [Gaurav Kumar](https://github.com/Gauravkumar1741)
- Aditya Chaudhary

## 📷 Screenshots

*Screenshots have been updated to reflect the new, unified dashboard interface.*

| Main Dashboard | Crop Recommendation |
| :---: | :---: |
| *New dashboard screenshot placeholder* | *New crop recommendation screenshot placeholder* |

| Fertilizer Recommendation | Disease Detection |
| :---: | :---: |
| *New fertilizer screenshot placeholder* | *New disease detection screenshot placeholder* |

## 📧 Contact

If you have any questions or feedback, feel free to reach out to us at [🔗Link](https://agrisens.netlify.app/form/).
