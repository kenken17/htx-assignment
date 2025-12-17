# Backend

This backend service provides RESTful APIs for processing **video** and **audio** files. It supports key frame extraction, object detection, speech transcription, text embeddings, and unified search over processed media.

The implementation is intentionally **CPU-only and lightweight**, suitable for local execution or containerized environments.

---

## API Documentation

This service uses FastAPI, which automatically generates
interactive API documentation.

After starting the server, access:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

The Swagger UI can be used to explore and test all available
endpoints, including file upload endpoints.

---

## Tech Stack

- **Python 3.12.7**
- **FastAPI** – REST API framework
- **OpenCV** – Video processing, key frame extraction, object detection (DNN)
- **Whisper (whisper-tiny)** – Speech-to-text transcription
- **sentence-transformers (all-MiniLM-L6-v2)** – Text embeddings
- **SQLite** – Persistent storage

---

## API Endpoints

### Health Check

```
GET /health
```

Returns service status.

---

### Video Processing

```
POST /process/video
```

Accepts a video file upload and performs:

- Key frame extraction (scene-change–style frame sampling using OpenCV)
- Object detection using a lightweight, CPU-friendly model (MobileNet-SSD–style via OpenCV DNN)
- Text embedding generation for detected objects
- Storage of detected objects, timestamps, and metadata in SQLite

---

### Audio Processing

```
POST /process/audio
```

Accepts an audio file upload and performs:

- Audio preprocessing (format conversion and normalization)
- Speech recognition using **openai/whisper-tiny**
- Timestamped transcription with confidence scores
- Text embedding generation using the same model as video processing
- Storage of transcription data in SQLite

---

### Data Retrieval

```
GET /videos
GET /transcriptions
```

Returns processed video metadata and audio transcriptions respectively.

---

### Search

This service supports **two search modes** via the same endpoint:

#### 1) Text query search

```http
GET /search?q=<query>&top_k=<k>
```

Encodes the query text into an embedding and performs unified full-text + vector similarity search across:

- Video file names
- Detected objects
- Video summaries
- Audio transcriptions

#### 2) Reference (query-by-example) search

```http
GET /search?ref_type=<video|transcription>&ref_id=<id>&top_k=<k>
```

Uses an **existing** processed record as the query vector by loading its stored embedding from SQLite.
This powers the frontend **“Use as reference”** feature for:

- Visual similarity
- Audio similarity

Notes:

- `ref_id` is the primary key of the selected table (`videos` or `transcriptions`). IDs may overlap across tables, so the pair `(ref_type, ref_id)` uniquely identifies the reference.
- If neither `q` nor `ref_type/ref_id` are provided (or `q` is empty), the endpoint returns an empty result set.

Vector similarity is implemented using **cosine similarity computed in Python** over embeddings loaded from SQLite.

---

## Design Notes

Audio and video pipelines follow the same conceptual structure (media ingestion → content extraction → summarization → embedding → search).

### Key Frame Extraction (Video Processing)

Key frames are extracted using scene change detection based on grayscale histogram
differences between sampled frames. Frames with histogram differences exceeding a
threshold are considered scene changes and selected as key frames.

### Object Detection (Video Processing)

Object detection is performed using a pretrained `MobileNet-SSD` model via
OpenCV's DNN module. Detection is run only on extracted key frames to keep
processing lightweight and CPU-friendly.

Key frame extraction and object detection are implemented as independent components and composed via a lightweight pipeline module. This allows individual stages to be tested and tuned independently while keeping the API layer thin.

#### Object Detection Model (MobileNet-SSD)

For CPU-friendly video object detection, this project uses a pretrained `MobileNet-SSD` model via OpenCV’s DNN module.

---

## Model Files (Required)

Object detection uses a lightweight **MobileNet-SSD** model via OpenCV DNN. For licensing/size reasons, the model files are **not** bundled in this repository.

The original MobileNet-SSD links are no longer available. Instead, this project uses the following maintained archive:

- Repository: PINTO0309 / MobileNet-SSD-RealSense
- Path: `caffemodel/MobileNetSSD`

Source:
https://github.com/PINTO0309/MobileNet-SSD-RealSense/tree/master/caffemodel/MobileNetSSD

### Download model files

```bash
# From the repository root
mkdir -p backend/models

curl -L -o backend/models/MobileNetSSD_deploy.prototxt \
  https://raw.githubusercontent.com/PINTO0309/MobileNet-SSD-RealSense/master/caffemodel/MobileNetSSD/MobileNetSSD_deploy.prototxt

curl -L -o backend/models/MobileNetSSD_deploy.caffemodel \
  https://raw.githubusercontent.com/PINTO0309/MobileNet-SSD-RealSense/master/caffemodel/MobileNetSSD/MobileNetSSD_deploy.caffemodel
```

These files are referenced by the video processing pipeline for OpenCV DNN inference.

---

## Running Locally (Without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Service will be available at `http://localhost:8000`.

---

## Running with Docker

The service can be run using Docker with a CPU-only configuration.

### Option A (Simple): Build image with model files included

1. Download the model files (see **Model Files** section above)

2. Build and run:

```bash
cd backend
docker build -t backend .
docker run -p 8000:8000 backend
```

### Option B (Keep model files on host): Mount as a volume

1. Download the model files (see **Model Files** section above)

2. Run with a bind mount:

```bash
cd backend
docker build -t backend .
docker run -p 8000:8000 -v $(pwd)/models:/app/video/models backend
```

---

## Database

- SQLite is used as the primary datastore
- Stores:
  - Video file names, detected objects, frame timestamps, creation timestamps
  - Audio file names, transcribed text, timestamps, confidence scores, creation timestamps

---

## Upload Storage

Uploaded media files are stored on the local filesystem under `uploads/`.

- For simplicity (and because results are persisted to SQLite), uploads are **not** guaranteed to persist across container restarts.
- If you want persistence when running in Docker, mount a host volume:

```bash
cd backend
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads backend
```

---

## Notes

This project is designed to demonstrate:

- Clean API design
- Practical ML integration
- Thoughtful trade-offs appropriate for a take-home assignment

The focus is on correctness, clarity, and maintainability rather than production-scale optimization.
