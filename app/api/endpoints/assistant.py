from fastapi import APIRouter, HTTPException
import json
import uuid

from app.models.embedding import Embedding
from app.dtos.navigation import NavigationDTO, ConversationResponseDTO, NavigationResponseDTO
from app.services.navigation import NavigationService
from app.services.conversation import ConversationService


router = APIRouter()

@router.post("/navigation", response_model=ConversationResponseDTO) 
async def navigation(message: NavigationDTO):
    try:
        navigation_service = NavigationService()
        
        conversation_id = message.conversation_id or str(uuid.uuid4())
        
        result = navigation_service.suggest_routes(
            content=message.content,
            role=message.role,
            conversation_id=conversation_id
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/interaction", response_model=NavigationResponseDTO) 
async def navigation(message: NavigationDTO):
    try:
        conversation_service = ConversationService()
        
        conversation_id = message.conversation_id or str(uuid.uuid4())
        
        response = conversation_service.process_user_input(
            content=message.content,
            user_id=conversation_id,
        )


        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
