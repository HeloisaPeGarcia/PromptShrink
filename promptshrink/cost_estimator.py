"""
Tabela de preços dos modelos e estimativa de custo em USD.

Preços em dólares por 1 milhão de tokens (input/output).
Carrega preços customizados de `prices.json` se disponível localmente.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from promptshrink.models import CostEstimate, ModelTarget
from promptshrink.logger import get_logger

logger = get_logger("promptshrink.cost_estimator")

PRICES: dict[str, dict[str, float]] = {
    # OpenAI
    "gpt-4o":           {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":      {"input": 0.15,  "output": 0.60},
    "gpt-4-turbo":      {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo":    {"input": 0.50,  "output": 1.50},
    # Anthropic
    "claude-3-5-sonnet":{"input": 3.00,  "output": 15.00},
    "claude-3-haiku":   {"input": 0.25,  "output": 1.25},
    "claude-3-opus":    {"input": 15.00, "output": 75.00},
    # Google
    "gemini-1.5-pro":   {"input": 1.25,  "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.0-flash": {"input": 0.10,  "output": 0.40},
}


def load_custom_prices(custom_file: Path | str = "prices.json") -> None:
    """Tenta carregar um arquivo prices.json customizado e mesclar com a tabela padrão."""
    path = Path(custom_file)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict) and "input" in v:
                        is_overwrite = k in PRICES
                        PRICES[k] = {"input": float(v["input"]), "output": float(v.get("output", v["input"] * 4))}
                        if is_overwrite:
                            logger.info("Preço customizado sobrescreveu modelo '%s'.", k)
                        else:
                            logger.info("Modelo customizado adicionado '%s'.", k)
        except Exception as exc:
            logger.warning("Falha ao carregar preços customizados de %s: %s", path, exc)


load_custom_prices()


def get_price(model: str) -> dict[str, float] | None:
    """Retorna o dicionário de preços para o modelo, ou None se não encontrado."""
    return PRICES.get(model)


def estimate_cost(tokens: int, model: str, direction: str = "input") -> CostEstimate:
    """
    Estima o custo em USD para um número de tokens.
    """
    price_info = PRICES.get(model)
    if price_info is None:
        raise ValueError(
            f"Modelo '{model}' não encontrado na tabela de preços. "
            f"Modelos disponíveis: {list(PRICES.keys())}"
        )

    price_per_million = price_info.get(direction, price_info["input"])
    cost = (tokens / 1_000_000) * price_per_million

    return CostEstimate(
        model=model,
        tokens=tokens,
        cost_usd=round(cost, 8),
        price_per_million=price_per_million,
    )


def list_models() -> list[dict]:
    """Retorna lista de modelos com preços formatados."""
    return [
        {
            "model": model,
            "input_per_1m_usd": prices["input"],
            "output_per_1m_usd": prices["output"],
        }
        for model, prices in PRICES.items()
    ]
