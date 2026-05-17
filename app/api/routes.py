from fastapi import APIRouter

from app.models.request_models import LogRequest

from app.reasoning.parser import (
    extract_important_logs,
    parse_log_events
)

from app.reasoning.correlation import (
    correlate_incident
)

from app.ai.llm import call_ai


router = APIRouter()


@router.post("/analyze")
def analyze(request: LogRequest):

    logs = request.logs

    important_logs = extract_important_logs(logs)

    events = parse_log_events(important_logs)

    reasoning_result = correlate_incident(events)

    ai_output = call_ai("\n".join(important_logs))

    return {
        "reasoning_result": reasoning_result,
        "ai_output": ai_output
    }