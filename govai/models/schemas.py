from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    language: str = Field(default="en", pattern=r"^[a-zA-Z]{2,3}(-[a-zA-Z]{2,4})?$")


class Source(BaseModel):
    title: str
    url: str


class StructuredAnswer(BaseModel):
    summary: str
    eligibility: Optional[str] = None
    steps: list[str] = []
    notes: Optional[str] = None
    sources: list[Source] = []


class GuidanceStep(BaseModel):
    step_number: int
    question: str
    options: list[str] = []


class ChatResponse(BaseModel):
    answer: StructuredAnswer
    session_id: str
    is_guidance_mode: bool = False
    guidance_step: Optional[GuidanceStep] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
