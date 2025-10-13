.PHONY: test clean install help

help:
	@echo "Available targets:"
	@echo "  make test      - Run test suite with pytest"
	@echo "  make install   - Install dependencies from requirements.txt"
	@echo "  make clean     - Remove generated files and cache"

test:
	pytest tests/ -v

install:
	pip install -r requirements.txt

clean:
	rm -rf __pycache__ tests/__pycache__ .pytest_cache
	rm -rf *.pyc tests/*.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
