from typing import Dict, List

import cv2
from video.detection import ObjectDetector
from video.keyframes import extract_keyframes


def process_video_frames(video_path: str, detector: ObjectDetector) -> Dict:
    """
    Run key frame extraction + object detection.

    Returns:
        {
          "keyframes": [...],
          "objects": [...]
        }
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    keyframes = extract_keyframes(video_path)
    all_detections: List[dict] = []

    for kf in keyframes:
        frame_index = kf["frame_index"]
        timestamp = kf["timestamp"]

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            continue

        detections = detector.detect(frame, timestamp)
        all_detections.extend(detections)

    cap.release()

    return {"keyframes": keyframes, "objects": all_detections}
