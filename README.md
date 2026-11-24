---
type: project-scope
status: draft
---

**English** | [한국어](README.ko.md)

# gait-insight

A capstone design prototype for a geriatric rehabilitation exercise department. It analyzes **public gait data** and shows the **observed gait features** and **recommended exercises** on the web and mobile web — built with **FastAPI + React + PostgreSQL** and run locally with **Docker Compose**.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)](https://vite.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Platform](https://img.shields.io/badge/Platform-Web%20%7C%20Mobile%20Web-555)](#mockup-demo)

> A demo prototype for a local network. Public deployment of the app server is out of scope.

Core flow: **select a record → visualize plantar pressure → explain observed features → recommend exercises**.

- **Numbers come from code.** Exercise recommendations follow criteria reviewed by the department.
- **AI is optional.** If used, it only rephrases computed results in plain language; prepared text works without it.
- **Data**: only the **73 healthy control subjects** from the PhysioNet Parkinson's disease gait study.
- Background and open issues: [kickoff brief](docs/briefs/2026-09-18-kickoff.md) (Korean).

## Mockup demo

Static HTML — opens directly in a browser. Demo login: `admin` / `0000`.

| Target | URL |
| --- | --- |
| Phone | <https://pis-o-cake.github.io/gait-insight/mockup/gait-insight-mobile.html> |
| Desktop · Tablet | <https://pis-o-cake.github.io/gait-insight/mockup/gait-insight-demo.html> |

- Share the **link**, not the file. Attachment previews (KakaoTalk, mail, iOS Files) do not run JavaScript and show a blank page.
- GitHub Pages serves the `docs/` folder of `main`. Changes appear 1–2 minutes after a push.

## Scope (범위)

| Area | Included |
| --- | --- |
| Data | Healthy controls only from PhysioNet gaitpdb v1.0.0, selected and converted. Source and license (ODC-By) credited |
| Screens | Record list, gait analysis (heatmap playback, overview/zoom charts, metric tiles, summary), exercise guide (step flow per feature) |
| Login | ID/password sign-up and login, bcrypt hashing, cookie session. Screens and API require login |
| Analysis | Metrics M01–M10 based on three expert references (8 insole + 2 gait-test inputs) and gait type classification (T1 load imbalance · T2 step-length difference · T3 normal). Reasons returned when a metric cannot be computed |
| Exercise | 18 exercises from the expert references (purpose, method, dosage, cautions), type → program mapping, rationale and re-assessment items, review status |
| Storage | PostgreSQL (record metadata, exercise content, rule sets, results) + parquet (sensor time series). Alembic migrations and seed tools |
| Runtime | `docker compose up --build` starts `db` + `app`. Only host port 8000 is exposed |

**Not included**: insole hardware, sensor calibration, Bluetooth streaming · running/squat/lunge analysis · disease diagnosis, fall risk, intervention efficacy · before/after comparison · native apps · password rules, email verification, password reset, roles · uploads and personal record storage · public deployment of the app server · LLM explanations (interface only).

## Definition of Done (DoD)

| Feature | Done when |
| --- | --- |
| Data preparation | Control selection criteria are documented against the demographics table; converted records pass column-count, time-axis and unit checks; excluded records and reasons are reported |
| Login | After sign-up and login the record list opens; when logged out or the cookie expires, every screen returns to login. No password rules |
| Record list | Each row shows name, condition, duration and source with a 6-second sparkline preview; rows do not clip at phone width |
| Gait analysis | Play, pause, restart, seek and speed (0.5–30×) work; heatmap, charts and seek bar point to the same time. All 10 metrics show left/right values and status chips per group, with a reason when not computable |
| Exercise guide | Each observed feature shows evidence (numbers), rationale and exercise cards in one block, with a review-status tag. With no observations, only general exercises are shown |
| Metric computation | Matches mockup values on synthetic-signal tests; short records and no-contact cases return reason codes |
| Startup · DB init | On a clean PC with only Docker, one `docker compose up --build` runs migrations, seeding and the server; changing the rule set recomputes results as a new version without a restart |
| LAN access | A phone on the same network opens `http://<IP>:8000` and completes all three screens, following the runbook |
| Docs | `engsys verify` passes |

## Getting started

```sh
cp .env.example .env     # set AUTH_SECRET
docker compose up --build
```

- App: `http://localhost:8000`
- API docs (Swagger UI): `http://localhost:8000/docs`
- Phone on the same LAN: `http://<host-ip>:8000`
- Details and troubleshooting: [demo runbook](docs/runbook/local-demo.md) (Korean)

## Project structure

```
backend/    FastAPI app (per-domain: api · service · crud · schemas · models), Alembic, seed data
frontend/   React + TypeScript (Vite)
docs/       architecture, design proposals, runbook, mockups (served by GitHub Pages)
scripts/    verify.sh — project verification
```

## Documentation

Documents follow the [Engineering System](https://github.com/pis-o-cake/engineering-system) contract (`.engsys/project.yaml`). All documents are in Korean.

| Type | Location |
| --- | --- |
| Architecture | [docs/architecture/README.md](docs/architecture/README.md) |
| Design proposals | [docs/design](docs/design) — 0001 architecture, 0002 infra, 0003 data model, 0004 API · analysis, 0005 screens |
| Prototype record | [docs/prototype/mockup-player.md](docs/prototype/mockup-player.md) |
| Runbook | [docs/runbook/local-demo.md](docs/runbook/local-demo.md) |
| Mockup | [docs/mockup/README.md](docs/mockup/README.md) |
| Design references | [docs/references/design-references.md](docs/references/design-references.md) |
| Service review v0.5 | [docs/gait-insight-service-review-v0.5.html](docs/gait-insight-service-review-v0.5.html) |

Source materials (the department's original proposal and the expert references) are kept locally and excluded from this repository.

## Status

- Working: login, record list, analysis and exercise screens, API.
- Records are **three synthetic signals**, not real measurements, tuned to the case values in the expert references; they classify as types 1, 3 and 2.
- Classification thresholds are **demo values** — the references give no cut-offs and the department has not confirmed them yet.
- Re-assessment lists the items to re-measure; no before/after comparison.

Open items:

- Confirm thresholds with the department and ship them as a new rule set.
- Decide whether to keep the PhysioNet controls — without a static stance or gait-test inputs, M01, M09 and M10 cannot be computed.
- Decide whether to connect LLM explanations.
