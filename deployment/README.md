# Deployment Notes

## Current Status

`deployment/docker-compose.yml` is kept under `deployment/`, so every relative
path in the file is resolved from that directory. The previous path issue has
been fixed by pointing services back to the repository root where needed.

Current service paths:

- `backend.build`: `../backend`
- `backend.env_file`: `../backend/.env`
- `frontend.build.context`: `../frontend`
- `nginx.build`: `./nginx`

The configuration has been validated with:

```bash
docker compose -f deployment/docker-compose.yml config --quiet
```

This proves the Compose file can be parsed and that build/env paths resolve.
It does not prove the full stack is healthy yet.

## How To Run

Prepare backend environment variables first:

```bash
copy backend\.env.example backend\.env
```

Then validate from the repository root:

```bash
docker compose -f deployment\docker-compose.yml config --quiet
```

Start the stack after validation:

```bash
docker compose -f deployment\docker-compose.yml up -d --build
```

Check services:

```bash
docker compose -f deployment\docker-compose.yml ps
curl http://localhost:8000/health
curl http://localhost:3000/chat
```

## Container Environment Notes

- `backend.env_file` still reads `backend/.env` for secrets such as LLM keys.
- Container-only connection values are overridden in Compose:
  - `DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/mall_agent`
  - `DATABASE_URL_SYNC=postgresql+psycopg2://postgres:postgres@postgres:5432/mall_agent`
  - `REDIS_URL=redis://redis:6379/0`
  - `QDRANT_URL=http://qdrant:6333`
- The frontend build receives `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`.

## Remaining Release Checks

Do not mark full one-command startup as passing until:

- `docker compose -f deployment\docker-compose.yml up -d --build` succeeds.
- `docker compose -f deployment\docker-compose.yml ps` shows core services running.
- `/health` returns 200 after startup.
- `http://localhost:3000/chat` is reachable.
- nginx proxy behavior is verified if port 80 is used.
