from fastapi import APIRouter, HTTPException
import json
import uuid

from app.models.embedding import Embedding
from app.dtos.navigation import NavigationDTO, ConversationResponseDTO
from app.services.navigation import NavigationService


router = APIRouter()

@router.post("/navigation", response_model=ConversationResponseDTO) 
async def navigation(message: NavigationDTO):
    try:
        navigation_service = NavigationService()
        
        # Generar un nuevo ID de conversación si no se proporciona uno
        conversation_id = message.conversation_id or str(uuid.uuid4())
        
        result = navigation_service.suggest_routes(
            content=message.content,
            role=message.role,
            conversation_id=conversation_id
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
