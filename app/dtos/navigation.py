from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class NavigationDTO:
    content: str
    role: str
    conversation_id: Optional[str] = None

@dataclass
class NavigationResponseDTO:
    response: str
    request_type: str
    paths: Optional[List[str]] = None

@dataclass
class ConversationResponseDTO:
    message: str
    conversation_id: Optional[str] = None
    current_parameter: Optional[str] = None
    benefit: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    is_complete: Optional[bool] = False