# Tasks: 네이버 검색 운영 MVP

**Input**: Design documents from `/specs/001-naver-search-mvp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml
**Output Rule**: Write the completed task list in Korean unless the user explicitly requests another language.

**Verification**: 조회/기록 API, 관리자 인증, 할당 저장, 로그 필터, CSV 다운로드는 자동 테스트를 우선한다. 배포 후 최종 확인은 quickstart.md의 수동 시나리오를 따른다.

**Organization**: 작업은 사용자 스토리별 독립 구현과 검증이 가능하도록 구성한다.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 골격, 의존성, 로컬 실행 기반 준비

- [X] T001 Python 프로젝트 메타데이터와 의존성 선언을 `pyproject.toml`, `.python-version`, `.env.example`에 작성한다
- [X] T002 애플리케이션/테스트 디렉터리 골격과 패키지 초기화 파일을 `app/`, `tests/`, `scripts/`, `alembic/versions/` 아래에 생성한다
- [X] T003 [P] 기본 설정, 환경 변수 로더, 로깅 구성을 `app/core/config.py`, `app/core/logging.py`에 구현한다
- [X] T004 [P] 테스트 공용 픽스처와 앱 부트스트랩을 `tests/conftest.py`에 구성한다

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 사용자 스토리의 선행 인프라 구축

- [X] T005 SQLAlchemy 베이스, 세션, 엔진 초기화를 `app/db/base.py`, `app/db/session.py`에 구현한다
- [X] T006 Alembic 설정과 초기 마이그레이션 환경을 `alembic.ini`, `alembic/env.py`, `alembic/versions/`에 구성한다
- [X] T007 핵심 엔터티 모델을 `app/db/models.py`에 구현한다
- [X] T008 [P] 비밀번호 해시, 관리자 세션, 앱 API Key 검증 유틸을 `app/core/security.py`, `app/admin/auth.py`에 구현한다
- [X] T009 [P] Asia/Seoul 시간 계산과 감사 로그 공용 헬퍼를 `app/core/time.py`, `app/services/admin_service.py`에 구현한다
- [X] T010 기본 레이아웃과 공통 정적 자산을 `app/templates/base.html`, `app/templates/admin/layout.html`, `app/static/app.css`에 작성한다

**Checkpoint**: 모든 기능 구현 전에 데이터 모델, 인증, 공통 레이아웃이 준비되어야 한다.

---

## Phase 3: User Story 1 - 앱 검색 대상 조회 및 시도 기록 (Priority: P1) 🎯 MVP

**Goal**: 앱이 회원번호와 API Key로 오늘의 키워드를 조회하고 검색 시도를 안정적으로 기록한다

**Independent Test**: 활성 테스터와 할당 데이터를 시드한 뒤 조회 API, 기록 API, 중복/실패 케이스를 자동 테스트로 검증한다

### Verification for User Story 1

- [X] T011 [P] [US1] 앱 API 계약 테스트를 `tests/contract/test_app_api.py`에 작성한다
- [X] T012 [P] [US1] 하루/월간 제한, 랜덤 키워드, 잘못된 키워드 경고 로그 통합 테스트를 `tests/integration/test_search_service.py`에 작성한다

### Implementation for User Story 1

- [X] T013 [P] [US1] 조회/기록 도메인 서비스를 `app/services/search_service.py`, `app/services/assignment_service.py`에 구현한다
- [X] T014 [US1] 앱 API 인증/DB 의존성을 `app/api/dependencies.py`에 구현한다
- [X] T015 [US1] 조회 API와 기록 API 라우트를 `app/api/routes/app_api.py`에 구현한다
- [X] T016 [US1] 헬스체크 라우트를 `app/api/routes/health.py`에 구현한다
- [X] T017 [US1] FastAPI 앱 팩토리와 라우터 연결을 `app/main.py`에 구현한다

**Checkpoint**: 앱 조회/기록 API와 헬스체크가 독립적으로 동작해야 한다.

---

## Phase 4: User Story 2 - 운영자 데이터 관리 및 관리자 인증 (Priority: P2)

**Goal**: 운영자가 로그인 후 테스터, 그룹, 키워드, 주차 할당, 관리자 계정, 월간 제한을 관리한다

**Independent Test**: 자동 테스트로 로그인, 테스터 재활성화, 할당 덮어쓰기, 비밀번호 변경을 검증한다

### Verification for User Story 2

- [X] T018 [P] [US2] 관리자 로그인, 테스터 재활성화, 할당 덮어쓰기 통합 테스트를 `tests/integration/test_admin_management.py`에 작성한다

### Implementation for User Story 2

- [X] T019 [P] [US2] 관리자 인증 서비스와 로그인/로그아웃 흐름을 `app/services/auth_service.py`, `app/admin/routes/auth.py`에 구현한다
- [X] T020 [P] [US2] 테스터/그룹/키워드/관리자 계정/설정 관리 라우트를 `app/admin/routes/testers.py`, `app/admin/routes/groups.py`, `app/admin/routes/keywords.py`, `app/admin/routes/accounts.py`에 구현한다
- [X] T021 [US2] 주차별 할당 저장 라우트와 화면 로직을 `app/admin/routes/assignments.py`, `app/services/assignment_service.py`에 구현한다
- [X] T022 [P] [US2] 관리자 로그인 및 관리 화면 템플릿을 `app/templates/admin/login.html`, `app/templates/admin/testers.html`, `app/templates/admin/groups.html`, `app/templates/admin/keywords.html`, `app/templates/admin/assignments.html`, `app/templates/admin/accounts.html`에 작성한다
- [X] T023 [US2] 관리자 변경 이력 감사 로그를 관련 서비스와 라우트에 연결한다

**Checkpoint**: 관리자 로그인 및 운영 데이터 관리가 브라우저에서 동작해야 한다.

---

## Phase 5: User Story 3 - 운영 현황 조회, 상세 로그 필터링, CSV 다운로드 (Priority: P3)

**Goal**: 운영자가 요약 통계와 상세 로그를 조회하고 CSV를 다운로드한다

**Independent Test**: 자동 테스트로 요약 집계, 로그 필터, CSV 결과 일치를 검증한다

### Verification for User Story 3

- [X] T024 [P] [US3] 대시보드 집계와 CSV 다운로드 통합 테스트를 `tests/integration/test_reporting.py`에 작성한다

### Implementation for User Story 3

- [X] T025 [P] [US3] 통계/CSV 서비스를 `app/services/stats_service.py`, `app/services/csv_service.py`에 구현한다
- [X] T026 [US3] 대시보드와 상세 로그/CSV 라우트를 `app/admin/routes/dashboard.py`, `app/admin/routes/logs.py`에 구현한다
- [X] T027 [P] [US3] 대시보드와 로그 화면 템플릿을 `app/templates/admin/dashboard.html`, `app/templates/admin/logs.html`에 작성한다
- [X] T028 [US3] HTMX/Alpine 기반 필터 유지와 CSV 감사 로그를 `app/templates/admin/logs.html`, `app/admin/routes/logs.py`에 구현한다

**Checkpoint**: 운영 요약과 상세 로그 조회 및 CSV 다운로드가 동작해야 한다.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 시드, 배포, 문서화, 최종 검증

- [X] T029 [P] 데모 시드와 초기 관리자/테스터 적재 스크립트를 `app/db/seed.py`, `scripts/seed_demo.py`에 구현한다
- [X] T030 [P] Render 배포 설정과 실행 명령을 `render.yaml`, `README.md`에 문서화한다
- [X] T031 [P] 스모크 테스트와 수동 검증 스크립트를 `scripts/smoke_test.py`, `specs/001-naver-search-mvp/quickstart.md`에 정리한다
- [X] T032 전체 자동 테스트를 실행하고 결과를 반영한다
- [ ] T033 배포 후 운영 검증 결과를 문서와 최종 보고에 반영한다

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: 즉시 시작 가능
- **Phase 2**: Phase 1 완료 후 시작, 모든 사용자 스토리를 차단
- **Phase 3~5**: Phase 2 완료 후 우선순위 순으로 진행
- **Phase 6**: 핵심 사용자 스토리 구현 후 진행

### User Story Dependencies

- **US1 (P1)**: Foundation 이후 바로 시작 가능, 다른 스토리에 의존하지 않음
- **US2 (P2)**: Foundation 이후 시작 가능, US1과 데이터 모델은 공유하지만 독립 검증 가능
- **US3 (P3)**: US1 로그 데이터와 US2 관리자 인증을 활용하지만 스토리 자체 검증은 독립 가능

### Within Each User Story

- 테스트를 먼저 작성한다
- 모델/기반 서비스 다음에 라우트를 구현한다
- 라우트 다음에 템플릿과 감사 로깅을 마무리한다

### Parallel Opportunities

- `T003`, `T004`, `T008`, `T009`
- `T011`, `T012`, `T013`
- `T019`, `T020`, `T022`
- `T024`, `T025`, `T027`
- `T029`, `T030`, `T031`

---

## Parallel Example: User Story 1

```bash
Task: "앱 API 계약 테스트를 tests/contract/test_app_api.py에 작성한다"
Task: "하루/월간 제한, 랜덤 키워드, 잘못된 키워드 경고 로그 통합 테스트를 tests/integration/test_search_service.py에 작성한다"
Task: "조회/기록 도메인 서비스를 app/services/search_service.py, app/services/assignment_service.py에 구현한다"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup과 Foundational 완료
2. US1 테스트 작성
3. US1 API 구현
4. 헬스체크와 앱 API를 먼저 검증

### Incremental Delivery

1. US1 완성 후 앱 핵심 플로우 배포 가능 상태 확보
2. US2 추가로 운영 관리 기능 확보
3. US3 추가로 통계/로그/CSV 확보
4. 마지막으로 시드/배포/스모크 검증 정리

## Notes

- 모든 업무상 실패는 외부에 단순 `ok=false`로 유지한다
- 관리자 화면은 데스크톱 효율 우선으로 구성한다
- 스키마 변경은 반드시 Alembic과 Supabase 마이그레이션으로 추적한다
