# NDCG metric to evaluate NOC retrieval method (Vector, BM25 and Hybrid)

from math import log
import os
from db.models import NOC
from db.service import DatabaseService
from noc.repository import IdealNOC, NOCRepository
from noc.service import NOCService


def ndcg_evaluate(
    noc_service: NOCService, search_result: list[NOC], ideal: IdealNOC, k: int = 10
) -> float:
    relevance_list = []
    for noc in search_result:
        relevance_score = 0
        if noc.noc_code == ideal.noc_code:
            relevance_score = 3
        elif noc.minor_group_code == ideal.minor_group_code:
            relevance_score = 2
        elif noc.major_group_code == ideal.major_group_code:
            relevance_score = 1
        relevance_list.append(relevance_score)

    # add padding zeros if necessary
    while len(relevance_list) < k:
        relevance_list.append(0)

    print(relevance_list)
    dcg_score = 0
    for rank, relevance in enumerate(relevance_list, start=1):
        dcg_score += relevance / log(rank + 1, 2)

    minor_count, major_count = noc_service.get_ideal_pool_count(ideal)
    ideal_relevance_list = ([3] * 1 + [2] * minor_count + [1] * major_count)[:k]

    # add padding zeros if necessary
    while len(ideal_relevance_list) < k:
        ideal_relevance_list.append(0)

    idcg_score = 0
    for rank, relevance in enumerate(ideal_relevance_list, start=1):
        idcg_score += relevance / log(rank + 1, 2)

    return dcg_score / idcg_score


# Example test case
job_title="Software Developer"
job_responsibility=(
            "Design, build and maintain backend REST APIs in Python, write unit "
            "tests, review code, and deploy services to AWS."
        )
ideal_noc=IdealNOC("21232", "2123", "21")  # Software developers and programmers

# construct search query
search_query = f"""
Job title: {job_title} \n Job responsibility: {job_responsibility}
"""

db_service = DatabaseService(db_url=os.getenv("DB_URL"))
noc_repository = NOCRepository(db_service=db_service)
noc_service = NOCService(noc_repository=noc_repository)

keyword_result = noc_service.noc_keyword_search(search_query)
vector_result = noc_service.noc_semantic_search(search_query)
hybrid_result = noc_service.noc_hybrid_search(search_query)

print(f"BM25: {ndcg_evaluate(noc_service,keyword_result[:10], ideal_noc, 10)}")
print(f"Vector: {ndcg_evaluate(noc_service,vector_result[:10], ideal_noc, 10)}")
print(f"Hybrid Search: {ndcg_evaluate(noc_service,hybrid_result[:10], ideal_noc, 10)}")
