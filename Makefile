IMAGE_TAG ?= science-template:verify

.PHONY: docker-build docker-verify docker-verify-rw clean

docker-build:
	docker build -f .devcontainer/Dockerfile -t $(IMAGE_TAG) .

docker-verify: docker-build
	mkdir -p .sisyphus/evidence
	docker run --rm \
	  -v "$(CURDIR)":/work:ro \
	  -v science-template-pip-cache:/tmp/pip-cache \
	  -e PYTHONDONTWRITEBYTECODE=1 \
	  -e XDG_CACHE_HOME=/tmp/.cache \
	  -e PIP_CACHE_DIR=/tmp/pip-cache \
	  $(IMAGE_TAG) \
	  sh -lc 'cp -a /work /tmp/work \
	    && cd /tmp/work \
	    && python -m venv /tmp/venv \
	    && /tmp/venv/bin/pip install -U pip \
	    && /tmp/venv/bin/pip install ".[test]" \
	    && /tmp/venv/bin/pytest -q -o cache_dir=/tmp/pytest_cache \
	    && /tmp/venv/bin/python app/main.py' \
	  | tee .sisyphus/evidence/task-1-docker-verify.log

# Debugging target: read-write mount (use only when read-only breaks)
docker-verify-rw: docker-build
	@echo "WARNING: Using read-write mount. This may pollute the workspace."
	mkdir -p .sisyphus/evidence
	docker run --rm \
	  -v "$(CURDIR)":/work \
	  -w /work \
	  -e PYTHONDONTWRITEBYTECODE=1 \
	  -e XDG_CACHE_HOME=/tmp/.cache \
	  -e PIP_CACHE_DIR=/tmp/pip-cache \
	  $(IMAGE_TAG) \
	  sh -lc 'python -m venv /tmp/venv \
	    && /tmp/venv/bin/pip install -U pip \
	    && /tmp/venv/bin/pip install ".[test]" \
	    && /tmp/venv/bin/pytest -q -o cache_dir=/tmp/pytest_cache \
	    && /tmp/venv/bin/python app/main.py' \
	  | tee .sisyphus/evidence/task-1-docker-verify-rw.log

clean:
	rm -rf build/ dist/ src/*.egg-info/ .pytest_cache/ .sisyphus/evidence/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	$(MAKE) -C docs clean
