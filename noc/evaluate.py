# NDCG metric to evaluate NOC retrieval method (Vector, BM25 and Hybrid)
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

        print(relevance_list)

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

        return dcg_score / idcg_score

if __name__ =="__main__":
    db_service = DatabaseService(db_url=os.getenv("DB_URL"))
    noc_repository = NOCRepository(db_service=db_service)
    noc_service = NOCService(noc_repository=noc_repository)
    evaluate_service = EvaluateService(noc_service=noc_service)

    df = pd.read_csv("data/noc_eval_labels.csv")
    df["search_query"] = df.apply(lambda row: f"Job title: {row['job_title']} \n Job responsibility: {row['job_responsibility']}", axis=1)
    for row in df.itertuples():
        search_query = row.search_query
        noc_code = str(row.noc_code) 
        minor_group_code = str(row.minor_group_code)
        major_group_code = str(row.major_group_code)
        ideal_noc = IdealNOC(noc_code=noc_code, minor_group_code=minor_group_code, major_group_code=major_group_code)
        keyword_result = noc_service.noc_keyword_search(search_query)
        vector_result = noc_service.noc_semantic_search(search_query)
        hybrid_result = noc_service.noc_hybrid_search(search_query)
        print("==============================================")
        print(f"Case type: {row.case_type}")
        print(f"Job title: {row.job_title}")
        print(f"BM25: {evaluate_service.ndcg_evaluate(keyword_result, ideal_noc, 10)}")
        print(f"Vector: {evaluate_service.ndcg_evaluate(vector_result, ideal_noc, 10)}")
        print(f"Hybrid Search: {evaluate_service.ndcg_evaluate(hybrid_result, ideal_noc, 10)}")
        print("==============================================")

        