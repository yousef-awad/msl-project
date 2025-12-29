"""
Preprocessing utilities for MediaPipe landmark extraction
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple


# Initialize MediaPipe
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


def mediapipe_detection(image: np.ndarray, model) -> Tuple[np.ndarray, object]:
    """
    Process image with MediaPipe Holistic model.

    Args:
        image: Input frame (BGR format)
        model: MediaPipe Holistic model instance

    Returns:
        Processed image and detection results
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results


def extract_keypoints(results) -> np.ndarray:
    """
    Extract keypoints from MediaPipe detection results.

    Features extracted:
    - Pose landmarks: 33 points × 4 values (x, y, z, visibility) = 132 features
    - Left hand landmarks: 21 points × 3 values (x, y, z) = 63 features
    - Right hand landmarks: 21 points × 3 values (x, y, z) = 63 features
    Total: 258 features

    Args:
        results: MediaPipe detection results

    Returns:
        Flattened array of 258 features
    """
    # Extract pose landmarks (33 points × 4 features = 132)
    pose = np.array([
        [res.x, res.y, res.z, res.visibility]
        for res in results.pose_landmarks.landmark
    ]).flatten() if results.pose_landmarks else np.zeros(33 * 4)

    # Extract left hand landmarks (21 points × 3 features = 63)
    lh = np.array([
        [res.x, res.y, res.z]
        for res in results.left_hand_landmarks.landmark
    ]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)

    # Extract right hand landmarks (21 points × 3 features = 63)
    rh = np.array([
        [res.x, res.y, res.z]
        for res in results.right_hand_landmarks.landmark
    ]).flatten() if results.right_hand_landmarks else np.zeros(21 * 3)

    return np.concatenate([pose, lh, rh])


def process_frame(frame: np.ndarray, holistic_model) -> Optional[np.ndarray]:
    """
    Process a single frame and extract keypoints.

    Args:
        frame: Input frame (BGR format)
        holistic_model: MediaPipe Holistic model instance

    Returns:
        Keypoints array (258 features) or None if no hands detected
    """
    _, results = mediapipe_detection(frame, holistic_model)

    # Only process if at least one hand is detected
    if results.left_hand_landmarks or results.right_hand_landmarks:
        keypoints = extract_keypoints(results)
        return keypoints

    return None


def decode_base64_image(base64_string: str) -> np.ndarray:
    """
    Decode base64 string to numpy array (image).

    Args:
        base64_string: Base64 encoded image

    Returns:
        Decoded image as numpy array
    """
    import base64

    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    # Decode base64 to bytes
    img_bytes = base64.b64decode(base64_string)

    # Convert bytes to numpy array
    nparr = np.frombuffer(img_bytes, np.uint8)

    # Decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return img
