from fastapi import APIRouter, HTTPException
import json
import uuid

from app.dtos.navigation import NavigationDTO, NavigationResponseDTO
from app.services.conversation import ConversationService


router = APIRouter()
    
@router.post("/interaction", response_model=NavigationResponseDTO) 
async def navigation(body: NavigationDTO):
    try:
        conversation_service = ConversationService()
        
        conversation_id = body.conversation_id or str(uuid.uuid4())
        
        response = conversation_service.process_user_input(
            content=body.content,
            user_type=body.user_type,
            user_id=conversation_id,
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
