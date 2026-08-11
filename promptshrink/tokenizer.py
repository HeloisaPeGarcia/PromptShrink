"""
Nível 2 — Contagem de tokens por modelo com lru_cache explícito.

Usa tiktoken para modelos OpenAI com cache LRU.
Para Claude e Gemini, usa aproximação baseada em tiktoken com fator de correção e rotulagem de confiança.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

from promptshrink.models import TokenCount

_TIKTOKEN_ENCODINGS: dict[str, str] = {
    "gpt-4o":            "o200k_base",
    "gpt-4o-mini":       "o200k_base",
    "gpt-4-turbo":       "cl100k_base",
    "gpt-3.5-turbo":     "cl100k_base",
}

_APPROXIMATION_FACTOR: dict[str, float] = {
    "claude-3-5-sonnet": 1.05,
    "claude-3-haiku":    1.05,
    "claude-3-opus":     1.05,
    "gemini-1.5-pro":    1.10,
    "gemini-1.5-flash":  1.10,
    "gemini-2.0-flash":  1.10,
}

_PT_STOPWORDS = {"de", "da", "do", "que", "em", "não", "uma", "para", "com", "os", "as", "um", "por"}


@lru_cache(maxsize=16)
def _get_tiktoken_encoding(encoding_name: str):
    """Obtém o objeto encoding de tiktoken com cache LRU explícito."""
    import tiktoken  # type: ignore
    return tiktoken.get_encoding(encoding_name)


def _count_with_tiktoken(text: str, encoding_name: str) -> int:
    """Conta tokens usando tiktoken de forma otimizada."""
    enc = _get_tiktoken_encoding(encoding_name)
    return len(enc.encode(text))


def _count_heuristic(text: str) -> int:
    """
    Heurística adaptativa baseada em palavras e densidade de idioma quando tiktoken não está disponível.
    Aproximação: ~1.3 (EN) / ~1.45 (PT-BR) tokens por palavra.
    """
    words = re.findall(r"\S+", text)
    if not words:
        return 0
    pt_count = sum(1 for w in words if w.lower() in _PT_STOPWORDS)
    factor = 1.45 if (pt_count / len(words)) > 0.08 else 1.3
    return max(1, int(len(words) * factor))


def count_tokens(text: str, model: str) -> TokenCount:
    """
    Conta tokens no texto para o modelo especificado.
    """
    if not text:
        return TokenCount(model=model, count=0, encoding_used="none", is_approximate=False, confidence="exact")

    encoding_name = _TIKTOKEN_ENCODINGS.get(model)
    if encoding_name:
        try:
            count = _count_with_tiktoken(text, encoding_name)
            return TokenCount(
                model=model,
                count=count,
                encoding_used=encoding_name,
                is_approximate=False,
                confidence="exact",
            )
        except ImportError:
            count = _count_heuristic(text)
            return TokenCount(
                model=model,
                count=count,
                encoding_used="heuristic_word_count",
                is_approximate=True,
                confidence="rough",
            )

    correction = _APPROXIMATION_FACTOR.get(model, 1.0)
    try:
        base_count = _count_with_tiktoken(text, "cl100k_base")
        count = max(1, round(base_count * correction))
        return TokenCount(
            model=model,
            count=count,
            encoding_used=f"cl100k_base×{correction}",
            is_approximate=True,
            confidence="estimated",
        )
    except ImportError:
        count = max(1, round(_count_heuristic(text) * correction))
        return TokenCount(
            model=model,
            count=count,
            encoding_used="heuristic_word_count",
            is_approximate=True,
            confidence="rough",
        )
