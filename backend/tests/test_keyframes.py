import cv2
import numpy as np


def _write_test_video(path, fps=10, size=(64, 64)):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(path), fourcc, fps, size)

    # 30 frames: 0-9 red, 10-19 green, 20-29 green (no further changes)
    for i in range(30):
        if i < 10:
            frame = np.full(
                (size[1], size[0], 3), (0, 0, 255), dtype=np.uint8
            )  # red (BGR)
        else:
            frame = np.full((size[1], size[0], 3), (0, 255, 0), dtype=np.uint8)  # green
        out.write(frame)
    out.release()


def test_extract_keyframes_detects_scene_change(tmp_path):
    from app.video.keyframes import extract_keyframes

    video_path = tmp_path / "scene_change.mp4"
    _write_test_video(video_path)

    keyframes = extract_keyframes(
        str(video_path), frame_interval=1, diff_threshold=0.02
    )

    # We expect at least one detected scene-change around the red->green transition.
    assert isinstance(keyframes, list)
    assert len(keyframes) >= 1

    # Find a keyframe near frame 10 (transition point)
    frame_idxs = [k["frame_index"] for k in keyframes]
    assert any(8 <= idx <= 12 for idx in frame_idxs), (
        f"Expected keyframe near 10, got {frame_idxs}"
    )

    # Timestamps should be non-negative floats rounded to 2dp
    for k in keyframes:
        assert k["timestamp"] >= 0
        assert isinstance(k["scene_change_score"], float)
