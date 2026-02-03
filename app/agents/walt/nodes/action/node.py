from langchain.agents import create_agent
from app.agents.walt.nodes.action.tools import tools
from app.agents.walt.nodes.action.prompt import prompt_template

action_node = create_agent(
    model="openai:gpt-4o-mini",
    tools=tools,
    system_prompt=prompt_template,
)
