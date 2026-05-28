from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck(request: Request, db: Session = Depends(get_db_session)) -> JSONResponse:
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"ok": False, "database": "error", "timezone": request.app.state.settings.timezone},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"ok": True, "database": "ok", "timezone": request.app.state.settings.timezone},
    )
