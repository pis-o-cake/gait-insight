#!/bin/sh
# 컨테이너 기동 순서: 마이그레이션 -> seed -> 서버.
set -eu

echo "[entrypoint] alembic upgrade head"
alembic upgrade head

echo "[entrypoint] seeding reference data"
python tools/seed.py

echo "[entrypoint] local network demo only - do not expose to the internet"
exec gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers "${WORKERS:-2}" \
  --bind "0.0.0.0:${PORT:-8000}" \
  --access-logfile - \
  --timeout 120
