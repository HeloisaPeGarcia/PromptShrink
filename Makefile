.PHONY: install cli api test lint fmt clean

# ─── Instalação ───────────────────────────────────────────
install:
	pip install -e ".[dev]"

install-uv:
	uv sync --all-extras

# ─── Desenvolvimento ──────────────────────────────────────
cli:
	python -m promptshrink.cli optimize --model gpt-4o --level moderate

api:
	uvicorn api.main:app --reload --port 8000

# Exemplo rápido via pipe
demo:
	@echo "Olá! Eu gostaria que você pudesse, por favor, me ajudar a escrever \
uma função Python que ordena uma lista de forma eficiente. Basicamente, \
preciso de algo simples. Obrigado!" | python -m promptshrink.cli optimize \
--model gpt-4o --level moderate --json

# ─── Qualidade ────────────────────────────────────────────
test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --tb=short --cov=promptshrink --cov=api --cov-report=term-missing

lint:
	ruff check promptshrink/ api/ tests/

fmt:
	ruff format promptshrink/ api/ tests/

# ─── Limpeza ──────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
