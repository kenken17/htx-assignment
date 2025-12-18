# Multimedia Processing & Analysis

This repository contains a full-stack multimedia processing application with:

- **[Backend](backend/README.md)** : FastAPI (video & audio processing, vector search, job queue)
- **[Frontend](frontend/README.md)** : Vue 3 single-page application
- **Containerisation**: Docker & Docker Compose (CPU-friendly)
- **[Architecture](architecture.pdf)** : Architecture overview diagram
- **[Limitations & Future Improvement](limitations%20and%20future%20improvements.pdf)** : Known limitations and potential future enhancements

---

## Prerequisites

- Docker
- Docker Compose
- (Optional for local dev) Node.js 18+ and Python 3.12+

---

## ⚠️ Important: VPN / Network Considerations (Very Important)

During Docker image builds, the backend image needs to download Python packages from **PyPI**
and machine learning models from **Hugging Face**.

If you are using:

- a **corporate VPN**
- Cloudflare WARP
- or any aggressive firewall / proxy

you may see errors like:

```
ReadTimeoutError: HTTPSConnectionPool(host='pypi.org', port=443): Read timed out
```

### ✅ Recommended Action

**Temporarily turn off your VPN while building Docker images.**

This is the most reliable way to avoid build failures.

You can re-enable the VPN **after** the images are built.

---

## MobileNet-SSD Model Files (Required for Video Processing)

For object detection, this project uses **MobileNet-SSD (Caffe)** via OpenCV DNN.

### Download Required Files

Download the following two files and place them in:

```
backend/app/video/models/
```

Files:

- `MobileNetSSD_deploy.prototxt`
- `MobileNetSSD_deploy.caffemodel`

Source repository:

```
https://github.com/PINTO0309/MobileNet-SSD-RealSense/tree/master/caffemodel/MobileNetSSD
```

> If these files are missing, **video jobs will fail gracefully** with a clear error message.
> Audio processing will still work.

---

## Run with Docker Compose

From the repository root:

```bash
docker compose up --build
```

### Access the Application

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

---

## Persistence

The Docker setup persists:

- Uploaded media files (`backend/uploads/`)
- SQLite database file
- Hugging Face and PyTorch model caches (faster subsequent runs)

---

## Development Notes

- The backend is CPU-optimised and does **not** require a GPU.
- Vector search is implemented using cosine similarity on stored embeddings.
- "Use as reference" performs true **query-by-example** vector search.

---

## Troubleshooting

### Docker build fails with pip timeout

- Turn off VPN
- Rebuild with:

```bash
docker compose build --no-cache
```

### Video jobs fail immediately

- Ensure MobileNet-SSD model files are present in:
  `backend/app/video/models/`
