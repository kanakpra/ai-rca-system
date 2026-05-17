from pydantic import BaseModel


class LogRequest(BaseModel):
    logs: str