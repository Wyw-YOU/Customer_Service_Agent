# Deployment Notes

## Current Status

`deployment/docker-compose.yml` is a target deployment draft. It is not yet a
verified one-command startup file.

Known blockers:

- `frontend/` does not exist yet, but the compose file still defines a
  `frontend` service.
- `nginx` depends on `frontend`, so full reverse-proxy startup is blocked too.
- Docker Compose resolves relative paths from the compose file directory. With
  `-f deployment/docker-compose.yml`, paths such as `./backend/.env` resolve to
  `deployment/backend/.env`, not `backend/.env` at the repository root.

## Why The Current Path Fails

From the repository root, this command:

```bash
docker compose -f deployment/docker-compose.yml config
```

loads `deployment/docker-compose.yml`. Relative paths inside that file are then
resolved relative to `deployment/`.

Current examples:

```yaml
backend:
  build: ./backend
  env_file:
    - ./backend/.env
frontend:
  build: ./frontend
nginx:
  build: ./deployment/nginx
```

These resolve as:

```text
deployment/backend
deployment/backend/.env
deployment/frontend
deployment/deployment/nginx
```

Those paths do not match the current repository layout.

## Recommended Fix Options

Choose one direction before using Compose as a release path.

### Option A: Move Compose To Repository Root

Create a root-level `docker-compose.yml` and keep paths simple:

```yaml
backend:
  build: ./backend
  env_file:
    - ./backend/.env
nginx:
  build: ./deployment/nginx
```

Only add `frontend` after `frontend/` exists.

### Option B: Keep Compose Under `deployment/`

Use paths relative to `deployment/`:

```yaml
backend:
  build: ../backend
  env_file:
    - ../backend/.env
nginx:
  build: ./nginx
```

Only add `frontend` after `../frontend` exists.

## Current Backend-Only Recommendation

Until `frontend/` is implemented, validate the backend with local services or a
temporary backend-only compose file containing:

- `backend`
- `postgres`
- `redis`
- `qdrant`

Do not mark full Docker Compose startup as passing until:

- `docker compose config` returns 0.
- No `env file not found` error appears.
- No missing `frontend` build path appears.
- `/health` returns 200 after startup.
