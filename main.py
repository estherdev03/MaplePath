from graph.state.profile import ProfileDraftEvent, ProfileDraftPayload
from graph.construct import compiled_graph

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

compiled_graph.invoke({"event": event})
