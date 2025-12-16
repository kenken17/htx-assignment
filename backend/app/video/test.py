import os

import cv2
from detection import ObjectDetector
from keyframes import extract_keyframes

# Paths for MobileNet SSD
PROTOTXT = "video/models/MobileNetSSD_deploy.prototxt"
MODEL = "video/models/MobileNetSSD_deploy.caffemodel"

# Load detector (lower confidence to catch more)
detector = ObjectDetector(PROTOTXT, MODEL, confidence_threshold=0.3)

# Video to test
VIDEO_PATH = "video/video_08.mp4"
SAVE_DIR = "video/debug_frames"
os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Cannot open video: {VIDEO_PATH}")

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print("Total frames:", frame_count)

# Pick every 300th frame for debugging
keyframes = list(range(0, frame_count, 300))

for i, frame_index in enumerate(keyframes):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    if not ret:
        print(f"Warning: Could not read frame {frame_index}")
        continue

    # Convert to BGR if necessary
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
    elif frame.shape[2] == 3:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    save_path = os.path.join(SAVE_DIR, f"debug_frame_{i}.jpg")
    cv2.imwrite(save_path, frame)
    print(f"Saved: {save_path}")

cap.release()


# Extract keyframes
keyframes = extract_keyframes(VIDEO_PATH)
print(f"Total keyframes extracted: {len(keyframes)}")

for i, kf in enumerate(keyframes[:5]):
    cap.set(cv2.CAP_PROP_POS_FRAMES, kf["frame_index"])
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(f"debug_frame_{i}.jpg", frame)

for kf in keyframes:
    frame_index = kf["frame_index"]
    timestamp = kf["timestamp"]

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    if not ret:
        continue

    # Ensure frame is BGR
    if frame.shape[2] == 4:  # RGBA -> BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
    elif frame.shape[2] == 3:  # RGB -> BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    detections = detector.detect(frame, timestamp)

    print(f"Frame {frame_index} @ {timestamp:.2f}s: {len(detections)} detections")
    for d in detections:
        print("  ", d)

        # Draw bounding box
        # For MobileNet-SSD, original code does not return box coords
        # If you have them, you can draw as:
        # x1, y1, x2, y2 = d["box"]
        # cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        # cv2.putText(frame, d["label"], (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    # Show frame
    cv2.imshow("Keyframe Detection", frame)
    if cv2.waitKey(500) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
