"""
Pre-analisador de compressibilidade de prompt (Compressibility Score).

Avalia o potencial de redução de um prompt antes da execução do pipeline.
"""

from __future__ import annotations

import re
from typing import Any


def analyze_compressibility(text: str) -> dict[str, Any]:
    """
    Retorna uma avaliação rápida do potencial de compressão (0.0 a 1.0) e potenciais ganchos.
    """
    if not text or not text.strip():
        return {"compressibility_score": 0.0, "potential_savings_category": "NONE", "reasons": []}

    words = re.findall(r"\w+", text.lower())
    total_words = len(words)
    if total_words == 0:
        return {"compressibility_score": 0.0, "potential_savings_category": "NONE", "reasons": []}

    reasons = []
    score_points = 0.0

    # 1. Cortesias
    greetings = ("olá", "oi", "bom dia", "boa tarde", "obrigado", "por favor", "please", "thanks", "hello")
    g_count = sum(1 for w in words if w in greetings)
    if g_count > 0:
        score_points += min(0.3, g_count * 0.1)
        reasons.append(f"Detectadas {g_count} palavras de cortesia/saudação.")

    # 2. Conectivos verbosos
    verbose = ("basicamente", "simplesmente", "literalmente", "basically", "actually", "due to the fact that")
    text_lower = text.lower()
    v_count = sum(1 for v in verbose if v in text_lower)
    if v_count > 0:
        score_points += min(0.3, v_count * 0.1)
        reasons.append("Detectadas expressões verbosas ou filler words.")

    # 3. Código com comentários
    if "```" in text and ("#" in text or "//" in text or "/*" in text):
        score_points += 0.3
        reasons.append("Blocos de código contêm comentários removíveis.")

    # 4. Formatação JSON/XML expansiva
    if "```json" in text or "```xml" in text:
        score_points += 0.2
        reasons.append("Formatos estruturados embutidos são minificáveis.")

    final_score = round(min(1.0, score_points), 2)
    if final_score >= 0.6:
        category = "HIGH"
    elif final_score >= 0.3:
        category = "MEDIUM"
    else:
        category = "LOW"

    return {
        "compressibility_score": final_score,
        "potential_savings_category": category,
        "reasons": reasons,
    }
