"""
Prompt Caching Advisor & Reorderer.

Reorganiza o prompt colocando instruções fixas, contexto e documentos no início,
aproveitando a funcionalidade de Cache de Prefixo das APIs (Anthropic, OpenAI, Gemini).
Valida limite mínimo de 1024 tokens e calcula taxas específicas de desconto e break-even por provedor.
"""

from __future__ import annotations

import re
from typing import Optional

from promptshrink.models import CacheAdvice, TokenCount
from promptshrink.cost_estimator import PRICES, estimate_cost
from promptshrink.tokenizer import count_tokens

_CONTEXT_PATTERNS = (
    r"(\bcontexto:\s*[\s\S]*?(?:\n\n|\Z))",
    r"(\bcontext:\s*[\s\S]*?(?:\n\n|\Z))",
    r"(\bdocumento:\s*[\s\S]*?(?:\n\n|\Z))",
    r"(\breferência:\s*[\s\S]*?(?:\n\n|\Z))",
    r"(```[\s\S]*?```(?:\n\n|\Z))",
)

MIN_CACHE_PREFIX_TOKENS = 1024  # Mínimo exigido por Anthropic e OpenAI


def _get_provider_cache_params(model: str) -> tuple[float, float, str]:
    """
    Retorna (fator_custo_leitura, fator_custo_escrita, nome_provedor)
    """
    model_lower = model.lower()
    if "claude" in model_lower:
        return 0.10, 1.25, "Anthropic"
    elif "gpt" in model_lower:
        return 0.50, 1.00, "OpenAI"
    else:
        return 0.25, 1.00, "Google Gemini"


def analyze_prompt_caching(text: str, model: str, tok_before: Optional[TokenCount] = None) -> Optional[CacheAdvice]:
    """
    Identifica partes estáveis do prompt que poderiam estar em cache e reordena o prompt.
    Valida mínimo de 1024 tokens e calcula taxas de desconto exatas e break-even por provedor.
    """
    blocks_found = []
    current_text = text

    for pat in _CONTEXT_PATTERNS:
        matches = list(re.finditer(pat, current_text, re.IGNORECASE))
        for m in matches:
            blocks_found.append(m.group(1))

    if not blocks_found:
        return CacheAdvice(
            is_cacheable=False,
            reordered_prompt=text,
            prefix_tokens=0,
            estimated_cache_savings_usd=0.0,
            explanation="O prompt não possui um bloco separado de contexto/documentos fixos evidente.",
        )

    fixed_context = "".join(blocks_found).strip()

    variable_instruction = text
    for b in blocks_found:
        variable_instruction = variable_instruction.replace(b, "")
    variable_instruction = variable_instruction.strip()

    reordered = f"[SYSTEM / FIXED CONTEXT]\n{fixed_context}\n\n[USER TASK]\n{variable_instruction}"
    prefix_tokens = count_tokens(fixed_context, model).count

    read_factor, write_factor, provider_name = _get_provider_cache_params(model)

    if prefix_tokens < MIN_CACHE_PREFIX_TOKENS:
        return CacheAdvice(
            is_cacheable=False,
            reordered_prompt=reordered,
            prefix_tokens=prefix_tokens,
            estimated_cache_savings_usd=0.0,
            break_even_requests=None,
            explanation=(
                f"O prefixo fixo possui {prefix_tokens} tokens, mas o provedor ({provider_name}) "
                f"exige no mínimo {MIN_CACHE_PREFIX_TOKENS} tokens para ativar o desconto de Prefix Caching."
            ),
        )

    price_info = PRICES.get(model, {"input": 2.50})
    normal_cost = (prefix_tokens / 1_000_000) * price_info["input"]
    cached_read_cost = normal_cost * read_factor
    savings_per_cached_call = normal_cost - cached_read_cost

    if write_factor > 1.0:
        write_overhead = normal_cost * (write_factor - 1.0)
        break_even = 1 + int(write_overhead / savings_per_cached_call) + 1
    else:
        break_even = 2

    pct_off = int((1.0 - read_factor) * 100)

    return CacheAdvice(
        is_cacheable=True,
        reordered_prompt=reordered,
        prefix_tokens=prefix_tokens,
        estimated_cache_savings_usd=round(savings_per_cached_call, 8),
        break_even_requests=break_even,
        explanation=(
            f"Estruturado em prefixo cacheável ({prefix_tokens} tokens fixos). "
            f"O provedor {provider_name} concede {pct_off}% de desconto a partir da 2ª chamada "
            f"(Ponto de equilíbrio: {break_even} requisições)."
        ),
    )
