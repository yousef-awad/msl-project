"""
Test script for Sign Language Recognition API
"""
import requests
import base64
import cv2
import numpy as np
import time
from pathlib import Path


API_URL = "http://localhost:7860"
SESSION_ID = "test_session_1"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_gestures():
    """Test gestures endpoint"""
    print("\n=== Testing Gestures Endpoint ===")
    response = requests.get(f"{API_URL}/gestures")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Gestures: {data['gestures']}")
    print(f"Count: {data['count']}")
    return response.status_code == 200


def test_predict_with_webcam():
    """Test prediction with webcam"""
    print("\n=== Testing Prediction with Webcam ===")
    print("Opening webcam... (Press 'q' to quit)")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return False

    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Encode frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_b64 = base64.b64encode(buffer).decode('utf-8')

            # Send to API
            try:
                response = requests.post(
                    f"{API_URL}/predict",
                    json={
                        "frame": frame_b64,
                        "session_id": SESSION_ID
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    frame_count += 1

                    # Display results on frame
                    text = f"{data['message']} ({data['confidence']:.2f})"
                    cv2.putText(
                        frame, text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )

                    cv2.putText(
                        frame, f"Frames: {data['sequence_length']}/30", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                    )

                    # Print to console
                    if frame_count % 10 == 0:
                        print(f"Frame {frame_count}: {data['gesture']} "
                              f"({data['confidence']:.2f}) - {data['message']}")

                else:
                    print(f"Error: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")

            # Display frame
            cv2.imshow('Sign Language Recognition Test', frame)

            # Break on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nTotal frames processed: {frame_count}")

    return True


def test_predict_with_image():
    """Test prediction with a static image"""
    print("\n=== Testing Prediction with Static Image ===")

    # Create a test image (you can replace this with an actual image path)
    print("Creating test image...")
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(
        test_img, "Test Frame", (200, 240),
        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3
    )

    # Encode to base64
    _, buffer = cv2.imencode('.jpg', test_img)
    frame_b64 = base64.b64encode(buffer).decode('utf-8')

    # Send multiple frames to build up sequence
    print("Sending 30 frames...")
    for i in range(30):
        response = requests.post(
            f"{API_URL}/predict",
            json={
                "frame": frame_b64,
                "session_id": "test_image_session"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Frame {i+1}/30: {data['message']}")
        else:
            print(f"Error on frame {i+1}: {response.status_code}")
            return False

    # Final prediction
    print(f"\nFinal prediction: {data['gesture']} "
          f"(confidence: {data['confidence']:.2f})")
    return True


def test_reset():
    """Test session reset"""
    print("\n=== Testing Session Reset ===")
    response = requests.post(f"{API_URL}/reset?session_id={SESSION_ID}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def main():
    """Run all tests"""
    print("=" * 60)
    print("Sign Language Recognition API - Test Suite")
    print("=" * 60)

    # Wait for API to be ready
    print("\nWaiting for API to be ready...")
    for i in range(5):
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                print("API is ready!")
                break
        except requests.exceptions.RequestException:
            print(f"Attempt {i+1}/5 failed, retrying...")
            time.sleep(2)
    else:
        print("Error: API is not responding. Make sure it's running:")
        print("  python app.py")
        return

    # Run tests
    results = {}
    results['health'] = test_health()
    results['gestures'] = test_gestures()
    results['reset'] = test_reset()

    # Choose test mode
    print("\n" + "=" * 60)
    print("Choose test mode:")
    print("1. Test with webcam (live)")
    print("2. Test with static image")
    print("3. Skip prediction test")
    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        results['predict'] = test_predict_with_webcam()
    elif choice == "2":
        results['predict'] = test_predict_with_image()
    else:
        print("Skipping prediction test")
        results['predict'] = None

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, result in results.items():
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "PASSED"
        else:
            status = "FAILED"
        print(f"{test_name.capitalize()}: {status}")

    print("\nAll tests completed!")


if __name__ == "__main__":
    main()
