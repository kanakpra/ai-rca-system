from fastapi import APIRouter
from pydantic import BaseModel

from app.reasoning.correlation import (
    correlate_incident
)

router = APIRouter()


class LogRequest(BaseModel):
    logs: str


@router.post("/analyze")
async def analyze(request: LogRequest):

    logs = request.logs.split("\n")

    result = await correlate_incident(
        logs
    )

    return result