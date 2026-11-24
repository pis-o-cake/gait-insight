# 1단계: React 화면 빌드. frontend 가 아직 없으면 빈 산출물을 만든다.
FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/ ./
RUN if [ -f package.json ]; then npm ci && npm run build; else mkdir -p dist; fi

# 2단계: API. uv 로 의존성을 설치하고 위 빌드 결과를 함께 담는다.
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app

COPY backend/pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml

COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./
COPY backend/tools ./tools
COPY backend/entrypoint.sh ./
COPY --from=web /web/dist ./static
RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
