from langgraph.graph import MessagesState
from typing import Optional

class State(MessagesState):
    user_profile: Optional[dict]
