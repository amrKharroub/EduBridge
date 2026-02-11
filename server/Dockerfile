FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

ARG UV_NO_DEV=0

#compile bytecode and remove hardlink warning
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

#install dev dependencies
ENV UV_NO_DEV=$UV_NO_DEV

#disable python downloads
ENV UV_PYTHON_DOWNLOADS=0

#dont create cache files and buffer logs 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

#caching to reduce build time
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked


# Then, use a final image without uv
FROM python:3.13-slim-trixie

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

#dont create cache files and buffer logs 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN chmod +x /app/entrypoint.dev.sh

# Use the non-root user to run our application
USER nonroot

# Use `/app` as the working directory
WORKDIR /app

EXPOSE 8000

CMD ["./entrypoint.dev.sh"]