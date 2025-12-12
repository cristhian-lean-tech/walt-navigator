from pydantic import BaseModel, Field
from typing import Optional
from app.shared.const import IntentType

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