FROM python:3.11-slim

ARG UV_VERSION=0.10.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends git make build-essential \
    && python -m pip install --no-cache-dir "uv==${UV_VERSION}" \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd -r -g app -d /home/app -m app

ENV HOME=/home/app \
    PYTHONNOUSERSITE=1 \
    UV_LINK_MODE=copy

WORKDIR /work
USER app
