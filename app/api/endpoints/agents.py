from fastapi import APIRouter

from app.dtos.agents import BenefitsDTO, BenefitsResponseDTO
from app.agents.walt.agent import graph
from langchain_core.messages import HumanMessage

router = APIRouter()

@router.post("/agents/benefits")
async def benefits(body: BenefitsDTO):
    """
    Interacts with the user's question based on the contract type.
    """
    human_message = HumanMessage(content=body.message)
    response = graph.invoke({"messages": [human_message]})
    last_message = list(response.get("messages"))[-1]
    if last_message:
        return BenefitsResponseDTO(response=last_message.text)
    else:
        return BenefitsResponseDTO(response="No response from the agent")
