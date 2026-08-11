"""
Calculadora e Simulador de Custos de LLM — promptshrink calc

Calcula e simula o impacto financeiro mensal de otimização de prompts em escala.
"""

from __future__ import annotations

from typing import Any
from promptshrink.cost_estimator import get_model_price, PRICES


def simulate_monthly_savings(
    calls_per_month: int = 100000,
    avg_input_tokens: int = 800,
    avg_output_tokens: int = 400,
    model: str = "gpt-4o",
    avg_reduction_percent: float = 35.0,
) -> dict[str, Any]:
    """
    Simula os custos mensais atuais vs. custos otimizados com o PromptShrink.
    """
    price_info = get_model_price(model)
    in_price = price_info.input_per_1m
    out_price = price_info.output_per_1m

    # Custo sem otimização
    orig_input_tokens_m = (calls_per_month * avg_input_tokens) / 1e6
    orig_output_tokens_m = (calls_per_month * avg_output_tokens) / 1e6

    cost_input_orig = orig_input_tokens_m * in_price
    cost_output_orig = orig_output_tokens_m * out_price
    total_cost_orig = cost_input_orig + cost_output_orig

    # Custo com PromptShrink
    opt_input_tokens = int(avg_input_tokens * (1.0 - (avg_reduction_percent / 100.0)))
    opt_input_tokens_m = (calls_per_month * opt_input_tokens) / 1e6

    cost_input_opt = opt_input_tokens_m * in_price
    cost_output_opt = cost_output_orig  # Mantém conservador

    total_cost_opt = cost_input_opt + cost_output_opt
    savings_usd = max(0.0, total_cost_orig - total_cost_opt)
    savings_percent = (savings_usd / total_cost_orig * 100) if total_cost_orig > 0 else 0.0

    # Simulação com Downgrade de Modelo (Model Router)
    cheaper_model = "gpt-4o-mini" if "gpt-4" in model else "claude-3-haiku"
    cheaper_price = get_model_price(cheaper_model)
    cost_with_router = (opt_input_tokens_m * cheaper_price.input_per_1m) + (orig_output_tokens_m * cheaper_price.output_per_1m)
    savings_with_router_usd = max(0.0, total_cost_orig - cost_with_router)

    return {
        "model": model,
        "calls_per_month": calls_per_month,
        "avg_input_tokens_orig": avg_input_tokens,
        "avg_input_tokens_opt": opt_input_tokens,
        "monthly_cost_orig_usd": round(total_cost_orig, 2),
        "monthly_cost_opt_usd": round(total_cost_opt, 2),
        "monthly_savings_usd": round(savings_usd, 2),
        "savings_percent": round(savings_percent, 1),
        "suggested_cheaper_model": cheaper_model,
        "monthly_cost_with_router_usd": round(cost_with_router, 2),
        "monthly_savings_with_router_usd": round(savings_with_router_usd, 2),
    }
