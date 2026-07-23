from langgraph.graph import END, START, StateGraph


from graph.nodes import make_profile_parser
from graph.routers import orchestrator, profile_router
from graph.state.shared import MainState
from user_profile.service import ProfileService

graph_builder = StateGraph(MainState)

# Dependencies initialization
profile_service = ProfileService()

# ========== NODES ==============
graph_builder.add_node("orchestrator", orchestrator)

# Profile related nodes
graph_builder.add_node("profile_router", profile_router)
graph_builder.add_node("profile_parser", make_profile_parser(profile_service))

# ========== EDGES ==============
graph_builder.add_edge(START, "orchestrator")
graph_builder.add_edge("profile_parser", END)

# ========== COMPILE GRAPH ==============
compiled_graph = graph_builder.compile()
