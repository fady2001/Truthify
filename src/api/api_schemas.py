from typing import Dict, List

from pydantic import BaseModel


class TextInput(BaseModel):
    text: str


class ClaimResult(BaseModel):
    claim: str
    status: str
    explanation: str
    sources: List[Dict[str, str]]


class FactCheckResponse(BaseModel):
    input_text: str
    extracted_claims: List[str]
    fact_check_results: List[ClaimResult]
    processing_time: float
