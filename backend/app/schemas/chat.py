from pydantic import BaseModel
from typing import Dict, List, Optional

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    emotion: str
    history: List[Dict[str, str]]
    error: Optional[str] = None