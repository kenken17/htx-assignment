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

...

## Future Improvements

...
