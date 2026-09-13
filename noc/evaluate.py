# NDCG metric to evaluate NOC retrieval method (Vector, BM25, RRF only and Hybrid)
from math import log
import os
from db.models import NOC
from db.service import DatabaseService
from noc.repository import IdealNOC, NOCRepository
from noc.service import NOCService
import pandas as pd


class EvaluateService:
    def __init__(self, noc_service: NOCService):
        self.noc_service = noc_service

    def ndcg_evaluate(
        self, search_result: list[NOC], ideal: IdealNOC, k: int = 10
    ) -> float:
        # relevance score list
        relevance_list = []
        for noc in search_result[:k]:
            relevance_score = 0
            if noc.noc_code == ideal.noc_code:
                relevance_score = 3
            elif noc.minor_group_code == ideal.minor_group_code:
                relevance_score = 2
            elif noc.major_group_code == ideal.major_group_code:
                relevance_score = 1
            relevance_list.append(relevance_score)

        # calculate DCG
        dcg_score = 0
        for rank, relevance in enumerate(relevance_list, start=1):
            dcg_score += relevance / log(rank + 1, 2)

        minor_count, major_count = self.noc_service.get_ideal_pool_count(ideal)
        ideal_relevance_list = ([3] * 1 + [2] * minor_count + [1] * major_count)[:k]

        # add padding zeros if necessary
        while len(ideal_relevance_list) < k:
            ideal_relevance_list.append(0)

        # calculate IDCG
        idcg_score = 0
        for rank, relevance in enumerate(ideal_relevance_list, start=1):
            idcg_score += relevance / log(rank + 1, 2)

        return dcg_score / idcg_score  # NDCG

    # calculate hit rate @ k
    def hit_rate(self, search_result: list[NOC], ideal: IdealNOC, k: int = 10) -> int:
        for noc in search_result:
            if noc.noc_code == ideal.noc_code:
                return 1
        return 0


if __name__ == "__main__":
    db_service = DatabaseService(db_url=os.getenv("DB_URL"))
    noc_repository = NOCRepository(db_service=db_service)
    noc_service = NOCService(noc_repository=noc_repository)
    evaluate_service = EvaluateService(noc_service=noc_service)

    df = pd.read_csv("data/noc_eval_labels.csv")
    df["search_query"] = df.apply(
        lambda row: f"Job title: {row['job_title']} \n Job responsibility: {row['job_responsibility']}",
        axis=1,
    )
    total_ndcg_bm25 = 0
    total_ndcg_vector = 0
    total_ndcg_hybrid = 0
    total_ndcg_rrf = 0
    total_hit_bm25 = 0
    total_hit_vector = 0
    total_hit_hybrid = 0
    total_hit_rrf = 0
    for row in df.itertuples():
        search_query = row.search_query
        noc_code = str(row.noc_code)
        minor_group_code = str(row.minor_group_code)
        major_group_code = str(row.major_group_code)
        ideal_noc = IdealNOC(
            noc_code=noc_code,
            minor_group_code=minor_group_code,
            major_group_code=major_group_code,
        )
        keyword_result = noc_service.noc_keyword_search(search_query)
        vector_result = noc_service.noc_semantic_search(search_query)
        hybrid_result = noc_service.noc_hybrid_search(search_query)
        rrf_result = noc_service._rrf(vector_result, keyword_result)

        # -------------------- NDCG -----------------------------
        # BM25
        bm25_ndcg = evaluate_service.ndcg_evaluate(keyword_result, ideal_noc, 10)
        # Vector
        vector_ndcg = evaluate_service.ndcg_evaluate(vector_result, ideal_noc, 10)
        # Hybrid (RRF + Cohere Rerank)
        hybrid_ndcg = evaluate_service.ndcg_evaluate(hybrid_result, ideal_noc, 10)
        # Only RRF
        rrf_ndcg = evaluate_service.ndcg_evaluate(rrf_result, ideal_noc, 10)
        total_ndcg_bm25 += bm25_ndcg
        total_ndcg_vector += vector_ndcg
        total_ndcg_hybrid += hybrid_ndcg
        total_ndcg_rrf += rrf_ndcg
        # -------------------- HIT RATE -----------------------------
        # BM25
        bm25_hit = evaluate_service.hit_rate(keyword_result, ideal_noc, 10)
        # Vector
        vector_hit = evaluate_service.hit_rate(vector_result, ideal_noc, 10)
        # Hybrid (RRF + Cohere Rerank)
        hybrid_hit = evaluate_service.hit_rate(hybrid_result, ideal_noc, 10)
        # Only RRF
        rrf_hit = evaluate_service.hit_rate(rrf_result, ideal_noc, 10)
        total_hit_bm25 += bm25_hit
        total_hit_vector += vector_hit
        total_hit_hybrid += hybrid_hit
        total_hit_rrf += rrf_hit
        print("==============================================")
        print(f"Case type: {row.case_type}")
        print(f"Job title: {row.job_title}")
        print(f"BM25: {bm25_ndcg} (NDCG) | {bm25_hit} (Hit Rate)")
        print(f"Vector: {vector_ndcg} (NDCG) | {vector_hit} (Hit Rate)")
        print(f"RRF only: {rrf_ndcg} (NDCG) | {rrf_hit} (Hit Rate)")
        print(
            f"Hybrid (RRF + Cohere Rerank): {hybrid_ndcg} (NDCG) | {hybrid_hit} (Hit Rate)"
        )
        print("==============================================")

    print("----------------------")
    print(f"Mean BM25: {total_ndcg_bm25/10} (NDCG) | {total_hit_bm25/10} (Hit Rate)")
    print(
        f"Mean Vector: {total_ndcg_vector/10} (NDCG) | {total_hit_vector/10} (Hit Rate)"
    )
    print(f"Mean RRF only: {total_ndcg_rrf/10} (NDCG) | {total_hit_rrf/10} (Hit Rate)")
    print(
        f"Mean Hybrid (RRF + Cohere Rerank): {total_ndcg_hybrid/10} (NDCG) | {total_hit_hybrid/10} (Hit Rate)"
    )
    print("----------------------")
