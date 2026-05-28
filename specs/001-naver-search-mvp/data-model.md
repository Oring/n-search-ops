# Data Model: 네이버 검색 운영 MVP

## 1. 관리자 계정 (`admin_accounts`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 관리자 식별자 |
| username | 문자열 | Unique, Not Null | 로그인 아이디 |
| password_hash | 문자열 | Not Null | 해시 비밀번호 |
| is_active | 불리언 | Not Null, 기본 `true` | 활성 여부 |
| created_at | 시각 | Not Null | 생성 시각 |
| updated_at | 시각 | Not Null | 수정 시각 |
| last_login_at | 시각 | Nullable | 최근 로그인 시각 |

## 2. 그룹 (`groups`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 그룹 식별자 |
| name | 문자열 | Unique, Not Null | 그룹명 |
| is_active | 불리언 | Not Null, 기본 `true` | 활성 여부 |
| created_at | 시각 | Not Null | 생성 시각 |
| updated_at | 시각 | Not Null | 수정 시각 |

## 3. 키워드 (`keywords`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 키워드 식별자 |
| phrase | 문자열 | Unique, Not Null | 검색어 원문 |
| is_active | 불리언 | Not Null, 기본 `true` | 활성 여부 |
| created_at | 시각 | Not Null | 생성 시각 |
| updated_at | 시각 | Not Null | 수정 시각 |

## 4. 테스터 (`testers`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 테스터 식별자 |
| member_no | 문자열 | Unique, Not Null | 앱 식별용 회원번호 |
| name | 문자열 | Not Null | 이름 |
| phone_last4 | 문자열 | Nullable | 휴대폰 뒷자리 |
| group_id | UUID | FK(groups.id), Nullable | 현재 그룹 |
| is_active | 불리언 | Not Null, 기본 `true` | 활성 여부 |
| created_at | 시각 | Not Null | 생성 시각 |
| updated_at | 시각 | Not Null | 수정 시각 |

### 상태 전이

- 신규 등록 → 활성
- 활성 → 비활성
- 비활성 → 재활성화
- 그룹 변경은 별도 상태 전이 없이 즉시 반영

## 5. 그룹-주차 키워드 할당 (`group_week_keyword_assignments`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 할당 행 식별자 |
| group_id | UUID | FK(groups.id), Not Null | 대상 그룹 |
| week_start | 날짜 | Not Null | 주차 시작일(월요일) |
| keyword_id | UUID | FK(keywords.id), Not Null | 할당된 키워드 |
| created_at | 시각 | Not Null | 생성 시각 |
| created_by_admin_id | UUID | FK(admin_accounts.id), Nullable | 저장한 관리자 |

### 제약

- `(group_id, week_start, keyword_id)` 유니크
- 저장 시 동일 `(group_id, week_start)` 범위 기존 행 전부 삭제 후 새 행 삽입
- 비활성 키워드는 신규 저장 대상에서 제외

## 6. 운영 설정 (`app_settings`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| key | 문자열 | PK | 설정 키 |
| value | 문자열 | Not Null | 직렬화된 설정값 |
| updated_at | 시각 | Not Null | 수정 시각 |
| updated_by_admin_id | UUID | FK(admin_accounts.id), Nullable | 마지막 수정 관리자 |

### 초기 키

- `monthly_limit`: 기본값 `2`

## 7. 검색 시도 로그 (`search_attempt_logs`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 이벤트 식별자 |
| tester_id | UUID | FK(testers.id), Not Null | 테스터 참조 |
| group_id | UUID | FK(groups.id), Nullable | 당시 그룹 참조 |
| keyword_id | UUID | FK(keywords.id), Not Null | 키워드 참조 |
| attempted_at | 시각 | Not Null | 시도 시각 |
| member_no_snapshot | 문자열 | Not Null | 당시 회원번호 |
| tester_name_snapshot | 문자열 | Not Null | 당시 이름 |
| group_name_snapshot | 문자열 | Nullable | 당시 그룹명 |
| keyword_snapshot | 문자열 | Not Null | 당시 키워드명 |
| source | 문자열 | Not Null | 이벤트 소스(`app`) |

### 도메인 규칙

- 동일 회원의 같은 날 중복 로그 허용
- 조회 제한 계산은 이 로그의 성공 저장 건수로 수행
- 월간 집계와 대시보드 요약의 원본 데이터

## 8. 내부 경고 로그 (`warning_logs`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 경고 식별자 |
| event_type | 문자열 | Not Null | `unregistered_member`, `inactive_tester`, `invalid_api_key`, `invalid_keyword` 등 |
| member_no | 문자열 | Nullable | 관련 회원번호 |
| request_path | 문자열 | Nullable | 요청 경로 |
| detail_json | JSONB | Not Null | 추가 정보 |
| occurred_at | 시각 | Not Null | 발생 시각 |

## 9. 관리자 감사 로그 (`admin_audit_logs`)

| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 감사 이벤트 식별자 |
| admin_id | UUID | FK(admin_accounts.id), Nullable | 작업 관리자 |
| event_type | 문자열 | Not Null | 예: `tester_created`, `assignment_saved`, `csv_exported` |
| entity_type | 문자열 | Not Null | 영향 엔터티 유형 |
| entity_id | 문자열 | Nullable | 영향 엔터티 식별자 |
| detail_json | JSONB | Not Null | 변경 상세 |
| occurred_at | 시각 | Not Null | 발생 시각 |

## 관계 요약

- 그룹 1 : N 테스터
- 그룹 N : N 키워드 (`group_week_keyword_assignments`를 통한 주차별 관계)
- 관리자 계정 1 : N 관리자 감사 로그
- 테스터 1 : N 검색 시도 로그
- 키워드 1 : N 검색 시도 로그

## 조회/기록 규칙 파생 값

- `today_start`, `tomorrow_start`: Asia/Seoul 기준 당일 경계
- `month_start`, `next_month_start`: Asia/Seoul 기준 월간 경계
- `current_week_start`: Asia/Seoul 기준 월요일 날짜
