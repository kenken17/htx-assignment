# Frontend (Vue 3 + Vite)

Single-page application to interact with the backend multimedia-processing APIs.

## Features

- Upload video/audio
- Media type selection (Video/Audio)
- Live job progress (polling)
- Results viewer (JSON + specialized views when fields exist)
- Lists processed videos and transcriptions from the database
- Unified search:
  - Text search via `/search?q=...`
  - “Use as reference” actions for visual/audio similarity (uses the selected item's summary/transcript text as the query)

## Configure

Set the backend URL:

```
VITE_API_BASE=http://localhost:8000
```

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:5173`.

## Containerization

Build and run the frontend:

```bash
docker build -t media-frontend .
docker run -p 5173:80 media-frontend
```

If your backend runs on a different host/port, set `VITE_API_BASE` at build time by editing a `.env` before building.
