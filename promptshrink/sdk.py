"""
SDK Wrapper do PromptShrink para integração transparente com clientes OpenAI e Anthropic.

Uso:
    from promptshrink.sdk import PromptShrinkClient
    client = PromptShrinkClient(model="gpt-4o")
    res = client.optimize("Olá! Eu gostaria que você pudesse...")
"""

from __future__ import annotations

from typing import Any, Optional
from promptshrink.optimizer import optimize
from promptshrink.models import CompressionLevel


class PromptShrinkClient:
    """
    Cliente Python leve e transparente para otimização de prompts.
    """

    def __init__(
        self,
        default_model: str = "gpt-4o",
        default_level: CompressionLevel = CompressionLevel.LIGHT,
        mask_pii: bool = False,
    ):
        self.default_model = default_model
        self.default_level = default_level
        self.mask_pii = mask_pii

    def optimize_text(
        self,
        text: str,
        model: Optional[str] = None,
        level: Optional[CompressionLevel] = None,
    ) -> str:
        """
        Otimiza um texto brutos e retorna a versão comprimida.
        """
        target_model = model or self.default_model
        target_level = level or self.default_level
        result = optimize(text, model=target_model, level=target_level)
        return result.optimized_text

    def wrap_chat_messages(
        self,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Otimiza um array de mensagens de chat (OpenAI / Anthropic format).
        """
        target_model = model or self.default_model
        optimized_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if isinstance(content, str) and content.strip():
                opt_content = self.optimize_text(content, model=target_model)
                optimized_messages.append({"role": role, "content": opt_content})
            else:
                optimized_messages.append(msg)

        return optimized_messages
