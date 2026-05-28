from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import authorize_api_key, get_db_session
from app.schemas.api import BasicResponse, SearchAttemptRequest, SearchTargetResponse
from app.services.search_service import get_search_target, record_search_attempt

router = APIRouter(tags=["app-api"])


@router.get("/search-target", response_model=SearchTargetResponse)
def search_target(
    request: Request,
    member_no: str,
    db: Session = Depends(get_db_session),
) -> SearchTargetResponse:
    authorize_api_key(request, db, member_no)
    result = get_search_target(db, request.app.state.settings, member_no, request.url.path)
    return SearchTargetResponse(ok=result.ok, keyword=result.keyword, keyword_id=result.keyword_id)


@router.post("/search-attempts", response_model=BasicResponse)
def create_search_attempt(
    payload: SearchAttemptRequest,
    request: Request,
    db: Session = Depends(get_db_session),
) -> BasicResponse:
    authorize_api_key(request, db, payload.member_no)
    ok = record_search_attempt(
        db,
        request.app.state.settings,
        member_no=payload.member_no,
        keyword_id=payload.keyword_id,
        request_path=request.url.path,
    )
    return BasicResponse(ok=ok)
