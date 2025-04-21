from typing import Dict, Optional, Any
from datetime import datetime

class ConversationState:
    def __init__(self):
        self.benefit: Optional[str] = None
        self.parameters: Dict[str, Any] = {}
        self.current_parameter: Optional[str] = None
        self.created_at: datetime = datetime.now()
        self.last_updated: datetime = datetime.now()

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, ConversationState] = {}

    def get_or_create_conversation(self, conversation_id: str) -> ConversationState:
        if not self.conversations[conversation_id]:
            self.conversations[conversation_id] = ConversationState()
        
        return self.conversations[conversation_id]

    def update_conversation(self, conversation_id: str, benefit: Optional[str] = None, 
                          parameter: Optional[str] = None, value: Any = None) -> None:
        state = self.get_or_create_conversation(conversation_id)
        
        if benefit:
            state.benefit = benefit
            state.parameters = {}
            state.current_parameter = None
        
        if parameter and value:
            state.parameters[parameter] = value
            state.current_parameter = None
        
        if parameter and not value:
            state.current_parameter = parameter
        
        state.last_updated = datetime.now()

    def get_next_parameter(self, conversation_id: str) -> Optional[str]:
        state = self.get_or_create_conversation(conversation_id)
        if not state.benefit:
            return None

        # Obtener los parámetros requeridos para el beneficio
        from app.shared.forms import FORMS
        required_parameters = list(FORMS.get(state.benefit, {}).keys())
        
        # Encontrar el primer parámetro que no ha sido completado
        for param in required_parameters:
            if param not in state.parameters:
                return param
        
        return None

    def is_conversation_complete(self, conversation_id: str) -> bool:
        state = self.get_or_create_conversation(conversation_id)
        if not state.benefit:
            return False

        from app.shared.forms import FORMS
        required_parameters = list(FORMS.get(state.benefit, {}).keys())
        return all(param in state.parameters for param in required_parameters)

    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        state = self.get_or_create_conversation(conversation_id)
        return {
            "benefit": state.benefit,
            "parameters": state.parameters,
            "current_parameter": state.current_parameter,
            "is_complete": self.is_conversation_complete(conversation_id)
        }

    def clear_conversation(self, conversation_id: str) -> None:
        if conversation_id in self.conversations:
            del self.conversations[conversation_id] 