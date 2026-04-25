# Contributing to Democracy Desk

First off, thank you for considering contributing to Democracy Desk! It's people like you that make Democracy Desk such a great tool for voter education.

## Technical Standards

To maintain our 95+ quality score, we enforce the following:
- **Type Hinting**: All new functions must include complete Python type hints.
- **Documentation**: All public methods must include Google-style docstrings.
- **Tests**: Every new feature must be accompanied by a `pytest` suite with at least 90% coverage.
- **Architecture**: Always follow the multi-agent orchestration pattern defined in `core/orchestrator.py`.

## Style Guide
We follow **PEP 8** with a 100-character line limit. Please use `black` for formatting and `isort` for import organization.

## Local Development
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `pytest tests/`
4. Start dev server: `python -m api.main`
