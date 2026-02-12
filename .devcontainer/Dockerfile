FROM python:3.11-slim

# Basic OS deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
         git \
         make \
         build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip tooling
RUN python -m pip install --upgrade pip setuptools wheel

# Devcontainers typically mount the repo; keep workdir generic
WORKDIR /work
