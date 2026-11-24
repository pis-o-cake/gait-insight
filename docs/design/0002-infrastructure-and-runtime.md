---
type: design-proposal
status: review
date: 2026-09-21
---

# 0002. 인프라와 실행

서버와 DB를 Docker Compose 한 스택으로 띄우고 호스트 PC의 8000 포트 하나만 같은 로컬망에 공개한다. `app` 이미지는 멀티스테이지로 React를 빌드해 python:3.12-slim + uv 위의 FastAPI에 넣고, entrypoint가 마이그레이션·seed 뒤 Gunicorn을 실행한다. 전체 구조는 [0001](0001-system-architecture.md), DB 스키마·seed 내용은 [0003](0003-data-model-and-storage.md)에 있다.

## 제안 요약

- 컨테이너 둘: `db`(postgres:16, named volume), `app`(아래 Dockerfile). Nginx·TLS·인증 없음.
- 시연은 `docker compose up --build` 한 명령. 개발은 `db`만 compose로 띄우고 앱·화면은 호스트에서 핫리로드.
- 호스트 공개 포트는 8000 하나. 5432는 compose 내부망에만 있다.
- 비밀값·접속 정보는 `.env`(pydantic-settings)로만 주입한다. 이미지에 넣지 않는다.

## 설계

### 파일

```text
docker-compose.yml     services: db, app / volumes: pgdata / app: ports 8000:8000, volumes ./backend/data:/app/data:ro, depends_on db (healthcheck)
                       db 는 호스트 127.0.0.1:5433 에도 연다(호스트의 5432 와 겹치지 않게). 시연만 할 때는 지워도 된다.
Dockerfile             stage 1 node:22-alpine  → frontend npm ci && npm run build
                       stage 2 python:3.12-slim → uv pip install -r pyproject.toml, COPY backend/app, COPY --from=1 frontend/dist → /app/static
.dockerignore          .git, .engsys, docs, node_modules, .venv, __pycache__, backend/data/raw, .env
.env.example           POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, AUTH_SECRET, AUTH_TOKEN_TTL_HOURS, WORKERS
backend/entrypoint.sh  alembic upgrade head → python tools/seed.py → gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w $WORKERS -b 0.0.0.0:$PORT
```

`app` 이미지 안의 FastAPI는 `/api`·`/docs`를 먼저 매칭하고 나머지 경로를 `/app/static`의 정적 파일(SPA fallback은 `index.html`)로 서빙한다.

### 네트워크와 접속

```text
휴대폰·PC 브라우저 ──http://<호스트IP>:8000──▶ 호스트 8000 ──▶ app:8000 ──compose 내부망──▶ db:5432
```

- 호스트 방화벽에서 8000 인바운드를 허용한다(macOS 방화벽, Windows Defender). 절차는 runbook.
- 호스트 IP는 시연 전에 `ipconfig getifaddr en0`(macOS) / `ipconfig`(Windows)로 확인해 화면 상단에 표시한다. 기동 로그에도 접속 주소와 "로컬망 시연 전용"을 출력한다.
- CORS는 개발 모드(Vite 5173 → 8000)에만 허용하고 시연 이미지에서는 끈다. 같은 출처라 필요 없다. 개발 모드의 CORS는 `allow_credentials=True`로 두어 로그인 쿠키가 프록시 없이도 오간다.
- 로그인 쿠키는 `HttpOnly; SameSite=Lax`이며 `Secure`는 붙이지 않는다. TLS가 없는 로컬망 http 접속이 전제이기 때문이다. 외부 공개·TLS 도입 시 `Secure`를 켠다.

### 실행 모드

| 모드 | 명령 | 용도 |
| --- | --- | --- |
| 시연 | `docker compose up --build` | db + app 컨테이너. entrypoint가 마이그레이션·seed 후 Gunicorn(Uvicorn worker 2개)을 띄운다. 휴대폰은 `http://<호스트IP>:8000` |
| 개발 | `docker compose up -d db` + `uv run uvicorn --reload` + `npm run dev` | 핫리로드. Vite가 `/api`를 8000으로 프록시 |

두 모드 모두 같은 `DATABASE_URL` 형식을 쓰고 호스트 이름만 다르다(`db` / `localhost`).


### 환경 변수

| 이름 | 시연(compose) | 개발(호스트) | 용도 |
| --- | --- | --- | --- |
| `DATABASE_URL` | `postgresql+asyncpg://…@db:5432/gait_insight` | `…@localhost:5433/gait_insight` | SQLAlchemy async engine |
| `DATA_DIR` | `/app/data` | `backend/data` | parquet·seed 위치 |
| `HOST` / `PORT` | `0.0.0.0` / `8000` | 동일 | 바인딩 |
| `WORKERS` | `2` | 해당 없음(uvicorn --reload) | Gunicorn worker 수 |
| `AUTH_SECRET` | `.env`에서 생성한 무작위 문자열 | 동일 | JWT 서명 키. 비면 기동 실패 |
| `AUTH_TOKEN_TTL_HOURS` | `12` | 동일 | 로그인 쿠키 만료 |
| `LLM_*` | 비움 | 비움 | Explainer 자리. 이번 단계 미사용 |

테스트는 `DATABASE_URL`의 DB 이름만 `gait_insight_test`로 바꿔 같은 `db` 컨테이너를 쓴다. `scripts/verify.sh`가 그 DB를 없으면 만들고, 테스트 코드는 배포 이미지에 넣지 않고 검증할 때만 마운트한다.

## 결정과 대안

### Docker Compose 단일 스택, 로컬망 전용

`docker compose up --build`로 `db`와 `app` 두 컨테이너를 띄운다. `app`은 python:3.12-slim 위에 uv로 설치한 FastAPI를 Gunicorn + Uvicorn worker로 실행하고, 같은 이미지 안에 멀티스테이지로 빌드한 React 정적 파일을 `/`에서 서빙한다. 호스트에는 8000 하나만 공개하고 5432는 compose 네트워크 안에만 둔다. 인증·TLS·Nginx·인터넷 공개는 두지 않고, README와 기동 로그에 "로컬망 시연 전용"을 명시한다.

배경: 사용자가 확인한 조건은 실 상용이 아니며 같은 로컬망의 PC·휴대폰이 접근하면 된다는 것이다. 사용자는 DB와 서버의 실행 방식이 갈리면 나중에 헷갈리므로 둘 다 Docker로 통일하길 원했다. 시연 데이터는 공개 라이선스(ODC-By)의 익명 기록이라 개인정보가 없다.

| 대안 | 거절 이유 |
| --- | --- |
| DB만 Docker, 앱은 호스트 `uv`로 실행 | 실행 방식이 둘로 갈려 시연 PC마다 Python·uv 설치가 필요하고 절차가 헷갈린다 |
| Nginx 리버스 프록시 추가 | TLS도 정적 캐시 요구도 없어 지금은 컨테이너 하나가 늘기만 한다. 외부 공개·TLS가 필요해지면 그때 추가한다 |
| 프론트·백엔드 분리 포트(5173 + 8000) | 휴대폰이 두 주소를 알아야 하고 CORS가 필요하다 |
| Vercel·Render 인터넷 배포 | 규칙·콘텐츠가 학과 검토 전이라 외부 공개가 부적절하고 시연 장소 인터넷 여부가 미확인 |

비용: 시연 PC에 Docker Desktop이 필요하고, 호스트 방화벽에서 8000 포트 인바운드를 열어야 한다(runbook). 이미지 빌드에 node 스테이지가 들어가 첫 빌드가 수 분 걸린다. 같은 망의 누구나 접속하며 공개 데이터이므로 수용한다.
