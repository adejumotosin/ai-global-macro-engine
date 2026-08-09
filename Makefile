.PHONY: run test
run:
	uvicorn app:app --reload --port 8000
test:
	pytest -q
