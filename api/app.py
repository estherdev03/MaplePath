import logging
import os
import secrets

from cohere.errors import TooManyRequestsError
from fastapi import Depends, FastAPI, Header, HTTPException

from logging_config import configure_logging
from graph.state.profile import (
    MaritalStatus,
    ProfileConfirmEvent,
    ProfileConfirmFormPayload,
    ProfileDraftEvent,
    ProfileDraftPayload,
)
from graph.state.shared import UserProfile
from graph.construct import compiled_graph, crs_service, eligibility_service
from noc.evaluate import noc_retrieval_method_evaluate

configure_logging()
logger = logging.getLogger(__name__)


def require_api_key(x_api_key: str | None = Header(default=None)):
    """Reject requests without the shared key, if API_KEY is set."""
    expected = os.getenv("API_KEY")
    if not expected:
        return
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        logger.warning("Rejected request with missing or invalid API key")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


app = FastAPI(dependencies=[Depends(require_api_key)])


@app.post("/profile/parse")
def parse_profile(profile_text: str):
    logger.info("Received profile parse request")
    payload = ProfileDraftPayload(text=profile_text)
    event = ProfileDraftEvent(event_type="profile_draft", payload=payload)
    try:
        result = compiled_graph.invoke({"event": event})
    except ValueError as e:
        logger.warning("Profile parse rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to parse profile")
        raise HTTPException(
            status_code=500, detail="Failed to parse profile"
        ) from e
    logger.info("Profile parse request completed")
    return {"result": result["profile"]}


@app.post("/profile/complete")
def complete_profile(profile_confirm: ProfileConfirmFormPayload):
    logger.info("Received profile complete request")
    event = ProfileConfirmEvent(event_type="profile_confirm", payload=profile_confirm)
    try:
        result = compiled_graph.invoke({"event": event})
    except ValueError as e:
        logger.warning("Profile complete rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except TooManyRequestsError as e:
        logger.warning("Profile complete rate-limited by Cohere: %s", e)
        raise HTTPException(
            status_code=429,
            detail="The occupation classifier's search service is rate-limited right now. Please try again in about a minute.",
        ) from e
    except Exception as e:
        logger.exception("Failed to complete profile")
        raise HTTPException(
            status_code=500, detail="Failed to complete profile"
        ) from e
    logger.info("Profile complete request completed")
    return {"result": result["profile"]}


# UserProfile is also partial graph state, so every field is optional on
# the model; scoring needs these filled in.
CRS_REQUIRED_FIELDS = (
    "age",
    "occupation",
    "languages",
    "work_experience",
    "marital_status",
    "education",
    "canada_education",
)


def missing_crs_fields(profile: UserProfile) -> list[str]:
    missing = [f for f in CRS_REQUIRED_FIELDS if getattr(profile, f) is None]
    if profile.marital_status == MaritalStatus.MARRIED and profile.spouse is None:
        missing.append("spouse")
    return missing


@app.post("/crs/simulate")
def simulate_crs(profile: UserProfile):
    logger.info("Received CRS simulate request")
    missing = missing_crs_fields(profile)
    if missing:
        logger.warning("CRS simulate rejected, missing fields: %s", missing)
        raise HTTPException(
            status_code=422,
            detail=f"Missing required profile fields: {', '.join(missing)}",
        )
    try:
        profile.crs_score = crs_service.calculate_crs(profile)
        profile.eligibility = eligibility_service.evaluate_express_entry(profile)
    except ValueError as e:
        logger.warning("CRS simulate rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to simulate CRS")
        raise HTTPException(status_code=500, detail="Failed to simulate CRS") from e
    logger.info("CRS simulate request completed")
    return {"crs_score": profile.crs_score, "eligibility": profile.eligibility}


@app.get("/evaluate")
def NOC_retrieval_evaluate():
    logger.info("Received NOC retrieval evaluation request")
    try:
        examples_report, mean_report = noc_retrieval_method_evaluate(
            "data/noc_eval_labels.csv"
        )
    except FileNotFoundError as e:
        logger.warning("NOC retrieval evaluation label file not found: %s", e)
        raise HTTPException(
            status_code=500, detail="Evaluation label file not found"
        ) from e
    except TooManyRequestsError as e:
        logger.warning("NOC retrieval evaluation rate-limited by Cohere: %s", e)
        raise HTTPException(
            status_code=429,
            detail="This benchmark reranks several examples through a rate-limited search API and just went over its quota. Please try again in about a minute.",
        ) from e
    except Exception as e:
        logger.exception("Failed to run NOC retrieval evaluation")
        raise HTTPException(
            status_code=500, detail="Failed to run NOC retrieval evaluation"
        ) from e
    logger.info("NOC retrieval evaluation completed: %s", mean_report)
    return {"examples_report": examples_report.report, "mean_report": mean_report}
