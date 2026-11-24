---
type: prototype-record
status: active
prototype-version: 2026-09-21-player
prototype: docs/mockup/gait-insight-demo.html
---

# 목업 기록 · 플레이어 골격

목업은 파일 하나(`docs/mockup/gait-insight-demo.html`)이며 기본 테마 "코발트"(옛 시안 3)가 실제 구현의 화면 기준이다. 라이트 모노톤에 코발트 한 색, 하단 고정 재생 독, 전체 폭 스테이지, 세로 스텝 플로우 운동정보로 구성된다. 상단 스와치로 테마 4종(코발트·샌드스톤·나이트·세이지)을 바꿀 수 있고 UX·마크업·JS는 공통이다. 테마 전환은 시안 비교용이며 실제 구현에는 기본 테마만 옮긴다. 옛 시안 1의 사이드 HUD 골격은 `docs/mockup/archive/`에만 있고 구현 기준이 아니다. 세 시안의 빌드 방법과 파일 구성은 [목업 안내](../mockup/README.md)에 있다.

## 대상과 version

| 항목 | 값 |
| --- | --- |
| 파일 | `docs/mockup/gait-insight-demo.html` (2026-09-21 단일 파일·테마 전환 판) |
| 생성 | `docs/mockup/build/build-skins.py`가 `archive/gait-insight-demo-v1-original.html`의 데이터·계산 로직에 `build/base-style.css`와 공통 렌더러, 테마 토큰 4벌을 얹어 한 파일로 만든다 |
| 실행 | 파일 더블클릭. 외부 요청 0건, 서버 불필요 |
| 확인한 환경 | Chrome 헤드리스 1280px·390px 캡처. Safari·실기기는 미확인 |
| 데이터 | 합성 신호 3건(demo-01~03), 10분·100 Hz. 실제 기록 아님 |
| 참고 디자인 | [디자인 레퍼런스](../references/design-references.md) 14~16번 |

## 화면과 상태

해시 라우팅 `#/list` → `#/analysis/<id>` → `#/exercise/<id>`. 브라우저 뒤로가기가 동작한다.

| 화면 | 구성 | 상태·조작 |
| --- | --- | --- |
| 기록 선택 | 큰 행 3개 + 6초 스파크라인(왼발 잉크·오른발 코발트) | 행 클릭 → 분석 |
| 보행 분석 | 상단 기록 A/B/C 세그먼트 탭, 전체 폭 스테이지(Canvas 히트맵, 큰 시간 표시, 좌우 순간값 배지), 우상단 "표시 설정" 팝오버(팔레트·표시 하한·윤곽/센서/CoP 스위치), 개요 그래프 + 현재 ±5초 확대 그래프, 지표 4열 벤토 타일(좌우 큰 숫자·비교 막대·상태 칩), 요약 카드, 하단 고정 재생 독(재생/처음으로/시크/배속 세그먼트) | `state.t` 하나를 히트맵·그래프 커서·시크바가 공유. 재생 종료·기록 전환·화면 이동 시 타이머 해제. 팝오버는 바깥 클릭·Esc로 닫힘 |
| 추천 운동 | 특징별 세로 스텝 플로우: 1 관찰한 것(수치) → 2 권하는 이유 → 3 운동 카드. 왼쪽 레일 번호 노드가 뷰포트 진입 시 점등. 괜찮아 보이는 부분 + 일반 운동 | 카드 "자세히 보기" 펼침(`grid-template-rows`), 분석으로 복귀 |

모션은 화면 진입 스태거 1회, 지표 카운트업, 막대 채움, 독 슬라이드업이며 `prefers-reduced-motion`이면 전부 끈다.

## 구현 인계 사항

목업과 실제 버전의 차이는 데이터 출처와 계산 위치다. 화면·조작은 그대로 옮긴다.

| 목업 위치 | 실제 버전 | 비고 |
| --- | --- | --- |
| `build/base-style.css` + 기본 테마 토큰(`build-skins.py`의 `SKINS["v3"]`) | `frontend/src/styles/base.css`, `tokens.css` | 캔버스 오버레이 색은 `--viz-*` 토큰을 JS가 읽는 구조 유지. 다른 테마와 `html[data-theme]` 전환은 옮기지 않는다 |
| §1 `STR` | `frontend/src/locales/ko.json` | 키 이름 유지. `{param}` 치환 방식 유지 |
| §2 `CFG.rules`, `contactThresholdN`, `analysisTrimSec` | `backend/data/seed/rule_set.demo.json` → `rule_set.thresholds` | 시연값 그대로, 버전 `demo-1` |
| §2 `PALETTES`, `SENSOR_LEFT`, `FRONT_IDX` | 프론트 `lib/palette.ts` / 백엔드 `metrics.py` | 센서 좌표는 PhysioNet format.txt 값. 양쪽에 같은 상수가 있으므로 테스트로 일치 확인 |
| §3 `RECORDS` (합성 프로필) | `frontend/src/fixtures/` (목업 모드 전용) | 실제 모드는 `record` 테이블 |
| §4 `EXERCISES`, `LINK_RULES`, `GENERAL_EXERCISES` | `seed/exercises.json` → `exercise` 테이블, `seed/rule_set.demo.json` → `link_rule` | 권유 이유 문장은 locale 키로. `GENERAL_EXERCISES`는 `exercise.is_general` |
| §5 신호 생성기 | `backend/tests/fixtures/synth.py` | 테스트 기대값 산출용 |
| §6 `analyze()` | `backend/app/domain/analysis/metrics.py` | [설계 0004](../design/0004-api-and-analysis.md) 결정과 대안 절 |
| §7 IDW 보간·캔버스 | `components/stage/HeatmapCanvas` + `lib/idw.ts` | 계산 부담이 크면 `OffscreenCanvas` 검토 |
| §8·§9·§10 렌더러 | `pages/*` + `components/*` | 문자열 템플릿 → JSX. 클래스명은 유지해 CSS 재사용 |

목업이 다루지 않아 실제 버전에서 새로 정해야 하는 것:

- 로그인 화면과 상단 내비의 사용자 표시·로그아웃(목업에는 인증이 없다)
- 계산 불가 지표 타일의 표현(사유 문구 위치)
- 기록이 3개를 넘을 때 상단 세그먼트 탭의 처리(스크롤 또는 드롭다운)
- 로딩·오류 상태(서버 미기동, 404) 화면
- 실제 기록의 길이가 10분이 아닐 때 개요 그래프 눈금
