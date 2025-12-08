.PHONY: up down test lint

up:
	@echo "Installing requirements..."
	pip install -r requirements.txt
	@echo "Running pipeline..."
	python src/main.py

down:
	@echo "Cleaning outputs..."
	rm -rf outputs/* || true

test:
	pytest -q
