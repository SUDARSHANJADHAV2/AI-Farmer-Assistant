# 🚀 KrushiAI - Quick Start Guide

## Start All Services

```powershell
# Navigate to project directory
cd C:\Users\SUDARSHAN\Desktop\AI-Farmer-Assistant

# Start all three backend services
.\start_all_services.ps1
```

This will start:
- **Crop Recommendation** → http://localhost:5000
- **Fertilizer Recommendation** → http://localhost:5001  
- **Disease Recognition** → http://localhost:5002

---

## Open Frontends in Browser

Once services are running, open these HTML files in your browser:

1. **Crop Recommendation**:
   ```
   C:\Users\SUDARSHAN\Desktop\AI-Farmer-Assistant\KrushiAI-Crop-Recommendation\index.html
   ```

2. **Fertilizer Recommendation**:
   ```
   C:\Users\SUDARSHAN\Desktop\AI-Farmer-Assistant\KrushiAI-Fertilizer-Recommendation\frontend\index.html
   ```

3. **Disease Recognition**:
   ```
   C:\Users\SUDARSHAN\Desktop\AI-Farmer-Assistant\KrushiAI-Disease-Recognition\frontend\index.html
   ```

---

## Test Each Module

### 1. Crop Recommendation
- Fill in soil parameters (N, P, K, pH)
- Fill in climate parameters (Temperature, Humidity, Rainfall)
- Click "Get Recommendation"
- See recommended crop with detailed info

### 2. Fertilizer Recommendation
- Select soil type from dropdown
- Select crop type from dropdown
- Enter environmental parameters
- Enter NPK values
- Click "Get Recommendation"
- See fertilizer recommendation with application details

### 3. Disease Recognition
- Click "Choose an image" 
- Upload a plant leaf image (JPG/PNG)
- Click "Predict"
- See disease classification with confidence scores

---

## Stop Services

Press `Ctrl + C` in the PowerShell window running the services.

---

## 📋 Everything is Fixed!

✅ Crop Recommendation - Working  
✅ Fertilizer Recommendation - Fixed & Working  
✅ Disease Recognition - Fixed & Working  

All modules tested and verified! 🎉

---

For detailed documentation, see:
- `SETUP_AND_TEST.md` - Comprehensive guide
- `FIX_SUMMARY.md` - What was fixed and how
