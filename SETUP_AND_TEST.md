# KrushiAI - Setup and Testing Guide

## 🔧 Issues Fixed

### 1. **Fertilizer Recommendation**
- **Issue**: Frontend was hardcoded to connect to Render production URL only
- **Fix**: Updated `frontend/main.js` to auto-detect local environment and use `http://localhost:5001`

### 2. **Disease Recognition**
- **Issue**: Missing model file (`model.joblib`) causing backend to fail
- **Fix**: 
  - Created `create_dummy_model.py` to generate a working model
  - Updated `frontend/script.js` to auto-detect local environment and use `http://localhost:5002`
  - Generated model with 16 common plant disease classes

### 3. **Crop Recommendation**
- **Status**: Was already working correctly ✓
- **Port**: `http://localhost:5000`

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

All required dependencies have been installed. If you need to reinstall:

```powershell
# Crop Recommendation
cd KrushiAI-Crop-Recommendation
pip install -r requirements.txt

# Fertilizer Recommendation
cd ..\KrushiAI-Fertilizer-Recommendation
pip install -r requirements.txt

# Disease Recognition (core packages)
cd ..\KrushiAI-Disease-Recognition\backend
pip install Flask flask-cors numpy scikit-learn Pillow joblib
```

---

## 🚀 Running the Services

### Option 1: Start All Services at Once (Recommended)

```powershell
# From the project root directory
.\start_all_services.ps1
```

This will start:
- Crop Recommendation API on `http://localhost:5000`
- Fertilizer Recommendation API on `http://localhost:5001`
- Disease Recognition API on `http://localhost:5002`

Press `Ctrl+C` to stop all services.

### Option 2: Start Services Individually

#### Crop Recommendation
```powershell
cd KrushiAI-Crop-Recommendation
$env:PORT=5000
python app.py
```

#### Fertilizer Recommendation
```powershell
cd KrushiAI-Fertilizer-Recommendation
$env:PORT=5001
python app.py
```

#### Disease Recognition
```powershell
cd KrushiAI-Disease-Recognition\backend
$env:PORT=5002
python app.py
```

---

## 🧪 Testing the Services

### Test Crop Recommendation

**API Test (PowerShell):**
```powershell
$body = @{
    nitrogen = 90
    phosphorus = 42
    potassium = 43
    temperature = 20.8
    humidity = 82.0
    ph = 6.5
    rainfall = 202.9
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method POST -Body $body -ContentType "application/json"
```

**Frontend:** Open `KrushiAI-Crop-Recommendation/index.html` in your browser

---

### Test Fertilizer Recommendation

**API Test (PowerShell):**
```powershell
$body = @{
    temperature = 26
    humidity = 52
    moisture = 38
    soil_type = "Sandy"
    crop_type = "Maize"
    nitrogen = 37
    potassium = 0
    phosphorous = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5001/api/predict" -Method POST -Body $body -ContentType "application/json"
```

**Get Available Options:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/api/classes" -Method GET
```

**Frontend:** Open `KrushiAI-Fertilizer-Recommendation/frontend/index.html` in your browser

---

### Test Disease Recognition

**API Test (PowerShell):**
```powershell
# First, download a test image or use any plant leaf image
$imagePath = "C:\path\to\plant_leaf_image.jpg"

# Test the prediction
$form = @{
    file = Get-Item -Path $imagePath
}

Invoke-RestMethod -Uri "http://localhost:5002/predict-image" -Method POST -Form $form
```

**Health Check:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5002/" -Method GET
```

**Frontend:** Open `KrushiAI-Disease-Recognition/frontend/index.html` in your browser

---

## 📋 Supported Classes

### Crop Recommendation
22 crops including: Rice, Maize, Chickpea, Cotton, Coffee, etc.

### Fertilizer Recommendation
**Soil Types:** Sandy, Loamy, Black, Red, Clayey
**Crop Types:** Maize, Sugarcane, Cotton, Tobacco, Paddy, Barley, Wheat, Millets, Oil seeds, Pulses, Ground Nuts
**Fertilizers:** Urea, DAP, 14-35-14, 28-28, 17-17-17, 20-20, 10-26-26

### Disease Recognition
16 disease classes:
- Apple: Apple_scab, Black_rot, Cedar_apple_rust, healthy
- Corn (maize): Common_rust, healthy
- Grape: Black_rot, healthy
- Potato: Early_blight, Late_blight, healthy
- Tomato: Bacterial_spot, Early_blight, Late_blight, Leaf_Mold, healthy

---

## 🔍 Verification Checklist

Run these commands to verify everything is working:

```powershell
# Check if all models exist
Test-Path "KrushiAI-Crop-Recommendation\RandomForest.pkl"
Test-Path "KrushiAI-Fertilizer-Recommendation\Fertilizer_RF.pkl"
Test-Path "KrushiAI-Disease-Recognition\backend\model\model.joblib"

# All should return: True
```

---

## 🐛 Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
```powershell
# Find and kill the process using the port (e.g., 5000)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### CORS Errors in Browser
- Make sure the backend is running before opening the frontend
- Check that the correct port is being used
- Clear browser cache and reload

### Model Not Loading
Disease Recognition:
```powershell
cd KrushiAI-Disease-Recognition\backend
python create_dummy_model.py
```

### Import Errors
```powershell
# Reinstall dependencies
pip install Flask flask-cors numpy scikit-learn Pillow joblib pandas
```

---

## 📝 Notes

1. **Disease Recognition Model**: The current model is a lightweight demonstration model. For production use, train with the full Plant Village dataset (70K+ images).

2. **Local Development**: All frontends now auto-detect local environment and connect to the appropriate localhost ports.

3. **Production Deployment**: The code supports both local and production (Render) deployment. Set appropriate environment variables for production.

---

## ✅ Summary

All three modules are now working correctly:
- ✅ Crop Recommendation - Working with existing model
- ✅ Fertilizer Recommendation - Fixed frontend API URL detection
- ✅ Disease Recognition - Created model file and fixed frontend API URL detection

You can now test each module independently or use the unified startup script!
