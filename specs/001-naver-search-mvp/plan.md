# Implementation Plan: 네이버 검색 운영 MVP

**Branch**: `001-naver-search-mvp` | **Date**: 2026-05-28 | **Spec**: [spec.md](/Users/jaeiklim/dev/work/naver-search-ops/specs/001-naver-search-mvp/spec.md)
**Input**: Feature specification from `/specs/001-naver-search-mvp/spec.md`

> Output rule: Write the completed plan in Korean unless the user explicitly
> requests another language.

## Summary

본 기능은 분리된 운영 시스템 안에서 본스탬프 앱용 조회/기록 API와 운영 관리자용
서버 렌더링 화면을 함께 제공한다. 단일 FastAPI 웹 서비스 안에 JSON API, Jinja2
관리자 화면, 세션 인증, 감사 로그, CSV 다운로드를 통합하고, Supabase Postgres에
운영 데이터와 감사 데이터를 저장하며, Render 단일 웹 서비스로 배포한다.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.x, Alembic, Jinja2, HTMX, Alpine.js, Pydantic Settings, psycopg, pwdlib, python-multipart  
**Storage**: Supabase Postgres (운영), SQLite (자동 테스트)  
**Testing**: pytest, pytest-asyncio, httpx, pytest-cov  
**Target Platform**: Render Linux 웹 서비스, 데스크톱 중심 관리자 브라우저  
**Project Type**: 서버 렌더링 관리자 화면과 JSON API를 함께 제공하는 단일 웹 서비스  
**Performance Goals**: 조회/기록 API p95 1초 이내, 관리자 목록/필터 화면 2초 이내, 상세 로그 CSV 5천 건 기준 10초 이내 생성  
**Constraints**: Asia/Seoul 시간대 고정, 공유 API Key 인증, 관리자 세션 인증, 단일 웹 서비스 구조 유지, 파일 스토리지 미사용, 운영 실패는 가능한 한 `ok=false`로 단순화  
**Scale/Scope**: 활성 테스터 100~120명, 관리자 소수, 초기 월간 로그 수만 건 수준, 단일 Render 서비스 1개와 단일 Postgres 프로젝트 1개

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Story slices are independently testable and mapped to explicit acceptance scenarios.
  - 충족. `spec.md`의 US1~US3 각각에 독립 테스트 기준과 수용 시나리오가 있다.
- Verification evidence is defined for each story; deterministic or business-critical behavior has automated coverage, or the plan explains why manual proof is the only practical option.
  - 충족. 조회/기록 API, 인증, 할당 저장, 집계, CSV는 자동화 대상이며 배포 후 최종 검증은 수동 시나리오를 병행한다.
- Audit impacts are identified for assignment changes, tester actions, admin mutations, and exported data.
  - 충족. 검색 시도 로그, 내부 경고 로그, 관리자 감사 로그, CSV 다운로드 이벤트를 모두 설계 범위에 포함한다.
- Privacy, access control, and secret-handling implications are documented for all affected roles and data flows.
  - 충족. 앱 공유 API Key, 관리자 세션, 비밀번호 해시, 제한된 PII 저장, CSV 접근 통제를 설계에 반영한다.
- Stateful changes, migrations, or new infrastructure include rollback or recovery steps; added complexity is justified below when needed.
  - 충족. Alembic 마이그레이션 기반 스키마 변경과 Render 재배포/이전 배포 복귀 기준을 정의한다.

## Project Structure

### Documentation (this feature)

```text
specs/001-naver-search-mvp/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── api/
│   ├── dependencies.py
│   └── routes/
│       ├── app_api.py
│       └── health.py
├── admin/
│   ├── auth.py
│   ├── routes/
│   │   ├── accounts.py
│   │   ├── assignments.py
│   │   ├── dashboard.py
│   │   ├── groups.py
│   │   ├── keywords.py
│   │   ├── logs.py
│   │   └── testers.py
│   └── templates/
├── core/
│   ├── config.py
│   ├── logging.py
│   ├── security.py
│   └── time.py
├── db/
│   ├── base.py
│   ├── models.py
│   ├── session.py
│   └── seed.py
├── services/
│   ├── admin_service.py
│   ├── assignment_service.py
│   ├── auth_service.py
│   ├── csv_service.py
│   ├── search_service.py
│   └── stats_service.py
├── static/
│   └── app.css
├── templates/
│   ├── base.html
│   └── admin/
└── main.py

alembic/
├── env.py
└── versions/

scripts/
├── seed_demo.py
└── smoke_test.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: 프런트와 백엔드를 분리하지 않고, 단일 FastAPI 애플리케이션 안에
앱 API와 서버 렌더링 관리자 UI를 함께 둔다. 이는 헌법의 운영 단순성 원칙에 맞고,
Render 단일 웹 서비스 제약 및 MVP 범위에 가장 적합하다.

## Complexity Tracking

해당 없음. 단일 웹 서비스, 단일 데이터베이스, 서버 렌더링 UI, 동기식 요청 처리만
사용한다.
