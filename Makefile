PY = python3
FILES = a_maze_ing.py
INPUT = config.txt



run: install
	$(PY) ${FILES} $(INPUT)

debug: install
	$(PY) -m pdb ${FILES}

clean:
	rm -rf __pycache__ .mypy_cache *.pyc

lint:
	flake8 ${FILES}
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 ${FILES}
	mypy . --strict

help:
	@echo "Available targets:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the maze generator"
	@echo "  make debug        - Run with debugger"
	@echo "  make clean        - Remove cache files"
	@echo "  make lint         - Run linters"
	@echo "  make lint-strict  - Run strict linters"
.PHONY: install run debug clean lint lint-strict help
