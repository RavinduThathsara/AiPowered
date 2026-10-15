# SignBridge Backend

FastAPI backend for the SignBridge application.

## Development setup

From this directory, create and activate a virtual environment, then install the
development dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Start the API with:

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive documentation is
available at `/docs`, and the initial health check is:

```text
GET /api/v1/health
```

The first translation contract is:

```text
POST /api/v1/voice-to-sign
Content-Type: application/json
```

Example request:

```json
{
  "text": "Hello, how are you?",
  "sign_language": "ASL"
}
```

This currently returns deterministic mock output and does not claim to perform
speech recognition or sign-language translation.

Run the backend tests with:

```powershell
pytest
```

The next backend slice can replace the mock service with a real provider
without changing the API contract.

## Configuration

Settings use the `SIGNBRIDGE_` environment variable prefix. For example,
`SIGNBRIDGE_ALLOWED_ORIGINS` can provide a JSON list of frontend origins when
the API is deployed outside local development.
