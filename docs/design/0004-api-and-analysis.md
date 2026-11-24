---
type: design-proposal
status: review
date: 2026-09-21
---

# 0004. API와 분석 파이프라인

백엔드는 `auth`·`record`·`analysis`·`exercise` 네 도메인이며 각 도메인이 `api → service → crud → models` 흐름을 갖는다. 분석은 목업 §6 `analyze()`를 이식한 `metrics.py`가 parquet을 읽어 계산하고, 활성 규칙 세트로 관찰 판정·운동 연결을 한 뒤 결과를 캐시한다. 데이터 모델은 [0003](0003-data-model-and-storage.md), 이 API를 쓰는 화면은 [0005](0005-frontend-screens.md)에 있다.

## 제안 요약

- 라우터는 `app/domain/*/api.py`를 스캔해 `/api/<domain>`에 자동 등록한다. 상세 스키마는 Swagger UI(`/docs`)가 정본이다.
- `auth`를 뺀 모든 엔드포인트는 `Depends(current_user)`로 로그인 쿠키를 요구한다. 없거나 만료면 401 `auth.required`.
- 지표 정의는 목업과 동일하며 임계값은 `rule_set.thresholds`에서 읽는다.
- 계산 불가는 `ok=false`와 사유 코드로 반환한다. 0이나 NaN을 값으로 내보내지 않는다.
- 사용자 문장은 `core/locales/ko.json`에서 조립한다. LLM 설명은 `Explainer` 프로토콜로 자리만 둔다.

```text
  backend/
    pyproject.toml
    app/
      main.py                 라우터 자동 등록, 정적 파일 마운트, CORS(개발용), lifespan에서 DB 연결
      core/
        config.py             pydantic-settings (.env: HOST, PORT, DATABASE_URL, DATA_DIR, LLM_*)
        db.py                 async engine, session factory, get_session Depends
        errors.py             AppError 계열 + 핸들러 (코드 → locale 메시지)
        locales/ko.json       API 응답 문구
        io.py                 parquet 로더 (LRU 캐시)
      domain/
        auth/     api.py service.py crud.py schemas.py models.py security.py (bcrypt, JWT) deps.py (current_user)
        record/   api.py service.py crud.py schemas.py models.py
        analysis/ api.py service.py crud.py schemas.py models.py metrics.py rules.py explain.py
        exercise/ api.py service.py crud.py schemas.py models.py
    tests/
```

## 설계

### API

라우터는 `app/domain/*/api.py`를 스캔해 `/api/<domain>`에 붙인다. 상세 스키마는 Swagger UI가 정본이며 여기서는 계약만 적는다.

| 메서드·경로 | 응답 | 오류 |
| --- | --- | --- |
| `POST /api/auth/register` | `{loginId, password, displayName}` → `User`. 비밀번호는 비어 있지만 않으면 된다. 응답과 함께 로그인 쿠키 발급 | 409 `auth.login_id_taken` |
| `POST /api/auth/login` | `{loginId, password}` → `User` + 쿠키. 아이디 없음과 비밀번호 틀림을 구분하지 않는다 | 401 `auth.invalid_credentials` |
| `POST /api/auth/logout` | 쿠키 삭제 | 없음 |
| `GET /api/auth/me` | `User`: id, loginId, displayName | 401 `auth.required` |
| `GET /api/record` | `RecordSummary[]`: id, name, participant, condition, durationSec, sampleRate, source, license, isDemo, preview(6초 좌·우 합계 60점) | 없음 |
| `GET /api/record/{id}?step=1` | `RecordData`: time[], left[8][], right[8][], leftSum[], rightSum[], unit `N`, sensorPositions. `step`은 표시용 간격(1=원본) | 404 `record.not_found`, 500 `record.file_missing` |
| `GET /api/analysis/{id}` | `Analysis`: window{from,to}, staticWindow, metrics{M01..M10}, observations[], links[](유형별 프로그램), watch[], summary, ruleSetVersion, computedAt. 캐시가 있으면 반환, 없으면 계산 후 저장 | 404, 422 `analysis.too_short`, 409 `analysis.no_active_rule_set` |
| `GET /api/exercise/{id}` | `Exercise`: id, name, purpose, steps[], caution[], dosage, source, reviewStatus, isGeneral | 404 |
| `GET /api/exercise` | `ExerciseSummary[]` | 없음 |

