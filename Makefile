MAP ?= config.txt

run:
	python3 fly_in.py $(MAP) || true

install:
	pip install -r requirements.txt

debug:
	python3 -m pdb fly_in.py $(MAP)

clean:
	rm -rf __pycache__ .mypy_cache */__pycache__
	@echo "Cleaned up cache files."

lint:
	python3 -m flake8 .
	python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


.PHONY: install run debug clean lint 