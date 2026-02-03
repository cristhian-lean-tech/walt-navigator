from pydantic import BaseModel, Field
from typing import Literal
from app.agents.walt.state import State
from langchain.chat_models import init_chat_model
from app.agents.walt.nodes.routes.intent.prompt import SYSTEM_PROMPT

type Intent = Literal["query", "action", "conversation"]

class RouteIntent(BaseModel):
    intent: Intent = Field(description="The intent of the user query")

llm = init_chat_model("openai:gpt-4o-mini", temperature=0)
llm = llm.with_structured_output(RouteIntent)

def intent_route(state: State) -> Intent:
    history = state.get("messages")
    messages = [
        ("system", SYSTEM_PROMPT),
    ] + list(history)
    schema = llm.invoke(messages)
    if schema.intent is None:
        return "conversation"
    return schema.intent
