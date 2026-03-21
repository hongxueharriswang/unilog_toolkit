
# Contributing to UniLog Toolkit

Thanks for your interest in contributing! This guide explains how to propose changes, add features, fix bugs, and help with docs and examples.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Development Environment](#development-environment)
- [Project Layout](#project-layout)
- [Style & Linting](#style--linting)
- [Running Tests](#running-tests)
- [Pull Request Checklist](#pull-request-checklist)
- [Issue Triage](#issue-triage)
- [Release & Versioning](#release--versioning)

## Code of Conduct
Participation in this project is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By interacting with this repository, you agree to abide by it.

## Development Environment
1. **Clone** the repository and install in editable mode:
   ```bash
   git clone https://github.com/hongxueharriswang/unilog_toolkit.git
   cd unilog_toolkit
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   pip install -U pip
   pip install -e .
   ```
2. **Install dev tools** (linters, test runner, docs):
   ```bash
   pip install pytest ruff black sphinx sphinx-autodoc-typehints furo pdoc
   ```

## Project Layout
```
unilog/
  parser/            # UniLang.g4, parser entry points
  ast/               # AST nodes, visitors
  engine/            # InferenceEngine, Model, solvers
  utils/             # PrettyPrinter, SubstitutionVisitor
examples/            # runnable samples (see below)
tests/               # unit tests
.github/workflows/   # CI configuration
docs/                # Sphinx + pdoc configuration
```

## Style & Linting
- **Black** for formatting (`black .`)
- **Ruff** for linting (`ruff check .`)

> Defaults are fine. If we later add a project-wide config, the CI will pick it up automatically.

## Running Tests
Run the full test suite with:
```bash
pytest -q
```

## Pull Request Checklist
- [ ] Feature or fix is covered by tests (or examples where appropriate)
- [ ] `ruff check .` reports no errors
- [ ] `black --check .` passes
- [ ] Updated docs and/or docstrings if behavior changed
- [ ] Added an entry in `CHANGELOG.md` (if we keep one) and updated `README.md` where relevant

## Issue Triage
- Use labels: `bug`, `feature`, `docs`, `examples`, `infra`, `help wanted`, `good first issue`
- For bugs, please include **minimal reproduction**, **expected vs actual**, and **environment info** (OS, Python, package version)

## Release & Versioning
We follow **semantic versioning** (MAJOR.MINOR.PATCH). Pre-1.0 minor versions may include breaking changes, but we will call them out in the release notes.
