.PHONY: all install test clean

all: install

install:
	pip install -e .

test:
	python -m pytest tests/

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete