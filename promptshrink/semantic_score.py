"""
Cálculo de retenção de fidelidade semântica (Semantic Similarity Score).

Avalia o grau de preservação do significado entre o texto original e o texto otimizado
utilizando frequência de palavras e n-gramas (bigramas) em vez de simples sets.
"""

from __future__ import annotations

import re
from collections import Counter


def _extract_tokens_and_bigrams(text: str) -> list[str]:
    words = re.findall(r"\b\w{2,}\b", text.lower())
    bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)]
    return words + bigrams


def calculate_semantic_similarity(original: str, optimized: str) -> float:
    """
    Calcula uma pontuação de similaridade semântica realista entre 0.0 e 1.0.

    Returns:
        float: Score de fidelidade semântica (ex: 0.95 = 95% de retenção).
    """
    if not original or not optimized:
        return 1.0

    orig_tokens = _extract_tokens_and_bigrams(original)
    opt_tokens = _extract_tokens_and_bigrams(optimized)

    if not orig_tokens:
        return 1.0

    orig_counts = Counter(orig_tokens)
    opt_counts = Counter(opt_tokens)

    intersection_count = sum(min(count, opt_counts[token]) for token, count in orig_counts.items())
    total_orig_count = len(orig_tokens)

    recall = intersection_count / total_orig_count if total_orig_count > 0 else 1.0

    return round(max(0.0, min(1.0, recall)), 2)
