from langgraph.graph import StateGraph, START, END
from app.agents.walt.state import State
from app.agents.walt.nodes.query.node import query_node
from app.agents.walt.nodes.action.node import action_node
from app.agents.walt.nodes.conversation.node import conversation_node
from app.agents.walt.nodes.routes.intent.route import intent_route

builder = StateGraph(State)

builder.add_node('query', query_node)
builder.add_node('action', action_node)
builder.add_node('conversation', conversation_node)

builder.add_conditional_edges(START, intent_route)
builder.add_edge('query', END)
builder.add_edge('action', END)
builder.add_edge('conversation', END)

graph = builder.compile()
