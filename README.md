# 네이버 검색 운영 MVP

본 저장소는 본스탬프 앱용 네이버 검색 운영 MVP를 위한 FastAPI 기반 단일 웹 서비스다.
앱 조회/기록 API와 관리자용 서버 렌더링 화면을 함께 제공한다.

## 로컬 실행

```bash
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
alembic upgrade head
python scripts/seed_demo.py
uvicorn app.main:app --reload
```

## 테스트

```bash
pytest
```

## 배포

- Build: `pip install -e .`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- 필수 환경 변수: `.env.example` 참고

