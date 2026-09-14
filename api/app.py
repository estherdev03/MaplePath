from fastapi import FastAPI

from graph.state.profile import (
    ProfileConfirmEvent,
    ProfileConfirmFormPayload,
    ProfileDraftEvent,
    ProfileDraftPayload,
)
from graph.construct import compiled_graph
from noc.evaluate import noc_retrieval_method_evaluate

app = FastAPI()


@app.post("/profile/parse")
def parse_profile(profile_text: str):
    payload = ProfileDraftPayload(text=profile_text)
    event = ProfileDraftEvent(event_type="profile_draft", payload=payload)
    result = compiled_graph.invoke({"event": event})
    return {"result": result["profile"]}


@app.post("/profile/complete")
def complete_profile(profile_confirm: ProfileConfirmFormPayload):
    event = ProfileConfirmEvent(event_type="profile_confirm", payload=profile_confirm)
    result = compiled_graph.invoke({"event": event})
    return {"result": result["profile"]}


@app.get("/evaluate")
def NOC_retrieval_evaluate():
    examples_report, mean_report = noc_retrieval_method_evaluate(
        "data/noc_eval_labels.csv"
    )
    return {"examples_report": examples_report.report, "mean_report": mean_report}
