from fastapi import APIRouter

from app.dtos.navigation import FaqsDTO, FaqsResponseDTO
from app.services.faqs_service2 import FaqsService2

router = APIRouter()

#@router.post("/response")
#async def faqs(body: FaqsDTO):
#    """
#    Returns a response to the user's question based on the contract type.
#    Uses conversational memory and intent classification to provide better responses.
#
#    Args:
#        body: FaqsDTO containing the question, contract type, and user_id.
#
#    Returns:
#        FaqsResponseDTO containing the question, answer, link, and point of contact.
#    """
#    faqs_service = FaqsService()
#    # Use user_id as conversation_id for memory management
#    response = faqs_service.response_faqs(
#        question=body.question,
#        contract_type=body.contract_type,
#        user_id=body.user_id
#    )
#
#    return FaqsResponseDTO(
#        question=body.question,
#        answer=response.get("answer", ""),
#        link=response.get("link", ""),
#        point_of_contact=response.get("point_of_contact", "")
#    )

@router.post("/interact")
async def interact(body: FaqsDTO):
    """
    Interacts with the user's question based on the contract type.
    """
    faqs_service = FaqsService2()    
    response = faqs_service.ask_faqs_agent(question=body.question, contract_type=body.contract_type, user_id=body.user_id)
    
    # response is a FaqsResponseDTO object, access properties with dot notation
    # response.answer - gets the answer property
    # response.question - gets the question property
    return FaqsResponseDTO(
        question=response.question if hasattr(response, 'question') else body.question,
        answer=response.answer if hasattr(response, 'answer') else str(response),
        link=None,  # or response.link if you uncomment it in the dataclass
        point_of_contact=None  # or response.point_of_contact if you uncomment it in the dataclass
    )