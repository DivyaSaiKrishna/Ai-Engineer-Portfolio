from typing import Literal

from pydantic import BaseModel, Field


class ResearchAnswer(BaseModel):
    answer: str = Field(min_length=1)
    confidence: Literal["low", "medium", "high"]
    assumptions: list[str]
    needs_external_data: bool