오류 본문은 `{code, message}`이며 `message`는 locale JSON에서 조립한다. `auth` 이외 행은 모두 401 `auth.required`가 추가로 가능하다. 시간 배열과 센서 배열 길이는 같아야 하며 서비스 계층이 단언한다.

### 지표 정의 (전문가 자료 기준)

지표는 `docs/analysis`의 스마트인솔 상세판 3종(좌우보행불균형·좌우보폭차이·정상보행유지)이 꼽은 측정 항목을 따른다. 기록은 자료의 측정 절차대로 앞쪽 정적 측정(양발로 선 20초)과 뒤쪽 자유 보행으로 나뉜다. 정적 구간은 기록 시작부터 양발이 모두 닿아 있는 동안이며, 첫 발 떼기 0.5초 전까지를 쓰고 `staticMinSec`(5초)보다 짧으면 없다고 본다. 보행 구간은 시작·끝 `analysisTrimSec`(1초)를 제외한 뒤 왼발 첫 접촉 시작부터 마지막 접촉 시작까지다. 접촉은 발 합계가 `contactThresholdN`(25 N) 이상인 연속 구간이며, 정적 구간의 연속 접촉은 걸음으로 세지 않는다.

| 지표 | 정의 | 단위 | 출처 |
| --- | --- | --- | --- |
| M01 정적 족저압 비율 | 정적 구간 좌·우 합계 평균의 비율 | % | 인솔 |
| M02 동적 족저압 비율 | 보행 구간 좌·우 합계 시간 적분의 비율 | % | 인솔 |
| M03 입각기 시간 | 좌·우 접촉 구간 길이 평균. `extra`에 보행 주기 대비 %와 유각기 | s | 인솔 |
| M04 한발 지지 시간 | 이 발 접촉 중 반대 발이 떠 있던 시간의 걸음당 평균 | s | 인솔 |
| M05 걸음 시간 | 반대 발 접촉 시작에서 이 발 접촉 시작까지. 보장 차이의 대리 지표 | s | 인솔 |
| M06 분당 걸음 수 | 120 ÷ 평균 보행 주기. `left`·`right`는 발별 보행 주기 | steps/min | 인솔 |
| M07 보행 주기 변동 | 같은 발 접촉 시작 간격의 변동계수 | % | 인솔 |
| M08 앞쪽 하중 비율 | 앞쪽 센서군(인덱스 5·6·7) 합 / 전체 합 | % | 인솔 |
| M09 보장 | 좌·우 한 걸음 길이 | cm | 보행검사 입력 |
| M10 보행 속도 | 10m 보행검사 거리 ÷ 시간 | m/s | 보행검사 입력 |

각 지표는 `{left, right, value?, unit, ok, diffPct?, reason?, extra}`다. M01·M02의 `diffPct`는 좌우 비율 차이(%p), 나머지는 큰 값 대비 %다. 정적 구간이 없으면 M01이 `analysis.no_static`, 보행검사 입력(`record.walk_test`)이 없으면 M09·M10이 `analysis.no_walk_test`로 계산 불가다.

### 보행 유형 판정과 운동 프로그램

`explain.py`가 지표별 관찰(차이 있음/작음 등)을 만든 뒤 유형을 판정한다. 주 지표가 하나라도 기준을 넘으면 그 유형이고, 보조 지표 중 넘은 것은 근거 문장에 덧붙는다. T1·T2에 모두 해당하지 않으면 T3다.

| 유형 | 주 지표 (`thresholds` 키) | 보조 지표 | 운동 프로그램 |
| --- | --- | --- | --- |
| T1 좌·우 체중 부하 불균형 | M01 ≥ `staticShareDiffPp`, M02 ≥ `dynamicShareDiffPp` | M03, M04 | 자료 4종 |
| T2 좌·우 보장 차이 | M09 ≥ `stepLengthDiffPct` | M05 ≥ `stepTimeDiffPct`, M03, M10 | 자료 10종 |
| T3 정상 보행 유지 | T1·T2 미해당 | M01·M02·M09·M06을 근거로 표시 | 자료 8종 |

유형과 별개로 T3 자료의 '잠재적 문제'인 M07 리듬 불규칙(≥ `cycleCvPct`), M08 압력 패턴 치우침(≥ `frontHighPct` 또는 ≤ `frontLowPct`), M10 속도 저하(< `speedLowMps`)는 `watch[]`로 낸다. 프로그램을 추가하지 않는다.

