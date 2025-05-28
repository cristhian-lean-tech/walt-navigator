from fastapi import APIRouter

from app.dtos.navigation import FaqsDTO, FaqsResponseDTO
from app.services.faqs_service import FaqsService

router = APIRouter()

@router.post("/response")
async def faqs(body: FaqsDTO):
    faqs_service = FaqsService()
    response = faqs_service.response_faqs(body.question, body.role)

    return FaqsResponseDTO(
        question=body.question,
        answer=response.get("answer"),
        link=response.get("link"),
        point_of_contact=response.get("point_of_contact")
    )