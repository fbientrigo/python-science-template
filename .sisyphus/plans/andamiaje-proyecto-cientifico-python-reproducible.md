# Andamiaje de Proyecto Cientifico Python Reproducible

## TL;DR

> **Quick Summary**: Generar un repositorio base (devcontainer + src/app + tests + CI en Docker + docs con Sphinx) para ciencia reproducible en Python.
>
> **Deliverables**:
> - `.devcontainer/Dockerfile` + `.devcontainer/devcontainer.json`
> - `pyproject.toml`
> - `src/science_lib/` (paquete) + `app/main.py`
> - `tests/` con `conftest.py` y un test de ejemplo
> - `.github/workflows/ci.yml` (build imagen + `pytest` dentro del contenedor)
> - `docs/ARCHITECTURE.md` + Sphinx basico en `docs/` + Makefile target para autogenerar API docs
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Devcontainer Dockerfile/devcontainer.json -> pyproject + paquete -> tests -> CI -> docs

---

## Context

### Original Request
Crear estructura base de repo para ciencia reproducible en Python con:
- devcontainer (Dockerfile + devcontainer.json)
- `src/` + `app/` y `pyproject.toml`
- `tests/` con pytest
- CI que construye la imagen y corre pytest dentro del contenedor
- `docs/ARCHITECTURE.md` + Sphinx (autodoc + napoleon) y autogeneracion API docs

### Metis Review (gaps addressed)
- **Preguntas potenciales** (lockfile, Jupyter, linting, data dir) se tratan como **OUT OF SCOPE por defecto** para evitar scope creep.
- **Riesgo CI bind mount / root-owned files**: en el workflow se ejecuta el contenedor con `--user` para igualar UID/GID del runner.
- **Verificacion faltante**: se agregan criterios de verificacion para `pip install -e`, import check, `python app/main.py`, y build docs con Sphinx.

---

## Work Objectives

### Core Objective
Disponer de un repo Python con layout `src/` reproducible (devcontainer y CI iguales) con tests y docs autogenerables.

### Concrete Deliverables
- `.devcontainer/Dockerfile`
- `.devcontainer/devcontainer.json`
- `pyproject.toml`
- `src/science_lib/__init__.py` (y un modulo minimo para ejemplo)
- `app/main.py`
- `tests/conftest.py` + `tests/science_lib/` espejo
- `.github/workflows/ci.yml`
- `docs/ARCHITECTURE.md`
- `docs/` configuracion Sphinx (incluyendo `conf.py` con `sys.path.insert(...)`)
- `docs/Makefile` (o target equivalente) con `apidoc` usando `sphinx-apidoc`

### Must Have
- CI construye la imagen desde `.devcontainer/Dockerfile` y corre `pytest` dentro del contenedor.
- `src/` es importable (editable install o path configurado) y `app/main.py` funciona importando desde `src`.
- Docs Sphinx compilan y generan API docs desde `src`.

### Must NOT Have (Guardrails)
- No agregar lockfiles (pip-tools/uv/poetry) salvo requerimiento explicito.
- No agregar notebooks/Jupyter, `data/`, DVC/LFS, ni despliegue de docs.
- No agregar pipelines de publicacion (PyPI) ni automatizaciones fuera de CI build+test.

---

## Verification Strategy (MANDATORY)

> Regla universal: toda verificacion debe ser ejecutable por el agente sin intervencion humana.

### Test Decision
- **Infrastructure exists**: se creara `pytest`.
- **Automated tests**: YES (Tests-after; no TDD estricto para scaffolding).
- **Framework**: `pytest`.

### Agent-Executed QA Evidence
- Guardar evidencias en `.sisyphus/evidence/`:
  - Logs: `task-*-*.log`
  - Outputs puntuales: `task-*-*.txt`

---

## Execution Strategy

Wave 1 (Start Immediately):
- Task 1: Devcontainer base
- Task 2: Pyproject + layout src/app/tests

Wave 2 (After Wave 1):
- Task 3: CI docker + pytest inside
- Task 4: Docs + Sphinx + apidoc

