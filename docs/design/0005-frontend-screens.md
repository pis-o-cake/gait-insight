---
type: design-proposal
status: review
date: 2026-09-21
prototype: docs/prototype/mockup-player.md
---

# 0005. 프론트엔드 화면

목업의 플레이어 골격(하단 재생 독, 전체 폭 스테이지, 세로 스텝 플로우)을 React로 옮긴다. 화면은 데이터 창구 네 함수만 호출하며, 목업 모드는 내장 fixture를, 실제 모드는 [0004](0004-api-and-analysis.md)의 API를 같은 형태로 돌려준다. 목업 §별 이식 대응표와 목업이 다루지 않은 항목은 [프로토타입 기록](../prototype/mockup-player.md)에 있다.

## 제안 요약

- TypeScript + React + Vite. 상태 관리 라이브러리·차트 라이브러리 없이 목업 렌더러를 컴포넌트로 옮긴다.
- 스타일은 목업 `build/base-style.css`와 기본 테마(코발트) 토큰을 `styles/`로 이식한다. 나머지 테마 토큰과 테마 전환 UI는 옮기지 않는다.
- 해시 라우터(`#/login`, `#/list`, `#/analysis/:id`, `#/exercise/:id`)로 목업과 같은 이동·뒤로가기를 유지한다. 로그인 전에는 모든 경로가 `#/login`으로 간다.
- 빌드 결과는 `app` 컨테이너 이미지에 포함돼 FastAPI가 `/`에서 서빙한다. 개발 중에는 Vite가 `/api`를 8000으로 프록시한다.

```text
  frontend/
    package.json  vite.config.ts  (dev proxy /api → :8000)
    src/
      main.tsx  App.tsx  router.ts        해시 라우터 (#/list, #/analysis/:id, #/exercise/:id)
      pages/    LoginPage  ListPage  AnalysisPage  ExercisePage
      components/
        stage/   HeatmapCanvas  StageHud  SettingsPopover  Legend
        dock/    PlaybackDock  (재생·처음으로·시크·배속 세그먼트)
        chart/   OverviewChart  DetailChart
        metric/  MetricTile  MetricGrid  StatusChip
        exercise/ FeatureStep  ExerciseCard
        ui/      Steps  Button  Segment  Switch
      data/     client.ts (api, credentials: include)  mock.ts (fixture)  index.ts (모드 선택)  auth.ts (me/login/register/logout)
      fixtures/ demo records (목업 이식)
      hooks/    usePlayback  useRoute
      lib/      idw.ts  palette.ts  format.ts
      types/    record.ts  analysis.ts  exercise.ts
      locales/  ko.json
      styles/   tokens.css  base.css
```

## 설계

### 데이터 창구

`data/index.ts`가 `VITE_DATA_MODE`(`api` | `mock`)로 구현을 고른다. 네 함수의 반환 타입은 `types/`에 있고 API 응답 스키마와 1:1이다.

| 함수 | 실제 모드 | 목업 모드 |
| --- | --- | --- |
| `listRecords()` | `GET /api/record` | `fixtures/records.ts` |
| `getRecord(id, step)` | `GET /api/record/{id}?step=` | 합성 신호 생성기(목업 §5 이식) |
| `getAnalysis(id)` | `GET /api/analysis/{id}` | `lib/analyze.ts`(목업 §6, 표시 검증용) |
| `getExercise(id)` | `GET /api/exercise/{id}` | `fixtures/exercises.ts` |
| `me()` · `login()` · `register()` · `logout()` | `/api/auth/*` | 항상 로그인된 가짜 사용자 |

목업 모드의 `analyze.ts`는 화면 개발용이며 지표 정의의 정본은 백엔드다. 두 구현이 어긋나면 백엔드가 맞다.

### 화면 상태

```text
auth:     { user | null, checked }                AppShell이 기동 시 me() 한 번. 401이면 #/login
route:    login | list | analysis(id) | exercise(id)
playback: { t, playing, speed }            AnalysisPage 지역 상태 (usePlayback)
display:  { palette, cutoffN, outline, sensors, cop }   localStorage 유지
```

목업의 `state.t` 공유 원칙을 유지한다. 히트맵·개요 그래프 커서·확대 그래프·시크바가 같은 `t`를 읽는다. 화면 이동·기록 전환 시 재생 타이머를 해제한다.

### 화면별 컴포넌트

| 화면 | 페이지 | 주요 컴포넌트 | 데이터 |
| --- | --- | --- | --- |
| 로그인 | `LoginPage` | 아이디·비밀번호 입력 카드 하나, 로그인/가입 토글. 실패는 카드 안 한 줄 문구 | `login`, `register` |
| 기록 선택 | `ListPage` | 기록 행 + 6초 스파크라인. 상단 내비에 표시 이름·로그아웃 | `listRecords`, `logout` |
| 보행 분석 | `AnalysisPage` | `HeatmapCanvas`(IDW 보간, `--viz-*` 토큰), `StageHud`(시간·좌우 순간값), `SettingsPopover`(팔레트·하한·오버레이), `OverviewChart`·`DetailChart`(SVG), `MetricGrid`·`MetricTile`·`StatusChip`, `PlaybackDock` | `getRecord`, `getAnalysis` |
| 추천 운동 | `ExercisePage` | `FeatureStep`(관찰→이유→운동, IntersectionObserver 점등), `ExerciseCard`(펼침) | `getAnalysis`, `getExercise` |

API 호출이 401을 돌려주면 데이터 창구가 `auth.user`를 비우고 `#/login`으로 보낸다. 계산 불가 지표는 `MetricTile`이 값 대신 사유 문구를 그린다. 서버 미기동·404는 페이지 공통 오류 카드로 표시하고 목록으로 돌아가는 버튼을 둔다. 모션은 `prefers-reduced-motion`이면 전부 끈다.

### 검증

목업 모드로 화면 3개 렌더 테스트, 1280px·390px 스냅샷. 히트맵·그래프·시크바가 같은 `t`를 가리키는지 재생 중 상태 검사.
