from pydantic import BaseModel

class BenefitsDTO(BaseModel):
    user_id: str
    message: str

class BenefitsResponseDTO(BaseModel):
    response: str