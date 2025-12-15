# NexusLEO Local Dev

Alembic lives under `backend/` and the canonical dev workflow is:

```bash
docker compose up --build -d
docker compose exec backend alembic -c alembic.ini upgrade head
docker compose exec backend pytest -q nexusleo/backend/tests
```

FastAPI will be available on http://localhost:8000 once the `backend` service is healthy.
