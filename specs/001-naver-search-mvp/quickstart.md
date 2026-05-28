# Quickstart: 네이버 검색 운영 MVP

## 1. 로컬 준비

1. Python 3.12 환경을 준비한다.
2. `.env`에 아래 값을 설정한다.

```env
APP_ENV=local
APP_NAME=naver-search-ops
SECRET_KEY=change-me
ADMIN_SESSION_COOKIE=naver_search_admin
API_SHARED_KEY=change-me
DATABASE_URL=sqlite:///./local.db
TIMEZONE=Asia/Seoul
MONTHLY_LIMIT_DEFAULT=2
```

## 2. 의존성 설치 및 DB 준비

```bash
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
alembic upgrade head
python scripts/seed_demo.py
```

## 3. 로컬 실행

```bash
uvicorn app.main:app --reload
```

- 관리자 로그인: `http://127.0.0.1:8000/admin/login`
- 앱 API 헬스체크: `http://127.0.0.1:8000/health`

## 4. 자동 테스트

```bash
pytest
```

## 5. 수동 핵심 검증

### 앱 API

1. 유효한 `X-API-Key`와 활성 테스터 회원번호로 `/api/v1/search-target` 호출
2. `ok=true`, `keyword`, `keyword_id` 수신 확인
3. 받은 `keyword_id`로 `/api/v1/search-attempts` 호출
4. `ok=true` 확인 후 같은 날 다시 조회하면 `ok=false` 확인

### 관리자 화면

1. 시드 관리자 계정으로 로그인
2. 그룹 생성, 키워드 생성, 테스터 등록/재활성화
3. 특정 그룹/주차에 다중 키워드 할당 저장
4. 월간 제한값 변경
5. 로그 화면 필터 적용 후 CSV 다운로드

## 6. 배포 절차

1. Supabase 프로젝트에 마이그레이션 적용
2. Render 서비스 환경 변수 설정
3. Render 배포 실행
4. 배포 URL 기준 `/health`, 앱 API, 관리자 로그인, CSV 다운로드 검증
