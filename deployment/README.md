# Sign Language Recognition API Deployment

This directory contains everything needed to deploy the Malaysian Sign Language (MSL) recognition model as a REST API.

## Overview

- **Model**: PyTorch LSTM (2 layers, 64 hidden units)
- **Input**: MediaPipe landmarks (258 features: pose + hands)
- **Output**: Gesture classification (11 classes)
- **Framework**: FastAPI
- **Deployment**: Hugging Face Spaces (recommended)

## Gesture Classes

The model recognizes 11 Malaysian Sign Language gestures:
1. minum (drink)
2. berjalan (walk)
3. berlari (run)
4. bola (ball)
5. dari (from)
6. hi (hello)
7. jangan (don't)
8. mohon (please)
9. pen (pen)
10. teh tarik (pulled tea)
11. tolong (help)

## Project Structure

```
deployment/
├── app.py                  # FastAPI application
├── model.py                # PyTorch model definition
├── preprocessing.py        # MediaPipe utilities
├── requirements.txt        # Python dependencies
├── trained_model.pth       # Model weights (489KB)
├── README.md              # This file
└── test_api.py            # Local testing script
```

## API Endpoints

### 1. Health Check
```bash
GET /
GET /health
```
Returns API status and configuration.

### 2. Predict Gesture
```bash
POST /predict
```
**Request Body:**
```json
{
  "frame": "base64_encoded_image_string",
  "session_id": "unique_session_id"
}
```

**Response:**
```json
{
  "gesture": "hi",
  "confidence": 0.95,
  "all_predictions": {
    "minum": 0.01,
    "berjalan": 0.02,
    "hi": 0.95,
    ...
  },
  "sequence_length": 30,
  "message": "Predicted: hi"
}
```

### 3. Reset Session
```bash
POST /reset?session_id=your_session_id
```
Clears the frame buffer for a specific session.

### 4. Get Gestures
```bash
GET /gestures
```
Returns list of all supported gestures.

## How It Works

1. **Frame Processing**: Client sends base64-encoded video frames
2. **Landmark Extraction**: MediaPipe extracts 258 landmarks per frame
3. **Sequence Building**: API accumulates 30 frames per session
4. **Prediction**: LSTM model processes the sequence and returns probabilities
5. **Confidence Threshold**: Only predictions above 50% confidence are shown

---

## Local Testing

### Prerequisites
- Python 3.9+
- Webcam (optional, for testing)

### Setup

1. **Install dependencies:**
```bash
cd deployment
pip install -r requirements.txt
```

2. **Run the API locally:**
```bash
python app.py
```

The API will start at `http://localhost:7860`

3. **Test with the provided script:**
```bash
python test_api.py
```

4. **Manual testing:**
Open your browser and visit:
- `http://localhost:7860/docs` - Interactive API documentation
- `http://localhost:7860/health` - Health check

---

## Deployment to Hugging Face Spaces

### Step 1: Create Hugging Face Account
1. Go to https://huggingface.co/join
2. Create a free account
3. Verify your email

### Step 2: Create a New Space
1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Configure:
   - **Space name**: `msl-recognition-api` (or your choice)
   - **License**: Apache 2.0
   - **Select SDK**: Docker (for custom FastAPI deployment)
   - **Space hardware**: CPU basic (free tier)
   - **Visibility**: Public or Private

### Step 3: Prepare Files
Create a `Dockerfile` in the deployment directory:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Step 4: Deploy

**Option A: Using Git (Recommended)**

```bash
# Navigate to deployment directory
cd deployment

# Initialize git repository
git init

# Add Hugging Face remote (replace USERNAME and SPACE_NAME)
git remote add origin https://huggingface.co/spaces/USERNAME/SPACE_NAME

# Add all files
git add .

# Commit
git commit -m "Initial deployment of MSL recognition API"

# Push to Hugging Face
git push origin main
```

**Option B: Using Web Interface**

1. In your Space, click "Files and versions"
2. Click "Add file" → "Upload files"
3. Upload all files from the `deployment` directory:
   - `app.py`
   - `model.py`
   - `preprocessing.py`
   - `requirements.txt`
   - `trained_model.pth`
   - `Dockerfile`
4. Click "Commit changes to main"

### Step 5: Wait for Build
- Hugging Face will automatically build your Space
- This takes 5-10 minutes
- Monitor the build logs in the "Logs" tab

### Step 6: Test Your Deployment
Once deployed, your API will be available at:
```
https://USERNAME-SPACE_NAME.hf.space
```

Test endpoints:
- `https://USERNAME-SPACE_NAME.hf.space/health`
- `https://USERNAME-SPACE_NAME.hf.space/docs`

---

## Alternative Deployment: Render

If you prefer Render:

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: msl-recognition-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### Step 3: Environment Variables
Add in Render dashboard:
```
PYTHON_VERSION=3.9.0
```

### Step 4: Deploy
- Render will automatically deploy on git push
- Your API will be at: `https://msl-recognition-api.onrender.com`

---

## Performance Optimization

### For Production:
1. **Use GPU**: Upgrade to GPU hardware on Hugging Face (paid)
2. **Batch Processing**: Process multiple frames simultaneously
3. **Model Quantization**: Reduce model size with `torch.quantization`
4. **Caching**: Use Redis for session management
5. **Rate Limiting**: Add rate limits to prevent abuse

### Current Limitations (Free Tier):
- CPU-only inference
- ~100-200ms latency per prediction
- Limited concurrent users
- No persistent storage (sessions reset on restart)

---

## Troubleshooting

### Build Fails
- Check Python version (needs 3.9+)
- Verify all dependencies in requirements.txt
- Check Dockerfile syntax

### Model Not Loading
- Ensure `trained_model.pth` is in the correct directory
- Check file size (should be ~489KB)
- Verify PyTorch version compatibility

### Slow Predictions
- Upgrade to GPU hardware
- Reduce sequence length (current: 30 frames)
- Use model quantization

### CORS Errors
- Check CORS middleware in `app.py`
- Add your frontend domain to `allow_origins`

---

## API Usage Examples

### Python Client
```python
import requests
import base64

# Read image
with open("frame.jpg", "rb") as f:
    frame_b64 = base64.b64encode(f.read()).decode()

# Make prediction
response = requests.post(
    "http://localhost:7860/predict",
    json={"frame": frame_b64, "session_id": "test_session"}
)

print(response.json())
```

### JavaScript Client
```javascript
// Capture frame from webcam
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');
context.drawImage(video, 0, 0, canvas.width, canvas.height);
const frameB64 = canvas.toDataURL('image/jpeg').split(',')[1];

// Send to API
fetch('http://localhost:7860/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    frame: frameB64,
    session_id: 'user_123'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## Next Steps

After deploying the API:
1. Note your API URL
2. Create the web app frontend (separate repository)
3. Connect frontend to this API
4. Test end-to-end with webcam

---

## Support

For issues or questions:
- Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- Check the [Hugging Face Spaces documentation](https://huggingface.co/docs/hub/spaces)
- Review the build logs in your Space

## License

Apache 2.0
