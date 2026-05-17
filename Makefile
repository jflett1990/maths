.PHONY: setup test lint type run-paper

setup:
	python -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check src tests

type:
	mypy src

run-paper:
	python scripts/run_paper.py --config configs/base.yaml
