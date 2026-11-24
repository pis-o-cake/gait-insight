---
type: runbook
status: active
last-reviewed: 2026-09-21
---

# 로컬망 시연 기동 절차

시연용 PC 한 대에서 `docker compose up --build` 한 번으로 DB와 서버를 띄우고, 같은 와이파이에 있는 휴대폰·노트북이 `http://<호스트IP>:8000`으로 접속한다. 구성의 근거는 [설계 0002](../design/0002-infrastructure-and-runtime.md)에 있다.

## 적용 상황

발표장·강의실에서 보행 분석 화면을 시연할 때 쓴다. 인터넷 공개 배포나 외부 접속은 이 절차의 대상이 아니다.

전제 조건:

- 시연 PC에 Docker Desktop이 설치돼 있고 실행 중이다.
- 시연 PC와 관람용 단말이 같은 공유기에 붙어 있다. 학교 와이파이가 단말 간 통신을 막는 경우가 있으므로 휴대용 핫스팟을 준비해 두면 안전하다.
- 저장소를 내려받았고 `.env` 파일이 있다.

## 실행 전 확인

1. `.env`가 없으면 만든다. `AUTH_SECRET`이 비어 있으면 서버가 뜨지 않는다.

   ```sh
   cp .env.example .env
   python3 -c "import secrets; print(secrets.token_urlsafe(48))"   # 출력값을 AUTH_SECRET 에 붙여넣는다
   ```

2. 호스트의 8000 포트가 비어 있는지 본다. 5432를 이미 쓰고 있어도 상관없다. compose는 호스트 쪽을 5433으로 연다.

   ```sh
   lsof -nP -iTCP:8000 -sTCP:LISTEN
   ```

3. 예시 기록 parquet이 있는지 본다. 없으면 만든다.

   ```sh
   ls backend/data/records/
   docker compose run --rm --no-deps app python tools/make_records.py
   ```

## 절차

```sh
docker compose up --build -d
docker compose ps              # db 는 healthy, app 은 Up 이어야 한다
docker compose logs -f app     # 마이그레이션 → seed → Gunicorn 순서로 찍힌다
```

시연 PC의 주소를 확인해 관람용 단말에 알려준다.

```sh
ipconfig getifaddr en0         # macOS 와이파이
ipconfig                       # Windows, IPv4 주소
```

처음 한 번은 계정을 만든다. 화면의 "계정 만들기"에서 아이디와 비밀번호를 넣으면 바로 로그인된다. 비밀번호 규칙은 없다.

## 성공 확인

| 확인할 것 | 기대 결과 |
| --- | --- |
| `curl -s localhost:8000/api/health` | `{"status":"ok"}` |
| 브라우저에서 `http://localhost:8000` | 로그인 화면이 뜬다 |
| 로그인 후 | 기록 3개가 보이고 각 행에 스파크라인이 그려진다 |
| 기록 하나를 열고 재생 | 히트맵 색이 걸음에 따라 바뀌고 그래프 커서가 같이 움직인다 |
| 휴대폰에서 `http://<호스트IP>:8000` | 같은 화면이 한 열로 쌓여 보이고 가로 스크롤이 생기지 않는다 |

## 실패와 복구

| 증상 | 원인과 조치 |
| --- | --- |
| `AUTH_SECRET is required` 로 app 이 죽는다 | `.env`의 `AUTH_SECRET`이 비었다. 값을 채우고 `docker compose up -d app` |
| `ports are not available` | 호스트에서 8000 또는 5433을 이미 쓰고 있다. 쓰는 쪽을 끄거나 `docker-compose.yml`의 호스트 포트를 바꾼다 |
| 휴대폰에서 접속되지 않는다 | 먼저 시연 PC 브라우저로 같은 주소를 연다. 그것이 되면 방화벽 문제다. macOS는 시스템 설정의 방화벽에서 Docker 수신 허용, Windows는 Defender 방화벽에서 8000 인바운드를 허용한다. 그래도 안 되면 공유기가 단말 간 통신을 막는 것이므로 핫스팟으로 바꾼다 |
| 기록 목록이 비어 있다 | seed 가 parquet 을 찾지 못했다. `docker compose logs app | grep "record file not found"` 로 확인하고 위의 `make_records.py` 를 돌린 뒤 `docker compose restart app` |
| 판정 기준을 바꿨는데 화면 값이 그대로다 | 분석 결과가 규칙 세트 단위로 캐시된다. `backend/data/seed/rule_set.json`의 `version`을 새 값으로 올리고 다시 seed 한다 |
| 처음부터 다시 하고 싶다 | `docker compose down -v` 로 DB 볼륨까지 지우고 다시 `up --build`. 만들어 둔 계정도 함께 사라진다 |

시연이 끝나면 `docker compose down`으로 내린다. 볼륨을 남겨 두면 다음 시연에서 계정과 기록이 그대로 있다.
