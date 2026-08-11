"""
Controle de Output Tokens (Budget Advisor).

Como tokens de saída custam 3-5x mais que tokens de entrada, adicionar pequenas
instruções de contenção gera alto retorno sobre o investimento (ROI).
Escala a estimativa de economia proporcionalmente ao tamanho do prompt.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

from promptshrink.models import OutputBudgetAdvice, TokenCount
from promptshrink.cost_estimator import PRICES, estimate_cost
from promptshrink.tokenizer import count_tokens


@lru_cache(maxsize=32)
def _get_constraint_tokens(constraint: str, model: str) -> int:
    return count_tokens(constraint, model).count


def analyze_output_budget(text: str, model: str, tok_before: Optional[TokenCount] = None) -> Optional[OutputBudgetAdvice]:
    """
    Analisa o prompt e sugere restrições de output com estimativa de ROI dinâmica.
    """
    text_lower = text.lower()
    tok_count = tok_before.count if tok_before is not None else count_tokens(text, model).count

    intent = None
    constraint = ""
    base_factor = 0.5

    if any(k in text_lower for k in ("código", "code", "função", "function", "script", "implement")):
        intent = "Desenvolvimento de Código"
        constraint = "Responda APENAS com o código, sem explicações nem introdução/conclusão."
        base_factor = 0.6

    elif any(k in text_lower for k in ("json", "xml", "csv", "yaml", "schema")):
        intent = "Saída Estruturada / Dados"
        constraint = "Retorne APENAS o objeto de dados bruto, sem formatação markdown ou conversa."
        base_factor = 0.4

    elif any(k in text_lower for k in ("resuma", "resumo", "summarize", "summary", "síntese")):
        intent = "Sumarização / Resumo"
        constraint = "Seja o mais conciso possível. Máximo 3 tópicos diretos."
        base_factor = 0.7

    elif any(k in text_lower for k in ("explique", "explain", "como funciona", "how it works", "oque é", "what is")):
        intent = "Explicação / Resposta a Dúvida"
        constraint = "Responda de forma direta e concisa em no máximo 2 parágrafos."
        base_factor = 0.5

    if not intent:
        intent = "Instrução Geral"
        constraint = "Seja conciso. Evite saudações e conclusões óbvias."
        base_factor = 0.3

    if any(c in text_lower for c in ("apenas", "only", "conciso", "concise", "sem introdução", "no intro")):
        return None

    # Economia dinâmica baseada no tamanho do prompt (mínimo 60 tokens, máximo 600 tokens)
    est_output_saved = min(max(60, int(tok_count * base_factor)), 600)

    tokens_added = _get_constraint_tokens(constraint, model)

    price_info = PRICES.get(model, {"input": 2.50, "output": 10.00})
    cost_prompt_added = (tokens_added / 1_000_000) * price_info["input"]
    cost_output_saved = (est_output_saved / 1_000_000) * price_info["output"]
    net_savings = cost_output_saved - cost_prompt_added

    roi = round(cost_output_saved / cost_prompt_added, 1) if cost_prompt_added > 0 else 1.0

    return OutputBudgetAdvice(
        intent_detected=intent,
        suggested_constraint=constraint,
        prompt_tokens_added=tokens_added,
        est_output_tokens_saved=est_output_saved,
        net_cost_savings_usd=round(net_savings, 8),
        roi_multiplier=roi,
    )
