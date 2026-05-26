from pydantic import BaseModel


class CollectRequest(BaseModel):
    source: str


class CollectResponse(BaseModel):
    success: bool
    message: str
    collected_count: int
