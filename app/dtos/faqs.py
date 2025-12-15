from pydantic import BaseModel, Field
from typing import Optional

class IntentClassifierOutput(BaseModel):
   intent: str
   confidence: float = Field(default=0.5, ge=0.0, le=1.0)
   needs_clarification: bool
   clarifying_question: Optional[str] = None
   short_reason: str = Field(default="Intent classified", max_length=120)

class SessionState(BaseModel):
   last_intent: Optional[str] = None
   pending_clarification: bool = False
   last_bot_question: str | None = None
   last_in_scope_topic: str | None = None

class FaqsDTO(BaseModel):
    question: str
    contract_type: str
    user_id: str

class FaqsResponseDTO(BaseModel):
    question: str
    answer: str
    link: Optional[str] = None
    point_of_contact: Optional[str] = None