---
type: project-scope
status: draft
---

[English](README.md) | **한국어**

# gait-insight

□ **노인재활운동과 캡스톤디자인 프로토타입. 공개 보행 데이터를 분석해 관찰된 특징과 추천 운동을 웹·모바일 웹으로 표시함**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)](https://vite.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Platform](https://img.shields.io/badge/%ED%94%8C%EB%9E%AB%ED%8F%BC-%EC%9B%B9%20%7C%20%EB%AA%A8%EB%B0%94%EC%9D%BC%20%EC%9B%B9-555)](#목업-바로-보기)

- 핵심 흐름: **기록 선택 → 발바닥 하중 시각화 → 관찰된 특징 설명 → 추천 운동**
- 구성: 로컬 PC에서 Docker Compose로 서버·DB 기동, 같은 로컬망의 PC·휴대폰 브라우저로 접속하는 시연용. 상용 배포는 범위 밖
- 역할 분담: 수치는 프로그램이 계산, 추천 운동은 학과가 검토한 기준으로 연결
  - AI는 계산 결과·추천 운동을 쉬운 말로 설명하는 역할로 한정. AI 없이 준비된 문장으로도 동작
- 데이터: PhysioNet 파킨슨병 보행 연구 자료 중 **비교용 건강한 사람 73명 기록만** 사용
- 합의 경위·미확정 안건: [킥오프 브리프](docs/briefs/2026-09-18-kickoff.md)

## 목업 바로 보기

정적 HTML이라 브라우저에서 링크로 바로 열림. 로그인은 시연용 고정 계정 `admin` / `0000`.

| 대상 | 주소 |
| --- | --- |
| 휴대폰 | <https://pis-o-cake.github.io/gait-insight/mockup/gait-insight-mobile.html> |
| PC·태블릿 | <https://pis-o-cake.github.io/gait-insight/mockup/gait-insight-demo.html> |

※ 파일로 보내면 카톡·메일 첨부 미리보기, iOS 파일 앱처럼 JS를 실행하지 않는 뷰어에서 빈 화면이 나옴. 전달은 링크로 함

※ GitHub Pages가 `main` 브랜치의 `docs/` 폴더를 그대로 서빙함. `docs/mockup/*.html`을 push하면 1~2분 뒤 반영됨

## 전체 범위

포함 범위:

| 영역 | 내용 |
| --- | --- |
| 데이터 | PhysioNet gaitpdb v1.0.0의 건강한 대조군 기록만 선별·변환. 원본 출처·라이선스(ODC-By) 표기 |
| 화면 | 기록 선택, 보행 분석(히트맵 재생·개요/확대 그래프·지표 타일·요약), 운동정보(특징별 스텝 플로우). 목업의 플레이어 골격·기본 테마 |
| 로그인 | 아이디·비밀번호 가입·로그인, bcrypt 해시, 쿠키 세션. 로그인 사용자만 화면·API 사용 |
| 분석 | 전문가 자료 3종 기준 지표 M01~M10(인솔 8 + 보행검사 입력 2), 보행 유형 판정(T1 체중 부하 불균형·T2 보장 차이·T3 정상 유지). 계산 불가 사유 전달 |
| 운동정보 | 전문가 자료의 운동 18종(목적·방법·운동량·주의), 유형→운동 프로그램 연결, 권유 이유·재평가 항목. 검토 상태 표시 |
| 저장 | PostgreSQL(기록 메타·운동 콘텐츠·규칙 세트·분석 결과) + parquet(센서 시계열). Alembic 마이그레이션·seed 도구 |
| 실행 | `docker compose up --build`로 `db` + `app` 컨테이너 기동. 호스트 8000 포트 하나만 공개 |
| 접속 | 호스트 PC의 컨테이너에 같은 로컬망의 PC·휴대폰 브라우저가 접속 |
| 문서 | Engineering System 계약에 따른 아키텍처·설계·ADR·프로토타입 기록·runbook |

제외 범위:

- 하드웨어: 인솔 하드웨어, 센서 교정, 블루투스 실시간 연결
- 분석: 러닝·스쿼트·런지 분석, 질병 진단, 낙상 위험도, 교정 효과 검증, 운동 전후 개선 분석
- 계정: 비밀번호 규칙, 이메일 인증, 비밀번호 찾기, 권한 등급
- 기타: 네이티브 앱, 업로드·개인 기록 저장, 앱 서버의 인터넷 공개 배포, LLM 설명(인터페이스만 둠)

※ 정적 목업의 GitHub Pages 공개는 시연 전달용. 앱 서버 공개 배포와 별개임

## 기능별 완료 기준

| 기능 | 완료 기준 |
| --- | --- |
| 데이터 준비 | demographics 표 기준으로 대조군 선별 기준 문서화. 변환된 기록이 열 수·시간축·단위 검증 통과. 제외 기록·사유를 보고서에 남김 |
| 로그인 | 가입 후 로그인 시 기록 목록이 열림. 미로그인·쿠키 만료 시 모든 화면이 로그인으로 복귀. 비밀번호 규칙 없음 |
| 기록 선택 | 목록에 기록 표시명·조건·길이·출처 표시, 6초 스파크라인 미리보기 표시. 휴대폰 폭에서 행 잘림 없음 |
| 보행 분석 | 재생·일시정지·처음으로·시크·배속(0.5~30배) 동작. 히트맵·그래프·시크바가 같은 시각을 가리킴. 지표 10개를 측정 묶음별 좌·우 값과 상태 칩으로 표시, 계산 불가 시 사유 표시 |
| 운동정보 | 관찰된 특징마다 관찰 근거(수치)·권유 이유·운동 카드를 한 블록으로 표시. 카드에 검토 상태 태그. 관찰이 없으면 일반 운동만 표시 |
| 지표 계산 | 합성 신호 테스트에서 목업 값과 일치. 짧은 기록·접촉 없음 예외는 사유 코드로 반환 |
| 기동·DB 초기화 | Docker만 있는 빈 PC에서 `docker compose up --build` 한 번으로 마이그레이션·seed·서버 기동. 규칙 세트를 바꾸면 재기동 없이 새 버전으로 분석 결과 계산 |
| 로컬망 접속 | runbook대로 기동한 서버에 같은 망의 휴대폰이 `http://<IP>:8000`으로 접속해 3화면 완주 |
| 문서 | `engsys verify` 통과 |

※ 진행 상태는 아래 "상태" 절에 기록

## 프로젝트 구조

```
backend/    FastAPI 앱(도메인별 api · service · crud · schemas · models), Alembic, seed 데이터
frontend/   React + TypeScript (Vite)
docs/       아키텍처·설계 제안·runbook·목업 (GitHub Pages 서빙)
scripts/    verify.sh — 프로젝트 검증
```

## 문서

- 기준: [Engineering System](https://github.com/pis-o-cake/engineering-system) 계약(`.engsys/project.yaml`)에 따라 유형별 폴더에 배치
- 새 문서: `engsys docs new --type <type> <slug>`로 시작, `engsys verify`로 검사

| 유형 | 위치 | 답하는 질문 |
| --- | --- | --- |
| 현행 아키텍처 | [docs/architecture/README.md](docs/architecture/README.md) | 지금 어떤 구성요소가 어떤 책임으로 동작하는가 |
| 설계 제안 | [docs/design](docs/design) | 이 범위·방법으로 구현해도 되는가. 0001 아키텍처, 0002 인프라·실행, 0003 데이터 모델, 0004 API·분석, 0005 화면 |
| 결정 기록 | `docs/adr` | 설계 동결 후 중요한 변경을 왜 했는가. 아직 없음 |
| 프로토타입 기록 | [docs/prototype/mockup-player.md](docs/prototype/mockup-player.md) | 목업의 화면·상태, 구현 인계 사항 |
| 운영 절차 | [docs/runbook/local-demo.md](docs/runbook/local-demo.md) | 시연 PC에서 어떻게 띄우고 무엇으로 성공을 판단하는가 |
| 킥오프 브리프 | [docs/briefs/2026-09-18-kickoff.md](docs/briefs/2026-09-18-kickoff.md) | 합의된 방향, 협의 안건, 사업비 질문 |
| 목업 | [docs/mockup/README.md](docs/mockup/README.md) | 단일 HTML 목업 실행·테마·빌드 구조. 기본 테마 코발트가 구현 기준 |
| 디자인 레퍼런스 | [docs/references/design-references.md](docs/references/design-references.md) | 참고한 사이트와 가져온 것 |
| 서비스 검토안 v0.5 | [docs/gait-insight-service-review-v0.5.html](docs/gait-insight-service-review-v0.5.html) | 기획자 전달용 HTML |
| 원본 자료 | `docs/analysis/` (레포 미포함) | 학과 원안 계획서(hwp), 전문가 자료 스마트인솔 상세판 3종(docx) |

※ 원본 자료는 비공개 유지를 위해 `.gitignore`로 제외. 로컬에만 보관함

## 실행

```sh
cp .env.example .env     # AUTH_SECRET 입력
docker compose up --build
```

- 화면: `http://localhost:8000`
- API 문서(Swagger UI): `http://localhost:8000/docs`
- 같은 로컬망 휴대폰: `http://<호스트IP>:8000`
- 상세 절차·문제 해결: [시연 runbook](docs/runbook/local-demo.md)

## 상태

- 동작: 로그인·기록 목록·분석·추천 운동 화면, API
- 기록: 실측이 아닌 합성 신호 3개. 전문가 자료(상세판 3종)의 가상 사례값에 맞춤, 각각 유형 1·3·2로 판정됨
- 지표·유형·운동 프로그램: 자료를 따름
  - 임계값은 자료에 판정 수치가 없어 시연값 사용. 학과 확인 안 함
- 운동 후 재평가: 다시 잴 항목만 표시. 전후 비교 안 함

남은 일:

| 항목 | 내용 |
| --- | --- |
| 유형 판정 임계값 | 학과 확인 후 새 규칙 세트로 반영 |
| PhysioNet 대조군 기록 | 계속 쓸지 결정 필요. 정적 측정·보행검사 입력이 없어 M01·M09·M10 산출 불가 |
| LLM 설명 | 연결 여부 결정 필요 |
