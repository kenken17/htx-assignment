from collections import defaultdict
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

# Load once (same model as audio)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_video_summary(detections: List[Dict]) -> str:
    """
    Create a human-readable summary of detected objects and timestamps.
    """
    if not detections:
        return "No objects detected in the video."

    objects = defaultdict(list)

    for det in detections:
        label = det["label"]
        timestamp = det["timestamp"]
        objects[label].append(timestamp)

    summary_lines = ["Detected objects in the video:"]
    for label, times in objects.items():
        times_str = ", ".join(f"{t:.1f}s" for t in times)
        summary_lines.append(f"- {label} at {times_str}")

    return "\n".join(summary_lines)


def generate_video_embedding(summary_text: str) -> bytes:
    """
    Generate text embedding for video summary.
    """
    embedding_vector = embedding_model.encode(summary_text)

    # Convert to float32 bytes for SQLite BLOB
    embedding_bytes = embedding_vector.astype(np.float32).tobytes()

    return embedding_bytes
