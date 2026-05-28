from pydantic import BaseModel


class BasicResponse(BaseModel):
    ok: bool


class SearchTargetResponse(BasicResponse):
    keyword: str | None = None
    keyword_id: str | None = None


class SearchAttemptRequest(BaseModel):
    member_no: str
    keyword_id: str
