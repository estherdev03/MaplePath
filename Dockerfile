FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.16 /uv /usr/local/bin/uv

# noc.esdc.gc.ca doesn't send its intermediate certificate. macOS fetches it
# automatically; Linux doesn't, so add it to the system trust store for
# init_db.py's NOC scraping (truststore reads this store).
COPY certs/ /usr/local/share/ca-certificates/
RUN update-ca-certificates

WORKDIR /app

# Install dependencies first so they're cached across code-only changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Railway injects PORT; fall back to 8000 for local runs
CMD uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000}