활성 규칙 세트의 `link_rule`은 유형 → 운동 ID 목록·권유 이유·재평가 항목이다. 판정된 유형마다 링크 하나가 만들어진다. 설명문은 locale 템플릿에 수치를 넣어 만든다. LLM 설명은 같은 입력을 받는 `Explainer` 프로토콜로 자리만 두고 구현하지 않는다. 자료에 판정 수치가 없어 시연용 세트 `expert-1`의 임계값(10·10·8·10·8·10·6·50·28·1.0)은 학과 확인 전 값이다.

## 결정과 대안

### 로그인은 최소 구성

아이디·비밀번호 하나로 가입·로그인한다. 비밀번호는 bcrypt(passlib 또는 pwdlib)로 해시하고, 로그인 성공 시 HS256 JWT(`sub=user_id`, `exp`=`AUTH_TOKEN_TTL_HOURS`)를 httpOnly 쿠키로 내려준다. 서버는 세션을 저장하지 않는다. 비밀번호 규칙·이메일 인증·비밀번호 찾기·권한 등급·가입 승인은 두지 않는다.

배경: 사용자는 시연이라도 로그인 뼈대는 있어야 한다고 판단했고, 암호화는 형식만 갖추되 규칙류는 전부 빼라고 했다. 데이터는 공용이라 사용자별 권한 구분이 필요 없다.

| 대안 | 거절 이유 |
| --- | --- |
| 로그인 없음 | 사용자가 뼈대를 원했다. 나중에 개인 기록이 생기면 붙일 자리가 없다 |
| DB 세션 테이블 + 불투명 토큰 | 로그아웃 즉시 무효화가 되지만 테이블·정리 작업이 늘어난다. 12시간 만료로 충분하다 |
| OAuth·소셜 로그인 | 인터넷과 외부 클라이언트 등록이 필요해 로컬망 시연과 맞지 않는다 |

비용: 로그아웃은 쿠키 삭제뿐이라 탈취된 토큰은 만료까지 유효하다. `AUTH_SECRET`이 바뀌면 전원 로그아웃된다. 비밀번호 규칙이 없으므로 `1` 같은 비밀번호도 허용되며 이는 의도다.

### 지표와 유형은 전문가 자료 기준, 임계값은 규칙 세트

지표 정의와 유형·운동 프로그램은 학과가 보낸 전문가 자료 3종을 따른다. 목업 §6의 M01~M04 정의는 동적 족저압 비율(M02)·입각기(M03)·보행 주기 변동(M07)·앞쪽 하중 비율(M08)로 남기고, 자료가 요구한 정적 족저압·한발 지지·걸음 시간·분당 걸음 수와 보행검사 입력값(보장·속도)을 더했다. 시연 기록 3개는 자료의 가상 사례값(유형 1: 정적 42:58·입각기 0.56/0.66초, 유형 2: 보장 48/60 cm·0.80 m/s, 유형 3: 49:51·분당 110걸음)에 맞춰 합성하고, 테스트는 각 기록이 의도한 유형으로 판정되는지 확인한다. 임계값은 활성 `rule_set.thresholds`에서 읽는다.

배경: 프로젝트는 운영 서비스가 아닌 시연용 목업이며, 기존 데이터는 화면 확인용으로 맞춰 넣은 합성 신호였다. 전문가 자료가 도착해 결과가 자료 기준으로 나오도록 데이터와 지표를 함께 바꿨다. 자료는 압력 인솔만으로 보장·속도·골반 움직임을 정확히 잴 수 없다고 반복해 밝히므로, 보장·속도는 기록에 보행검사 입력값으로 따로 둔다.

| 대안 | 거절 이유 |
| --- | --- |
| 목업 M01~M04 유지 | 자료의 유형 1·2 주 지표(정적 비율·보장)를 낼 수 없다 |
| 인솔 신호로 보장 추정 | 자료가 정확한 측정이 불가하다고 밝힌다. 걸음 시간(M05)은 자료에 없는 대리 지표라 판정에 쓰지 않고 보조 근거로만 보인다 |
| 유형별 판정 기준을 코드에 고정 | 임계값은 학과 확인 전이라 바뀐다. 주·보조 지표 구성만 코드에 두고 수치는 규칙 세트에 둔다 |

비용: 자료에 판정 수치가 없어 임계값은 시연값이다. 유형별로 같은 운동의 운동량이 다를 때(예: 싱글 레그 밸런스) 한 운동에 범위를 합쳐 적었다. 정적 구간이 없는 실측 기록은 M01을 계산하지 못한다.

