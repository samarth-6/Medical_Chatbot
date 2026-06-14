from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    mode: str
    session_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]  