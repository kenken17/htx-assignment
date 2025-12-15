# Backend Setup

Create a virtual environment and install dependencies:

```sh
pip install -r requirements.txt
uvicorn main:app --reload
```

## Running the Service

...

## API Documentation

This service uses FastAPI, which automatically generates
interactive API documentation.

After starting the server, access:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

The Swagger UI can be used to explore and test all available
endpoints, including file upload endpoints.

## Design Notes

Audio and video pipelines follow the same conceptual structure (media ingestion → content extraction → summarization → embedding → search).

Due to differences in processing complexity, video logic is modularized further, while audio processing is kept within the API layer for simplicity.

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

**Model Files**

The pipeline requires two files:

- `MobileNetSSD_deploy.prototxt`
  Defines the network architecture (layers, filters, strides, etc.)

- `MobileNetSSD_deploy.caffemodel`
  Contains the learned weights of the network
  Provides knowledge for object detection (person, car, dog, etc.)
  Both files must be present in backend/video/models/ for detection to work.

**Download Links**

A mirror with the specific files are available in the [PINTO0309/MobileNet-SSD-RealSense](https://github.com/PINTO0309/MobileNet-SSD-RealSense/tree/master/caffemodel/MobileNetSSD) archived repository

### Vector Search Implementation

This project implements vector similarity search using **Option 3** from the assignment specification.

Text embeddings are generated using the `all-MiniLM-L6-v2` model and stored directly in SQLite as serialized vectors. At query time, embeddings are loaded into memory and cosine similarity is computed in Python to rank results.

The `scikit-learn` library is used solely for cosine similarity computation, not as a vector indexing or nearest-neighbor engine.

## Future Improvements

...
