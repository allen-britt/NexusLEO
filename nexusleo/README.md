# NexusLEO Local Dev

Alembic lives under `backend/` and the canonical dev workflow is:

```bash
docker compose -f nexusleo/docker-compose.yml down -v
docker compose -f nexusleo/docker-compose.yml up --build -d
docker compose -f nexusleo/docker-compose.yml exec backend pytest -q
```

Note: inside the `backend` container, the Alembic config path is `alembic.ini` (NOT `backend/alembic.ini`).

FastAPI will be available on http://localhost:8000 once the `backend` service is healthy.
