import logging

from db.models import NocEvaluationRun
from db.service import DatabaseService

logger = logging.getLogger(__name__)


class EvaluateRepository:
    """Persist/retrieve cached NOC retrieval evaluation runs."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def get_by_hash(self, labels_hash: str) -> NocEvaluationRun | None:
        with self.db_service.create_session() as session:
            return session.get(NocEvaluationRun, labels_hash)

    def save(
        self, labels_hash: str, examples_report: list[dict], mean_report: dict
    ) -> None:
        with self.db_service.create_session() as session:
            session.merge(
                NocEvaluationRun(
                    labels_hash=labels_hash,
                    examples_report=examples_report,
                    mean_report=mean_report,
                )
            )
            session.commit()
        logger.info("Saved NOC retrieval evaluation run for labels hash %s", labels_hash)
