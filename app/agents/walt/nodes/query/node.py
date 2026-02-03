from langchain.chat_models import init_chat_model
from app.agents.walt.state import State
from app.agents.walt.nodes.query.tools import get_user_info
from app.agents.walt.nodes.query.prompt import SYSTEM_PROMPT
import json

llm = init_chat_model("openai:gpt-4o-mini", temperature=0)

def query_node(state: State):
    new_state = State()
    
    # Check if user_profile is already cached
    user_profile = state.get("user_profile")
    
    if user_profile is None:
        # Fetch user info using the tool
        user_profile = get_user_info.invoke({})
        
        # Cache the user profile in state if successful
        if user_profile and "error" not in user_profile:
            new_state["user_profile"] = user_profile
    
    # Use cached profile or the one we just fetched
    profile_to_use = user_profile if user_profile else state.get("user_profile")
    
    # Format the response
    history = state.get("messages")
    messages = [
        ("system", SYSTEM_PROMPT),
    ] + list(history)
    
    # Add context about user profile if available
    if profile_to_use and "error" not in profile_to_use:
        profile_json = json.dumps(profile_to_use, indent=2)
        profile_context = f"\n\nEmployee Information:\n{profile_json}"
        messages.append(("system", profile_context))
    elif profile_to_use and "error" in profile_to_use:
        error_context = f"\n\nError fetching employee information: {profile_to_use.get('error', 'Unknown error')}"
        messages.append(("system", error_context))
    
    ai_message = llm.invoke(messages)
    new_state["messages"] = [ai_message]
    
    # Preserve user_profile in state
    if profile_to_use:
        new_state["user_profile"] = profile_to_use
    
    return new_state