---

## TODOs

- [x] 1. Crear entorno `.devcontainer/` (Dockerfile + devcontainer.json)

  **What to do**:
  - Crear `.devcontainer/Dockerfile` basado en `python:3.11-slim`.
  - Instalar via apt: `git`, `make` (para docs), y deps basicas (recomendado: `build-essential` para wheels nativos).
  - Configurar `devcontainer.json` para construir el Dockerfile (contexto repo) y declarar extensiones recomendadas:
    - `ms-python.python`
    - `ms-python.vscode-pylance`
    - `ms-python.black-formatter` (opcional)
    - `charliermarsh.ruff` (opcional)
    - `ms-toolsai.jupyter` (opcional, solo si se decide incluir notebooks mas adelante)
  - (Recomendado) agregar un usuario no-root en la imagen o documentar el uso de `--user` en CI.

  **Suggested implementation snippets** (para evitar ambiguedades):

  `/.devcontainer/Dockerfile` (ejemplo base):

  ```dockerfile
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
  ```

  `/.devcontainer/devcontainer.json` (ejemplo base):

  ```json
  {
    "name": "science-python",
    "build": {
      "dockerfile": "Dockerfile",
      "context": ".."
    },
    "customizations": {
      "vscode": {
        "extensions": [
          "ms-python.python",
          "ms-python.vscode-pylance",
          "ms-python.black-formatter",
          "charliermarsh.ruff",
          "ms-toolsai.jupyter"
        ]
      }
    }
  }
  ```

  **Must NOT do**:
  - No incluir tooling extra (conda/mamba) salvo requerimiento.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: mezcla de Docker + VS Code devcontainer config.
  - **Skills**: (none)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3, Task 4
  - **Blocked By**: None

  **References**:
  - External docs: https://containers.dev/implementors/json_reference/ - esquema de `devcontainer.json`.
  - External docs: https://code.visualstudio.com/docs/devcontainers/containers - patrones recomendados devcontainers.

  **Acceptance Criteria**:
  - [ ] `docker build -f .devcontainer/Dockerfile -t project-devcontainer .` termina OK.
  - [ ] Evidencia: `.sisyphus/evidence/task-1-docker-build.log` (stdout/stderr capturado).

  **Agent-Executed QA Scenarios**:
  
  ```text
  Scenario: Build imagen devcontainer local
    Tool: Bash (docker)
    Preconditions: Docker disponible localmente
    Steps:
      1. docker build -f .devcontainer/Dockerfile -t project-devcontainer . | tee .sisyphus/evidence/task-1-docker-build.log
      2. Assert: exit code 0
    Expected Result: Imagen construida sin errores
    Evidence: .sisyphus/evidence/task-1-docker-build.log
  ```

