"""
Roteamento Inteligente de Modelo (Model Router).

Classifica a complexidade do prompt, considera presença de código, sugere modelos
mais baratos quando a tarefa é simples e identifica elegibilidade para Batch API (50% off).
Trata exceções de precificação com segurança.
"""

from __future__ import annotations

import re
from typing import Optional

from promptshrink.models import ModelRoutingRecommendation
from promptshrink.cost_estimator import PRICES, estimate_cost
from promptshrink.tokenizer import count_tokens

_HIGH_REASONING_KEYWORDS = (
    "prove", "prova", "demonstre", "derive", "matemátic", "math",
    "arquitetura", "refatore", "refactor", "benchmark", "complexidade",
    "algoritmo avançado", "concorrência", "deadlock", "teorema",
)

_CHEAPER_ALTERNATIVES: dict[str, str] = {
    "gpt-4o": "gpt-4o-mini",
    "gpt-4-turbo": "gpt-4o-mini",
    "claude-3-opus": "claude-3-5-sonnet",
    "claude-3-5-sonnet": "claude-3-haiku",
    "gemini-1.5-pro": "gemini-1.5-flash",
}


def analyze_model_routing(
    text: str,
    current_model: str,
    tokens: Optional[int] = None,
) -> Optional[ModelRoutingRecommendation]:
    """
    Avalia se o modelo selecionado é exagerado para a complexidade do prompt
    e sinaliza oportunidade de Batch API (50% de desconto adicional).
    """
    target_cheaper = _CHEAPER_ALTERNATIVES.get(current_model)
    tok_count = tokens if tokens is not None else count_tokens(text, current_model).count

    text_lower = text.lower()
    has_high_reasoning = any(k in text_lower for k in _HIGH_REASONING_KEYWORDS)
    code_block_count = len(re.findall(r"```", text)) // 2
    is_very_long = tok_count > 1200

    if has_high_reasoning or (code_block_count >= 2 and tok_count > 400) or is_very_long:
        complexity = "high"
        reasoning = (
            f"O prompt requer raciocínio elevado, refatoração de múltiplos blocos de código "
            f"ou contextualização ampla. Manter '{current_model}' é recomendado."
        )
        batch_savings = 0.0
        try:
            cost_curr = estimate_cost(tok_count, current_model).cost_usd
            batch_savings = cost_curr * 0.50
        except Exception:
            pass

        return ModelRoutingRecommendation(
            suggested_model=current_model,
            current_model=current_model,
            complexity_level=complexity,
            reasoning=reasoning + " Dica: Para tarefas assíncronas, use Batch API com 50% de desconto.",
            potential_cost_savings_usd=0.0,
            percent_cheaper=0.0,
            batch_api_eligible=True,
            batch_api_savings_usd=round(batch_savings, 8),
        )

    if not target_cheaper:
        return None

    if tok_count < 80 and code_block_count == 0:
        complexity = "trivial"
        reasoning = (
            f"Prompt curto e direto ({tok_count} tokens). "
            f"O modelo '{target_cheaper}' executa com a mesma qualidade e custo até 94% menor."
        )
    elif tok_count < 400 and code_block_count <= 1:
        complexity = "low"
        reasoning = (
            f"Tarefa de baixa complexidade ({tok_count} tokens). "
            f"'{target_cheaper}' é altamente capacitado para esta instrução."
        )
    elif tok_count < 1200:
        complexity = "medium"
        reasoning = (
            f"Instrução moderada ({tok_count} tokens). "
            f"'{target_cheaper}' é suficiente e gera grande economia."
        )
    else:
        return None

    savings = 0.0
    percent = 0.0
    batch_savings = 0.0

    try:
        cost_curr = estimate_cost(tok_count, current_model).cost_usd
        cost_cheap = estimate_cost(tok_count, target_cheaper).cost_usd
        savings = cost_curr - cost_cheap
        percent = round((savings / cost_curr) * 100, 1) if cost_curr > 0 else 0.0
        batch_savings = cost_cheap * 0.50
    except Exception:
        pass

    return ModelRoutingRecommendation(
        suggested_model=target_cheaper,
        current_model=current_model,
        complexity_level=complexity,
        reasoning=reasoning,
        potential_cost_savings_usd=round(savings, 8),
        percent_cheaper=percent,
        batch_api_eligible=True,
        batch_api_savings_usd=round(batch_savings, 8),
    )
