# =============================================================
FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_NO_SYNC=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-install-project

# =============================================================
FROM base AS dev

ENV PYTHONDEVMODE=1

RUN uv sync --locked --all-extras --no-install-project

COPY . .

# =============================================================
FROM base AS production

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser

COPY --exclude=**/tests --exclude=*.md --exclude=*.ini ./src ./

ENTRYPOINT ["uv", "run", "run.py"]
