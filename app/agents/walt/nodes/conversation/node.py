from langchain.chat_models import init_chat_model
from app.agents.walt.state import State
from app.agents.walt.nodes.conversation.prompt import SYSTEM_PROMPT

llm = init_chat_model("openai:gpt-4o-mini", temperature=0)

def conversation_node(state: State):
    new_state = State()
    history = state.get("messages")
    messages = [
        ("system", SYSTEM_PROMPT),
    ] + list(history)
    ai_message = llm.invoke(messages)
    new_state["messages"] = [ai_message]
    return new_state
