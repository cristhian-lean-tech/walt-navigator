from fastapi import APIRouter, HTTPException
import json

from app.models.embedding import Embedding
from app.dtos.navigation import NavigationDTO, ConversationResponseDTO
from app.services.navigation import NavigationService


router = APIRouter()

@router.post("/navigation", response_model=ConversationResponseDTO) 
async def navigation(embedding: NavigationDTO):
    try:
        navigation_service = NavigationService()
        result = navigation_service.suggest_routes(
            content=embedding.content,
            role=embedding.role,
        )

        print("*** 7", result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
