---
title: Malaysian Sign Language Recognition API
emoji: 🤟
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: apache-2.0
---

# Malaysian Sign Language (MSL) Recognition API

Real-time sign language recognition using MediaPipe landmarks and LSTM neural network.

## 🎯 Features

- **Real-time Recognition**: Process video frames in real-time
- **11 Gestures**: Recognizes 11 common Malaysian Sign Language gestures
- **High Accuracy**: 87.5% test accuracy
- **REST API**: Easy integration with any frontend
- **Session Management**: Maintains frame sequences per user

## 🤖 Supported Gestures

| Gesture | Meaning |
|---------|---------|
| minum | drink |
| berjalan | walk |
| berlari | run |
| bola | ball |
| dari | from |
| hi | hello |
| jangan | don't |
| mohon | please |
| pen | pen |
| teh tarik | pulled tea |
| tolong | help |

## 🚀 Quick Start

### API Endpoints

#### 1. Health Check
```bash
GET https://YOUR-SPACE-URL.hf.space/health
```

#### 2. Predict Gesture
```bash
POST https://YOUR-SPACE-URL.hf.space/predict
Content-Type: application/json

{
  "frame": "base64_encoded_image",
  "session_id": "unique_user_id"
}
```

#### 3. Get Supported Gestures
```bash
GET https://YOUR-SPACE-URL.hf.space/gestures
```

## 📖 How to Use

### Python Example
```python
import requests
import base64

# Read and encode frame
with open("frame.jpg", "rb") as f:
    frame_b64 = base64.b64encode(f.read()).decode()

# Make prediction
response = requests.post(
    "https://YOUR-SPACE-URL.hf.space/predict",
    json={"frame": frame_b64, "session_id": "user_123"}
)

result = response.json()
print(f"Gesture: {result['gesture']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### JavaScript Example
```javascript
// Capture from webcam
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');
context.drawImage(videoElement, 0, 0, 640, 480);
const frameB64 = canvas.toDataURL('image/jpeg').split(',')[1];

// Send to API
fetch('https://YOUR-SPACE-URL.hf.space/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    frame: frameB64,
    session_id: 'user_123'
  })
})
.then(res => res.json())
.then(data => {
  console.log(`Gesture: ${data.gesture}`);
  console.log(`Confidence: ${data.confidence}`);
});
```

## 🏗️ Architecture

- **Frontend**: Captures webcam frames
- **Preprocessing**: MediaPipe extracts 258 landmark features
- **Model**: 2-layer LSTM (64 hidden units)
- **Output**: Gesture classification with confidence scores

## 📊 Model Performance

- **Test Accuracy**: 87.5%
- **Training Set**: 561 sequences
- **Validation Set**: 81 sequences
- **Test Set**: 161 sequences
- **Sequence Length**: 30 frames

## 🔧 Technical Details

- **Framework**: FastAPI + PyTorch
- **Feature Extraction**: MediaPipe Holistic (v0.10.21)
- **Input Features**: 258 (33×4 pose + 21×3 left hand + 21×3 right hand)
- **Model Architecture**: LSTM → Dropout → Dense → Softmax
- **Confidence Threshold**: 50%

## 📝 API Documentation

Interactive API documentation is available at:
```
https://YOUR-SPACE-URL.hf.space/docs
```

## ⚡ Performance

- **Latency**: ~100-200ms per frame (CPU)
- **Sequence Requirement**: 30 frames for prediction
- **Frame Rate**: Supports 15-30 FPS

## 🤝 Integration

This API is designed to be integrated with a web application. Check out the companion frontend repository for a complete implementation.

## 📜 License

Apache 2.0

## 🙏 Acknowledgments

Built with:
- [MediaPipe](https://google.github.io/mediapipe/)
- [PyTorch](https://pytorch.org/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**Note**: Replace `YOUR-SPACE-URL` with your actual Hugging Face Space URL after deployment.
