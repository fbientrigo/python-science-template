IMAGE_TAG ?= science-template:verify
UV ?= uv

.PHONY: init lock sync lint test docs smoke local-verify verify docker-build docker-verify docker-verify-rw clean

init:
	python scripts/init_project.py

lock:
	$(UV) lock

sync:
	@if [ -f uv.lock ]; then \
	  $(UV) sync --group dev --group docs --frozen; \
	else \
	  echo "WARNING: uv.lock missing; resolving dependencies from pyproject.toml"; \
	  $(UV) sync --group dev --group docs; \
	fi

lint:
	$(UV) run --no-sync ruff check .

test:
	$(UV) run --no-sync pytest

docs:
	$(UV) run --no-sync sphinx-build -W -b html docs/source docs/build/html

smoke:
	$(UV) run --no-sync python app/main.py

local-verify: sync lint test docs smoke

verify: docker-verify

docker-build:
	docker build -f .devcontainer/Dockerfile -t $(IMAGE_TAG) .

# Canonical gate: the checkout is read-only; all installation/build writes happen in /tmp/work.
docker-verify: docker-build
	docker run --rm \
	  -v "$(CURDIR)":/work:ro \
	  -e HOME=/tmp \
	  -e XDG_CACHE_HOME=/tmp/.cache \
	  -e UV_CACHE_DIR=/tmp/uv-cache \
	  -e PYTHONNOUSERSITE=1 \
	  $(IMAGE_TAG) \
	  sh -lc 'cp -a /work /tmp/work \
	    && cd /tmp/work \
	    && if [ -f uv.lock ]; then uv sync --group dev --group docs --frozen; else echo "WARNING: uv.lock missing; resolving dependencies"; uv sync --group dev --group docs; fi \
	    && uv run --no-sync ruff check . \
	    && uv run --no-sync pytest \
	    && uv run --no-sync sphinx-build -W -b html docs/source docs/build/html \
	    && uv run --no-sync python app/main.py'

# Debug only: permits writes to the checkout and is intentionally not used by CI.
docker-verify-rw: docker-build
	@echo "WARNING: read-write verification may create local artifacts."
	docker run --rm \
	  -v "$(CURDIR)":/work \
	  -w /work \
	  -e HOME=/tmp \
	  -e XDG_CACHE_HOME=/tmp/.cache \
	  -e UV_CACHE_DIR=/tmp/uv-cache \
	  -e PYTHONNOUSERSITE=1 \
	  $(IMAGE_TAG) \
	  sh -lc 'if [ -f uv.lock ]; then uv sync --group dev --group docs --frozen; else echo "WARNING: uv.lock missing; resolving dependencies"; uv sync --group dev --group docs; fi \
	    && uv run --no-sync ruff check . \
	    && uv run --no-sync pytest \
	    && uv run --no-sync sphinx-build -W -b html docs/source docs/build/html \
	    && uv run --no-sync python app/main.py'

clean:
	rm -rf .venv build dist .pytest_cache .ruff_cache docs/build src/*.egg-info
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
