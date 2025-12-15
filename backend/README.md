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

### Vector Search Implementation

This project implements vector similarity search using **Option 3** from the assignment specification.

Text embeddings are generated using the `all-MiniLM-L6-v2` model and stored directly in SQLite as serialized vectors. At query time, embeddings are loaded into memory and cosine similarity is computed in Python to rank results.

The `scikit-learn` library is used solely for cosine similarity computation, not as a vector indexing or nearest-neighbor engine.

## Future Improvements

...
