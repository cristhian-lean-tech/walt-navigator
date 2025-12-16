from fastapi import APIRouter

from app.dtos.faqs import FaqsDTO, FaqsResponseDTO
from app.services.faqs_service2 import FaqsService2

router = APIRouter()

@router.post("/interact")
async def interact(body: FaqsDTO):
    """
    Interacts with the user's question based on the contract type.
    """
    faqs_service = FaqsService2()    
    response = faqs_service.ask_faqs_agent(question=body.question, contract_type=body.contract_type, user_id=body.user_id)
    return response