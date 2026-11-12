# Image for the Vouch API.
FROM python:3.14-slim

RUN pip install --no-cache-dir uv==0.13.7

WORKDIR /app

# Dependencies first, in their own layer: Docker reuses this layer on rebuilds
# as long as pyproject.toml and uv.lock haven't changed.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY src ./src
RUN uv sync --locked --no-dev

EXPOSE 8000
CMD [".venv/bin/uvicorn", "vouch.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
