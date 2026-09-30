FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.16 /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first so they're cached across code-only changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Railway injects PORT; fall back to 8000 for local runs
CMD uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000}
