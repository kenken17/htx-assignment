import cv2
import numpy as np


def test_object_detector_filters_by_threshold_and_maps_label(monkeypatch):
    # Prepare a dummy net that returns 2 detections: one above, one below threshold.
    class DummyNet:
        def setInput(self, blob):
            self._blob = blob

        def forward(self):
            # detections shape: (1, 1, N, 7)
            # [image_id, class_id, confidence, x1, y1, x2, y2]
            det = np.zeros((1, 1, 2, 7), dtype=np.float32)
            det[0, 0, 0, 1] = 15  # class_id -> "person" in MobileNet SSD label list
            det[0, 0, 0, 2] = 0.72
            det[0, 0, 1, 1] = 7  # class_id -> "car"
            det[0, 0, 1, 2] = 0.20  # below threshold
            return det

    monkeypatch.setattr(cv2.dnn, "readNetFromCaffe", lambda *args, **kwargs: DummyNet())

    from app.video.detection import ObjectDetector

    detector = ObjectDetector(
        "dummy.prototxt", "dummy.caffemodel", confidence_threshold=0.5
    )
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    results = detector.detect(frame, timestamp=1.234)

    assert results == [{"label": "person", "confidence": 0.72, "timestamp": 1.23}]
