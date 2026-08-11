"""
Compressão de Histórico de Conversa (Chat History Compressor).

Permite otimizar arrays de mensagens de chat (OpenAI / Anthropic schema),
preservando as últimas N mensagens intactas e comprimindo as anteriores.
Usa contagem direta de tokens para mensagens mantidas sem overhead.
"""

from __future__ import annotations

from typing import Any
from promptshrink.optimizer import optimize
from promptshrink.models import CompressionLevel
from promptshrink.tokenizer import count_tokens


def compress_chat_history(
    messages: list[dict[str, Any]],
    model: str = "gpt-4o",
    keep_last_n: int = 3,
    level: CompressionLevel = CompressionLevel.LIGHT,
) -> dict[str, Any]:
    """
    Comprime o histórico de mensagens mantendo as últimas N mensagens intocadas.
    """
    if not messages:
        return {"messages": [], "total_tokens_before": 0, "total_tokens_after": 0, "tokens_saved": 0, "percent_saved": 0.0}

    total_tokens_before = 0
    total_tokens_after = 0
    optimized_messages = []

    cutoff_index = max(0, len(messages) - keep_last_n)

    for idx, msg in enumerate(messages):
        content = msg.get("content", "")
        role = msg.get("role", "user")

        if not isinstance(content, str) or not content.strip():
            optimized_messages.append(msg)
            continue

        # Mensagens recentes ou system role mantém-se intactas
        if idx >= cutoff_index or role == "system":
            optimized_messages.append(msg)
            toks = count_tokens(content, model).count
            total_tokens_before += toks
            total_tokens_after += toks
        else:
            res = optimize(content, model=model, level=level, enable_llm_insights=False)
            total_tokens_before += res.metrics.tokens_before
            total_tokens_after += res.metrics.tokens_after
            optimized_messages.append({"role": role, "content": res.optimized_text})

    tokens_saved = total_tokens_before - total_tokens_after

    return {
        "messages": optimized_messages,
        "total_tokens_before": total_tokens_before,
        "total_tokens_after": total_tokens_after,
        "tokens_saved": max(0, tokens_saved),
        "percent_saved": round((max(0, tokens_saved) / total_tokens_before) * 100, 2) if total_tokens_before > 0 else 0.0,
    }
