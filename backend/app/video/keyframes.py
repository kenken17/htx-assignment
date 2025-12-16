from typing import Dict, List

import cv2


def extract_keyframes(
    video_path: str, frame_interval: int = 10, diff_threshold: float = 0.05
) -> List[Dict]:
    """
    Extract keyframes using scene change detection based on histogram difference.

    Args:
        video_path: Path to video file
        frame_interval: Process every Nth frame
        diff_threshold: Threshold for scene change detection

    Returns:
        List of keyframes with timestamp and frame index
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    prev_hist = None
    keyframes = []
    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process every N frames
        if frame_index % frame_interval != 0:
            frame_index += 1
            continue

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compute normalized histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        if prev_hist is not None:
            # Compare histograms
            diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)

            if diff > diff_threshold:
                timestamp = frame_index / fps if fps > 0 else 0
                keyframes.append(
                    {
                        "frame_index": frame_index,
                        "timestamp": round(timestamp, 2),
                        "scene_change_score": round(float(diff), 3),
                    }
                )

        prev_hist = hist
        frame_index += 1

    cap.release()
    return keyframes
