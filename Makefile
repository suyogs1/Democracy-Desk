.PHONY: test build deploy run clean

test:
	pytest tests/ --cov=src --cov-report=term-missing

run:
	python -m gunicorn src.api.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080

build:
	docker build -t democracy-desk-ai .

deploy:
	gcloud run deploy democracy-desk-ai --source . --project promptwar-493105 --region us-central1 --allow-unauthenticated

lint:
	black src/ tests/
	isort src/ tests/
	flake8 src/ tests --max-line-length=120 --ignore=E203,W503

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
