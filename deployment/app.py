"""
FastAPI application for Sign Language Recognition API
"""
import os
import torch
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import mediapipe as mp

from model import CustomLSTM
from preprocessing import decode_base64_image, process_frame


# Initialize FastAPI app
app = FastAPI(
    title="Sign Language Recognition API",
    description="Real-time Malaysian Sign Language (MSL) recognition using MediaPipe and LSTM",
    version="1.0.0"
)

# Enable CORS for web app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gesture classes
GESTURES = [
    'minum', 'berjalan', 'berlari', 'bola', 'dari',
    'hi', 'jangan', 'mohon', 'pen', 'teh tarik', 'tolong'
]

# Configuration
INPUT_SIZE = 258
HIDDEN_SIZE = 64
NUM_CLASSES = len(GESTURES)
SEQUENCE_LENGTH = 10
CONFIDENCE_THRESHOLD = 0.5

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load model
model = CustomLSTM(INPUT_SIZE, HIDDEN_SIZE, NUM_CLASSES).to(device)
model_path = "trained_model.pth"

try:
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print(f"Model loaded successfully from {model_path}")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

# Initialize MediaPipe
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Store sequences for each session (in production, use Redis or similar)
# Key: session_id, Value: list of keypoints
sequences = {}


# Request/Response models
class FrameRequest(BaseModel):
    frame: str  # Base64 encoded image
    session_id: str = "default"


class PredictionResponse(BaseModel):
    gesture: str
    confidence: float
    all_predictions: Dict[str, float]
    sequence_length: int
    message: str


class HealthResponse(BaseModel):
    status: str
    device: str
    model_loaded: bool
    gestures: List[str]


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "device": str(device),
        "model_loaded": True,
        "gestures": GESTURES
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "device": str(device),
        "model_loaded": True,
        "gestures": GESTURES
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: FrameRequest):
    """
    Process a single frame and return prediction.

    The API maintains a sequence buffer for each session_id.
    Predictions are only made when 30 frames have been accumulated.

    Args:
        request: FrameRequest containing base64 encoded frame and session_id

    Returns:
        PredictionResponse with gesture prediction and confidence
    """
    try:
        # Decode frame
        frame = decode_base64_image(request.frame)

        # Process frame and extract keypoints
        keypoints = process_frame(frame, holistic)

        # Initialize session if not exists
        if request.session_id not in sequences:
            sequences[request.session_id] = []

        # Add keypoints to sequence (only if hands detected)
        if keypoints is not None:
            sequences[request.session_id].append(keypoints)

            # Keep only last 30 frames
            sequences[request.session_id] = sequences[request.session_id][-SEQUENCE_LENGTH:]

        # Get current sequence length
        current_length = len(sequences[request.session_id])

        # Check if we have enough frames for prediction
        if current_length < SEQUENCE_LENGTH:
            return {
                "gesture": "collecting_frames",
                "confidence": 0.0,
                "all_predictions": {},
                "sequence_length": current_length,
                "message": f"Collecting frames... {current_length}/{SEQUENCE_LENGTH}"
            }

        # Make prediction
        sequence = sequences[request.session_id][-SEQUENCE_LENGTH:]
        input_tensor = torch.tensor(
            np.expand_dims(sequence, axis=0),
            dtype=torch.float32
        ).to(device)

        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)[0]

        # Get predictions
        max_prob = torch.max(probabilities).item()
        max_idx = torch.argmax(probabilities).item()
        predicted_gesture = GESTURES[max_idx]

        # Create all predictions dict
        all_preds = {
            GESTURES[i]: float(probabilities[i].item())
            for i in range(len(GESTURES))
        }

        # Determine message
        if max_prob >= CONFIDENCE_THRESHOLD:
            message = f"Predicted: {predicted_gesture}"
        else:
            message = "Low confidence - keep signing"

        return {
            "gesture": predicted_gesture,
            "confidence": max_prob,
            "all_predictions": all_preds,
            "sequence_length": current_length,
            "message": message
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/reset")
async def reset_session(session_id: str = "default"):
    """
    Reset the sequence buffer for a session.

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    if session_id in sequences:
        sequences[session_id] = []
    return {"message": f"Session {session_id} reset successfully"}


@app.get("/gestures")
async def get_gestures():
    """
    Get list of all supported gestures.

    Returns:
        List of gesture names
    """
    return {"gestures": GESTURES, "count": len(GESTURES)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
