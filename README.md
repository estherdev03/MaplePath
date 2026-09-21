# MaplePath AI

**An AI-powered Express Entry assistant for Canada’s skilled immigration system.**

MaplePath helps prospective immigrants understand where they stand: it extracts a structured profile from natural language, classifies the occupation under **NOC 2021**, calculates a **CRS** score, and assesses eligibility for **Federal Skilled Worker**, **Canadian Experience Class**, and **Federal Skilled Trades**.

Built as a production-oriented **Python** backend: **LangGraph** orchestration, hybrid retrieval over PostgreSQL, retrieval-augmented occupation classification, and **rule-based** scoring engines that stay explainable—not a black-box chatbot. A **Next.js** frontend walks applicants through intake, confirmation, and results against that API.

---



## Why it exists

Express Entry decisions depend on occupation codes, language conversions, and program-specific rules. Applicants often receive generic advice that cannot be audited. MaplePath separates **AI where it is useful** (parsing and occupation matching) from **deterministic policy** (CRS and eligibility), so every result can be inspected category by category.

---



## Capabilities


| Area                     | What it delivers                                                                                                                          |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Profile intelligence** | Converts unstructured text into a validated applicant profile, flagging missing or ambiguous fields instead of inventing data             |
| **Occupation matching**  | Hybrid search retrieves official NOC 2021 profiles, an LLM then picks a unit group, TEER, and confidence score from those candidates only |
| **CRS scoring**          | Full Comprehensive Ranking System breakdown: core human capital, spouse factors, skill transferability, and additional points             |
| **Program eligibility**  | Requirement-level results for FSW, CEC, and FST, including the FSW 67-point selection grid and settlement-fund checks                     |


**Language support:** IELTS, CELPIP, and PTE (English); TEF and TCF (French), converted to CLB / NCLC before scoring.

---



## Engineering highlights

Skills this project is designed to demonstrate:

- **Agentic workflow design** with LangGraph (event routing, typed state, multi-step profile → score → eligibility pipeline)
- **Hybrid search** combining BM25 full-text retrieval, pgvector semantic search, Reciprocal Rank Fusion, and Cohere reranking
- **Retrieval-augmented generation (RAG)** for NOC classification: retrieved occupation records are passed as context, and the model must choose from that list rather than invent a code
- **LLM structured extraction** with LangChain / OpenAI—constrained to stated facts, with missing-field and warning lists
- **Domain rule engines** for CRS and Express Entry, implemented in Python with Pydantic models (auditable point tables, not prompt-only scoring)
- **Retrieval evaluation** using NDCG@10 and hit rate across BM25, vector, RRF, and hybrid pipelines
- **API and data layer**: FastAPI, SQLAlchemy, PostgreSQL, Docker Compose for local infrastructure
- **End-to-end product surface**: a Next.js/TypeScript frontend (intake, confirmation, CRS simulator, NOC search, eligibility, and advice views) calling the FastAPI backend
- **Automated test suite** with pytest covering the graph, services, and API layer

---



## Architecture

```
Natural language or confirmed form
        │
        ▼
   LangGraph orchestrator
        │
        ├── parse profile          (LLM structured output)
        └── confirm profile
                ├── retrieve NOC candidates (hybrid search)
                ├── classify occupation from retrieved context

                ├── CRS calculation
                └── Express Entry eligibility
                        └── JSON result (occupation, scores, program breakdowns)
```


| Module          | Responsibility                                                                |
| --------------- | ----------------------------------------------------------------------------- |
| `graph/`        | Workflow graph, routers, and shared application state                         |
| `user_profile/` | Profile parse, occupation classification, score and eligibility orchestration |
| `noc/`          | NOC ingest, hybrid search, retrieval evaluation                               |
| `crs/`          | CRS points, language conversion, skill transferability                        |
| `eligibility/`  | FSW, CEC, and FST rule evaluation                                             |
| `db/`           | SQLAlchemy models and persistence                                             |
| `api/`          | REST API                                                                      |
| `frontend/`     | Next.js application (intake, confirmation, simulator, NOC search, results)   |
| `tests/`        | pytest suite mirroring the module layout above                               |


---



## Tech stack

**Languages & runtime:** Python 3.12, uv, Node.js  

**AI & retrieval:** LangGraph, LangChain, OpenAI (chat + embeddings), Cohere Rerank  

**Backend:** FastAPI, Pydantic, SQLAlchemy  

**Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS  

**Data:** PostgreSQL, pgvector, BM25 (`pg_textsearch`)  

**Ops:** Docker Compose, Makefile  

**Testing:** pytest  

---



## Getting started

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 20+, Docker, OpenAI and Cohere API keys.

**Backend:**

```bash
uv sync
cp example.env .env   # set OPENAI_API_KEY, COHERE_API_KEY, POSTGRES_*, DB_URL
make pgup
uv run python init_db.py          # first run: load NOC 2021 from ESDC and generate embeddings
uv run fastapi dev api/app.py
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000, expects the API at http://localhost:8000 (override with API_URL)
```


| Method | Endpoint            | Description                                                 |
| ------ | ------------------- | ------------------------------------------------------------|
| `POST` | `/profile/parse`    | Extract a structured draft from free-text                   |
| `POST` | `/profile/complete` | Confirm a profile; return occupation, CRS, and eligibility   |
| `POST` | `/crs/simulate`     | Recalculate CRS score and eligibility for an edited profile |
| `GET`  | `/evaluate`         | Run the NOC retrieval benchmark and return its report        |


Sample graph run without the API: `uv run python main.py`.

NOC retrieval benchmark: `uv run python noc/evaluate.py` (labeled set in `data/noc_eval_labels.csv`).

Run the test suite: `make test` (or `uv run pytest`).

Stop the database with `make pgdown` (add `make pgdownvol` to drop the volume). Initial `init_db.py` scrapes official NOC profiles and may take a substantial amount of time.

---



## Roadmap

**Current (v1)**  
AI profile extraction · hybrid NOC search · RAG occupation classification · CRS calculator · Express Entry eligibility · retrieval evaluation · Next.js frontend · automated test suite  

**In progress**  
Containerized application deploy  

**Next**  
Policy Q&A with cited IRCC sources · Alberta (AAIP) pathways · journey planning · policy monitoring and notifications  

---

MaplePath is an engineering project for educational and demonstration purposes. It is **not legal advice** and does not replace IRCC tools or a licensed immigration representative. Scoring tables and program rules should be verified against current Government of Canada publications.