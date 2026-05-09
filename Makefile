.PHONY: clean check hinting test all

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name '__pycache__' -exec rm -rf {} +

check:
	ruff check .
	ruff format --check .

hinting:
	mypy . --exclude 'files/' --cache-dir=/dev/null

test:
	pytest -v -p no:cacheprovider

all: clean check hinting test