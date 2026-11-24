---
type: guide
status: active
---

# 디자인 참고 사이트 (16)

기준: 기록 선택 → 발바닥 하중 시각화(재생) → 쉬운 설명 → 운동정보 카드 흐름, 고령자·비전문가 가독성, 라이트 톤.

| # | 사이트 | 참고 포인트 | 가져올 것 |
| --- | --- | --- | --- |
| 1 | [Gait Analysis Application (bionichaos)](https://bionichaos.com/GaitAnalysis/) | 양발 히트맵 + Play/Pause + 프레임 슬라이더 + 배속, 팔레트 전환, 발 윤곽 오버레이 | 분석 화면 중심영역 구조 그대로 (재생바·발 윤곽·색 팔레트) |
| 2 | [Moticon](https://moticon.com/) | 인솔 압력맵·시간 그래프를 앱 대시보드로 묶은 구성, 단일 포인트 컬러(오렌지)+화이트 | 발그림·그래프 나란히 배치, 강조색 1개 원칙 |
| 3 | [Tekscan Human Gait Analysis](https://www.tekscan.com/products-solutions/human-gait-analysis) | 힘-시간 곡선(뒤꿈치/앞발), 압력 분포, 보행 파라미터 표(stance/swing) | 좌우 하중 그래프·요약 수치 표의 항목 이름과 단위 |
| 4 | [Digitsole Pro](https://www.digitsole.com/) | 임상 데이터를 환자에게 설명하는 리포트, 걷기·달리기 동적 분석 | "선택한 기록에서 관찰된 특징" 설명 카드 형식 |
| 5 | [OneStep](https://www.onestep.co/) | 30+ 지표를 Walk Score 하나로 요약, 환자용/임상용 화면 분리 | 핵심 수치 카드(좌우 차이·접촉 시간) 우선 노출 |
| 6 | [Oura](https://ouraring.com/) | 점수·상태를 차분한 톤과 평이한 문장으로 전달 | 결과 설명 영역 문체·여백·타이포 |
| 7 | [Bold (agebold)](https://www.agebold.com/) | 65+ 대상 운동 클래스, 큰 글자·넓은 여백·낙상예방 메시지 | 운동정보 카드 크기·대비·사진 톤 |
| 8 | [Physitrack](https://www.physitrack.com/) | 재활 운동 라이브러리, 운동 카드(영상·반복 수·설명) | 운동 카드 펼치기 UI, 동작 설명 구조 |
| 9 | [The Pudding](https://pudding.cool/) | 데이터 스토리텔링, 그림+짧은 문장으로 숫자 해설 | 히트맵·그래프 옆 "이 숫자는 무엇인가" 설명 방식 |
| 10 | [Muzli 대시보드 모음 (2026)](https://muz.li/blog/best-dashboard-design-examples-inspirations-for-2026/) | 헬스 대시보드 10종 — 특히 [Health Records 환자 모니터링(라이트)](https://me.muz.li/orbix-studio/healthcare-analytics-dashboard-patient-monitoring-ui) | PC 2단 카드 레이아웃, 라이트 모드 색 체계 |

## 시안 2 (다크·모던) 추가 참고

| # | 사이트 | 참고 포인트 | 가져올 것 |
| --- | --- | --- | --- |
| 11 | [Oura 앱 리디자인 (2025)](https://ouraring.com/blog/new-app-design/) · [WHOOP 앱 (2026)](https://liveworksleep.com/whoop-app-features/) | 한 화면에 핵심 하나("One Big Thing"), 다크 배경 위 데이터 색 최소화 | 요약 카드가 특징 n개만 크게, 나머지는 조용히 |
| 12 | [Linear · Vercel · Raycast 계열 SaaS 대시보드 (2026)](https://www.925studios.co/blog/saas-dashboard-design-examples-2026) · [다크 대시보드 모음](https://adminlte.io/blog/dark-dashboard-templates/) | 다크 퍼스트, 순검정 대신 남색, 그림자 없이 표면 밝기로 층위, 강조색 1개 절제 | `:root` 토큰 구조(bg/surface/surface-2/surface-3), 헤어라인 보더 |
| 13 | [2026 UI 트렌드: 글래스·벤토](https://blog.brucira.com/top-ui-design-trends/) · [Midrocket 2026 가이드](https://midrocket.com/en/guides/ui-design-trends-2026/) | 반투명 글래스는 내비 같은 얕은 층에만, 벤토형 카드 그리드 | sticky 내비 `backdrop-filter`, 지표 4타일 벤토 |

## 시안 3 (라이트·플레이어) 추가 참고

| # | 사이트 | 참고 포인트 | 가져올 것 |
| --- | --- | --- | --- |
| 14 | [Apple Design Awards 2026](https://developer.apple.com/design/awards/) — Tide Guide(Visuals) · Moonlitt(Interaction) | 전체 화면 차트, 데이터 하나를 크게, 커스텀 애니메이션, 유리(Liquid Glass) 부유 컨트롤 | 전체 폭 스테이지 + 떠 있는 재생 독, 큰 시간 숫자 |
| 15 | [Awwwards 2026 수상작 정리](https://www.hontran.dev/blog/best-award-winning-websites-2026) — By-Kin 등 | 절제된 편집 타이포, 한 번의 진입 모션, 연속된 표면 | 큰 헤드라인(-.04em), 화면 진입 스태거 1회, 보더 없는 카드 |
| 16 | [토스 디자인 시스템(TDS) 공개](https://developers-apps-in-toss.toss.im/design/components.html) | 흰 카드 + 회색 캔버스, 세그먼트 컨트롤, 스위치, 필 버튼, 한 가지 파랑 | 기록 탭·배속 세그먼트, 팝오버 스위치, 코발트 1색 원칙 |

## 정리

- 화면 골격: 1·2·3 (히트맵·그래프·재생)
- 설명·수치 전달: 4·5·6·9
- 운동정보·고령자 접근성: 7·8
- 전체 레이아웃·색: 10 (시안 1) · 11~13 (시안 2) · 14~16 (시안 3)
