PY = python3
FILES = a_maze_ing.py
INPUT = config.txt

install:
	pip install build flake8 mypy

run: install
	$(PY) ${FILES} $(INPUT)

debug: install
	$(PY) -m pdb ${FILES}

clean:
	rm -rf __pycache__ .mypy_cache *.pyc dist mazegen.egg-info

lint:
	flake8 a_maze_ing.py mazegen/
	mypy a_maze_ing.py mazegen/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint
