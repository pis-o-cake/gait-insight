#!/bin/sh
# 프로젝트 native 검증 진입점. engsys verify 가 이 스크립트를 부른 뒤
# 문서 구조 검사와 편집 검토 검사를 이어서 실행한다.
#
# backend 테스트는 Postgres 가 필요하다. compose 의 db 컨테이너를 쓰며,
# 없으면 건너뛰지 않고 실패한다(설계 0001 검증 절).
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

if [ -f frontend/package.json ]; then
  echo "verify: frontend"
  (cd frontend && npm run -s typecheck && npm test --silent -- --run)
fi

if [ -f backend/pyproject.toml ]; then
  echo "verify: backend"
  if ! docker compose ps --status running --services 2>/dev/null | grep -qx db; then
    echo "verify: db container is not running. start it with: docker compose up -d db" >&2
    exit 1
  fi
  [ -f .env ] || { echo "verify: .env is missing. copy .env.example and fill AUTH_SECRET" >&2; exit 1; }
  # shellcheck disable=SC1091
  set -a; . ./.env; set +a
  docker compose exec -T db psql -U "${POSTGRES_USER:-gait}" -d postgres -tc \
    "SELECT 1 FROM pg_database WHERE datname='gait_insight_test'" | grep -q 1 \
    || docker compose exec -T db psql -U "${POSTGRES_USER:-gait}" -d postgres -c \
       "CREATE DATABASE gait_insight_test OWNER ${POSTGRES_USER:-gait}" >/dev/null
  # 테스트 코드는 배포 이미지에 넣지 않는다. 검증할 때만 마운트한다.
  docker compose run --rm --no-deps \
    -e DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER:-gait}:${POSTGRES_PASSWORD}@db:5432/gait_insight_test" \
    -e AUTH_SECRET="$AUTH_SECRET" \
    -v "$root/backend/tests:/app/tests:ro" \
    -v "$root/backend/pyproject.toml:/app/pyproject.toml:ro" \
    app sh -c "uv pip install --system --quiet --no-cache pytest pytest-asyncio httpx && pytest -q"
fi

echo "verify: native checks done"
