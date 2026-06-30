from langgraph.graph import END, START, StateGraph


from graph_routers import orchestrator, profile_router
from states.graph_states import UserState
from states.profile_states import ProfileDraftEvent, ProfileDraftPayload
from user_profile.profile_parser import profile_parser

graph_builder = StateGraph(UserState)

graph_builder.add_node("orchestrator", orchestrator)
graph_builder.add_node("profile_router", profile_router)
graph_builder.add_node("profile_parser", profile_parser)

# Starting point
graph_builder.add_edge(START, "orchestrator")

# Profile route
graph_builder.add_edge("profile_parser", END)


# Compile graph
graph = graph_builder.compile()


# =============== Example ============================
text = """
I'm 28 years old,
I'm a software engineer,
I have 2 years working in Alberta, 1 year in Toronto, 1 year in Europe
My IELTS is 8.5
"""

payload = ProfileDraftPayload(text=text)
event = ProfileDraftEvent(
    event_type="profile_draft",
    payload=payload,
)

graph.invoke({"event": event})
