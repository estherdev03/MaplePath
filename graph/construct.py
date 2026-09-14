import os

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph


from crs.english import EnglishService
from crs.french import FrenchService
from crs.service import CRSService
from crs.transferability import TransferabilityService
from db.service import DatabaseService
from eligibility.service import EligibilityService
from graph.nodes import (
    calculate_crs_wrapper,
    create_advice_wrapper,
    evaluate_eligibility_wrapper,
    parse_profile_wrapper,
    create_profile_wrapper,
)
from graph.routers import orchestrator, profile_router
from graph.state.shared import MainState
from noc.repository import NOCRepository
from noc.service import NOCService
from user_profile.service import ProfileService

load_dotenv()

graph_builder = StateGraph(MainState)

# Dependencies initialization
english_service = EnglishService()
french_service = FrenchService()
transferability_service = TransferabilityService(
    english_service=english_service, french_service=french_service
)
crs_service = CRSService(
    english_service=english_service,
    french_service=french_service,
    transferability_service=transferability_service,
)
db_service = DatabaseService(os.getenv("DB_URL"))
noc_repository = NOCRepository(db_service=db_service)
noc_service = NOCService(noc_repository=noc_repository)
eligibility_service = EligibilityService()
profile_service = ProfileService(
    crs_service=crs_service,
    noc_service=noc_service,
    eligibility_service=eligibility_service,
)

# ========== NODES ==============
graph_builder.add_node("orchestrator", orchestrator)

# Profile related nodes
graph_builder.add_node("profile_router", profile_router)
graph_builder.add_node("parse_profile", parse_profile_wrapper(profile_service))
graph_builder.add_node("create_profile", create_profile_wrapper(profile_service))
graph_builder.add_node("calculate_crs", calculate_crs_wrapper(profile_service))
graph_builder.add_node(
    "evaluate_express_entry", evaluate_eligibility_wrapper(profile_service)
)
graph_builder.add_node("create_advice", create_advice_wrapper(profile_service))


# ========== EDGES ==============

graph_builder.add_edge(START, "orchestrator")
graph_builder.add_edge("parse_profile", END)
graph_builder.add_edge("create_profile", "calculate_crs")
graph_builder.add_edge("calculate_crs", "evaluate_express_entry")
graph_builder.add_edge("evaluate_express_entry", "create_advice")
graph_builder.add_edge("create_advice", END)

# ========== COMPILE GRAPH ==============
compiled_graph = graph_builder.compile()
