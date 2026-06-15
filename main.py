from langgraph.graph import END, START, StateGraph


from states.graph_states import UserState
from states.profile_states import ProfileDraftEvent, ProfileDraftPayload
from user_profile.profile_parser import profile_parser

graph_builder = StateGraph(UserState)

graph_builder.add_node("profile_parser", profile_parser)

graph_builder.add_edge(START, "profile_parser")
graph_builder.add_edge("profile_parser", END)

graph = graph_builder.compile()

text = """
I'm 25 years old and I'm a software engineer,
I have 3 years working experience,
My IELTS is 8.0.
"""
payload = ProfileDraftPayload(text=text)
event = ProfileDraftEvent(
    event_type="profile_draft",
    payload=payload,
)

graph.invoke({"event": event})
