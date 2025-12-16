from app.dtos.faqs import FaqsResponseDTO

def from_string_to_faqs_response_dto(response: str, question: str) -> FaqsResponseDTO:
   return FaqsResponseDTO(
       question=question,
       answer=response,
       link=None,
       point_of_contact=None
   )

def from_dict_to_faqs_response_dto(response: dict) -> FaqsResponseDTO:
   return FaqsResponseDTO(
       question=response.get("question", ""),
       answer=response.get("answer", ""),
       link=response.get("link", ""),
       point_of_contact=response.get("point_of_contact", "")
   )
   