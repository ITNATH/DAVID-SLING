.PHONY: install boot test lint typecheck audit run-sim run-api backtest clean

install:
	pip install -e . && pip install -r requirements-dev.txt

boot:
	python main.py --mode sim --host 0.0.0.0 --port 8000

run-sim:
	python run.py live --sim

run-api:
	python run.py api --host 0.0.0.0 --port 8000

backtest:
	python run.py backtest --days 30

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src

audit:
	python scripts/architecture_audit.py

clean:
	rm -rf storage data/ticks data/ohlcv data/orderbook .pytest_cache