- [x] 2. Crear estructura `src/` + `app/` + `tests/` y configurar `pyproject.toml`

  **What to do**:
  - Crear `pyproject.toml` con packaging moderno via `setuptools` y layout `src/`.
  - Definir paquete ejemplo: `science_lib` en `src/science_lib/__init__.py`.
  - Crear un modulo minimo (ej. `src/science_lib/core.py`) para tener algo testeable.
  - Crear `app/main.py` que importe desde `science_lib` (ej. `from science_lib.core import ...`) y ejecute un ejemplo.
  - Crear `tests/conftest.py` basico.
  - Crear `tests/science_lib/test_core.py` (espejo de `src/science_lib/core.py`).
  - Configurar `pytest` en `pyproject.toml` (`[tool.pytest.ini_options]`).
  - Definir extra `dev` (recomendado) con `pytest`, `sphinx`, y un tema estable (ej. `sphinx-rtd-theme`).

  **Suggested implementation snippets** (para evitar ambiguedades):

  `/pyproject.toml` (esqueleto; completar nombre/version/descripcion):

  ```toml
  [build-system]
  requires = ["setuptools>=68", "wheel"]
  build-backend = "setuptools.build_meta"

  [project]
  name = "science-project"
  version = "0.1.0"
  description = "Reproducible scientific Python scaffold"
  requires-python = ">=3.11"
  dependencies = []

  [project.optional-dependencies]
  dev = [
    "pytest>=8",
    "sphinx>=7",
    "sphinx-rtd-theme>=2"
  ]

  [tool.setuptools]
  package-dir = {"" = "src"}

  [tool.setuptools.packages.find]
  where = ["src"]

  [tool.pytest.ini_options]
  testpaths = ["tests"]
  addopts = "-q"
  ```

  `src/science_lib/core.py` (ejemplo minimo):

  ```python
  def add(a: float, b: float) -> float:
      return a + b
  ```

  `tests/science_lib/test_core.py` (ejemplo minimo):

  ```python
  from science_lib.core import add

  def test_add():
      assert add(1, 2) == 3
  ```

  **Must NOT do**:
  - No introducir dependencias cientificas especificas (numpy/pandas) salvo requerimiento.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: mezcla de packaging (pyproject) + estructura.
  - **Skills**: (none)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 3, Task 4
  - **Blocked By**: None

  **References**:
  - External docs: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ - PEP 621 + pyproject.
  - External docs: https://docs.pytest.org/en/stable/reference/customize.html#pyproject-toml - pytest config en pyproject.

  **Acceptance Criteria**:
  - [ ] En el host (o dentro del contenedor): `python -m pip install -e ".[dev]"` termina OK.
  - [ ] `python -c "import science_lib; print(science_lib.__file__)"` imprime una ruta bajo `src/`.
  - [ ] `python app/main.py` termina OK (exit code 0).
  - [ ] `pytest -q` termina OK.
  - [ ] Evidencia:
    - `.sisyphus/evidence/task-2-pip-install.log`
    - `.sisyphus/evidence/task-2-import-check.txt`
    - `.sisyphus/evidence/task-2-pytest.log`

  **Agent-Executed QA Scenarios**:

  ```text
  Scenario: Editable install + import check
    Tool: Bash (python/pip)
    Preconditions: Python 3.11 disponible (host o contenedor)
    Steps:
      1. python -m pip install -e ".[dev]" | tee .sisyphus/evidence/task-2-pip-install.log
      2. python -c "import science_lib; print(science_lib.__file__)" | tee .sisyphus/evidence/task-2-import-check.txt
      3. pytest -q | tee .sisyphus/evidence/task-2-pytest.log
      4. Assert: exit code 0
    Expected Result: Paquete instalable e importable; tests pasan
    Evidence: .sisyphus/evidence/task-2-*.log/.txt
  ```

- [x] 3. Crear CI `.github/workflows/ci.yml` (build Dockerfile + pytest dentro del contenedor)

  **What to do**:
  - Crear workflow `ci.yml` que corra en `push` y `pull_request`.
  - Paso 1: checkout.
  - Paso 2: `docker build` usando `.devcontainer/Dockerfile`.
  - Paso 3: `docker run` ejecutando `pytest` dentro del contenedor.
    - Mitigar root-owned files: ejecutar con `--user $(id -u):$(id -g)` o asegurando usuario no-root por defecto.
  - Dentro del contenedor, instalar el repo: `python -m pip install -e ".[dev]"` y luego `pytest`.

  **Must NOT do**:
  - No agregar publish ni despliegue; solo build + test.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: GitHub Actions + Docker.
  - **Skills**: (none)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: none
  - **Blocked By**: Task 1, Task 2

  **References**:
  - External docs: https://docs.github.com/en/actions - sintaxis workflows.
  - External docs: https://docs.docker.com/build/ci/github-actions/ - docker build en actions.

  **Acceptance Criteria**:
  - [ ] En GitHub Actions, job `ci` pasa en PR/push.
  - [ ] El log de CI muestra que `pytest` se ejecuto dentro del contenedor construido desde `.devcontainer/Dockerfile`.

  **Agent-Executed QA Scenarios**:

  ```text
  Scenario: Emular CI localmente con docker run
    Tool: Bash (docker)
    Preconditions: Imagen construida (Task 1) y repo con pyproject/tests (Task 2)
    Steps:
      1. docker build -f .devcontainer/Dockerfile -t project-devcontainer .
      2. docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/work -w /work project-devcontainer \
           sh -lc "python -m pip install -e '.[dev]' && pytest -q" \
           | tee .sisyphus/evidence/task-3-ci-local-docker-run.log
      3. Assert: exit code 0
    Expected Result: pytest pasa dentro del contenedor
    Evidence: .sisyphus/evidence/task-3-ci-local-docker-run.log
  ```

