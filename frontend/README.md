# NexusLEO Demo UI

## Run

1. Start backend:

```powershell
docker compose -f nexusleo/docker-compose.yml up --build -d
```

2. Start UI:

```powershell
cd frontend
npm install
npm run dev
```

Open:

- http://localhost:5173

## Notes

- This UI uses a generated typed OpenAPI client (no hand-written fetch calls).
- Client is generated from `../openapi/nexusleo.openapi.json` via `openapi-typescript-codegen` on `postinstall`.
- API calls use relative URLs and are proxied by Vite to `http://localhost:8000`.
