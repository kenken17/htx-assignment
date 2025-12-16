from typing import Dict, List

import cv2

# MobileNet SSD class labels
CLASSES = [
    "background",
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
]


class ObjectDetector:
    def __init__(
        self, prototxt_path: str, model_path: str, confidence_threshold: float = 0.5
    ):
        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
        self.confidence_threshold = confidence_threshold

    def detect(self, frame, timestamp: float) -> List[Dict]:
        """
        Run object detection on a single frame.

        Returns:
            List of detected objects with label, confidence, timestamp
        """
        (h, w) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            scalefactor=0.007843,
            size=(300, 300),
            mean=127.5,
        )

        self.net.setInput(blob)
        detections = self.net.forward()

        results = []

        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])

            if confidence < self.confidence_threshold:
                continue

            class_id = int(detections[0, 0, i, 1])
            label = CLASSES[class_id]

            results.append(
                {
                    "label": label,
                    "confidence": round(confidence, 3),
                    "timestamp": round(timestamp, 2),
                }
            )

        return results