- [x] 4. Documentacion viva en `docs/` (ARCHITECTURE.md + Sphinx + apidoc)

  **What to do**:
  - Crear `docs/ARCHITECTURE.md` explicando:
    - Por que `src/` contiene el paquete (logica) y `app/` contiene entry points.
    - Como se garantiza reproducibilidad (devcontainer + CI en Docker).
    - Convenciones basicas de tests y docs.
  - Inicializar Sphinx basico en `docs/`:
    - Crear `docs/source/conf.py`.
    - En `conf.py`, agregar `src` al path (ej. `sys.path.insert(0, os.path.abspath('../../src'))`).
    - Habilitar `sphinx.ext.autodoc` y `sphinx.ext.napoleon`.
    - Crear `docs/source/index.rst`.
  - Agregar un target `apidoc` en `docs/Makefile` (o Makefile raiz) que corra `sphinx-apidoc` para generar stubs API desde `src/science_lib` hacia `docs/source/api/`.
  - Asegurar que `make -C docs html` funciona (o `sphinx-build`).

  **Must NOT do**:
  - No desplegar docs (GitHub Pages) ni agregar tutoriales extensos.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Sphinx + estructura docs.
  - **Skills**: (none)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: none
  - **Blocked By**: Task 2

  **References**:
  - External docs: https://www.sphinx-doc.org/en/master/usage/quickstart.html - estructura Sphinx.
  - External docs: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html - `sphinx-apidoc`.
  - External docs: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html - autodoc.
  - External docs: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html - napoleon.

  **Acceptance Criteria**:
  - [ ] `python -m pip install -e ".[dev]"` instalado.
  - [ ] `make -C docs apidoc` genera stubs en `docs/source/api/`.
  - [ ] `make -C docs html` termina OK.
  - [ ] Evidencia:
    - `.sisyphus/evidence/task-4-sphinx-apidoc.log`
    - `.sisyphus/evidence/task-4-sphinx-html.log`

  **Agent-Executed QA Scenarios**:

  ```text
  Scenario: Generar docs API + HTML
    Tool: Bash (make/sphinx)
    Preconditions: Extra dev instalado (pytest+sphinx)
    Steps:
      1. make -C docs apidoc | tee .sisyphus/evidence/task-4-sphinx-apidoc.log
      2. make -C docs html | tee .sisyphus/evidence/task-4-sphinx-html.log
      3. Assert: exit code 0
    Expected Result: Documentacion HTML generada sin errores
    Evidence: .sisyphus/evidence/task-4-sphinx-*.log
  ```

---

## Commit Strategy

- Commit 1 (Task 1-2): `chore(scaffold): add devcontainer and python src/app/tests layout`
- Commit 2 (Task 3): `ci: run pytest inside devcontainer image`
- Commit 3 (Task 4): `docs: add architecture and sphinx scaffolding`

---

## Success Criteria

### Verification Commands
```bash
docker build -f .devcontainer/Dockerfile -t project-devcontainer .
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/work -w /work project-devcontainer sh -lc "python -m pip install -e '.[dev]' && pytest -q"
python -m pip install -e ".[dev]"
python -c "import science_lib; print(science_lib.__file__)"
python app/main.py
make -C docs apidoc
make -C docs html
```

### Final Checklist
- [ ] Devcontainer build OK
- [ ] Paquete importable desde `src/`
- [ ] Tests pasan localmente y dentro del contenedor
- [ ] CI pasa (pytest dentro del contenedor)
- [ ] Docs (Sphinx) se generan con autodoc + napoleon y API stubs
