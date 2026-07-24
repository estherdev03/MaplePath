# MaplePath AI 🍁

**MaplePath AI** is an AI-powered **Express Entry Assistant** that helps prospective immigrants understand their eligibility for Canada's Express Entry system. It combines LLM-powered profile extraction, a CRS calculator, hybrid NOC search, and Retrieval-Augmented Generation (RAG) to provide accurate, explainable immigration guidance.

Built with **FastAPI**, **PostgreSQL**, **pgvector**, **SQLAlchemy**, **OpenAI**, and **Docker**.

---

## ✨ Features

### 🤖 AI Profile Extraction

- Extract structured immigration profiles from natural language.
- Validate and normalize applicant information using Pydantic models.

### 📊 CRS Score Calculator

- Calculate Comprehensive Ranking System (CRS) scores.
- Provide a detailed score breakdown for every scoring category.

### ✅ Express Entry Eligibility

- Assess eligibility for:
  - Federal Skilled Worker (FSW)
  - Canadian Experience Class (CEC)
  - Federal Skilled Trades (FST)
- Explain eligibility decisions and missing requirements.

### 🔎 Hybrid NOC Search

- Match job titles to the most relevant NOC occupations.
- Combine PostgreSQL Full-Text Search with pgvector semantic search and rerank using Cohere for improved retrieval accuracy.

### 📚 Immigration Policy RAG

- Retrieve relevant IRCC immigration policies.
- Generate grounded answers with citations from official sources.

---

## 🏗️ Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

### Database

- PostgreSQL
- pgvector
- PostgreSQL Full-Text Search

### AI & Search

- OpenAI
- Hybrid Retrieval (Full-Text Search + Vector Search)
- Retrieval-Augmented Generation (RAG)

### DevOps

- Docker
- GitHub
- Pytest

---

## 🎯 Engineering Highlights

- LLM-powered profile extraction
- Rule-based CRS scoring engine
- Express Entry eligibility engine
- Hybrid search using PostgreSQL Full-Text Search and pgvector
- RESTful API with FastAPI
- Automated testing
- Search evaluation and benchmarking

---

## 🚀 Roadmap

### Version 1.0

- ✅ AI Profile Extraction
- ✅ CRS Calculator
- ✅ Hybrid NOC Search
- 🚧 Express Entry Eligibility
- 🚧 Immigration Policy RAG
- 🚧 Search Evaluation
- 🚧 Automated Testing
- 🚧 Docker Deployment

### Future Versions

- Alberta immigration pathways (AAIP)
- Journey planning
- Policy monitoring
- Notification system
