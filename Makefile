clean:
	rm -rf .ipynb_checkpoints
	rm -rf .pytest_cache
	rm -rf **/.ipynb_checkpoints
	rm -rf **/.pytest_cache
	rm -rf **/__pycache__

install:
	python -m pip install -e ".[dev]"

deploy-docs:
	mkdocs gh-deploy
