"""
Utilitário para extração e proteção de blocos de código markdown.

Garante que transformações de texto (sanitização, compressão, normalização, tradução)
não alterem ou corrompam trechos de código embutidos.
Usa um delimitador seguro (@@PROMPTSHRINK_CODE_BLOCK_N@@) que não conflita com regras de markdown.
"""

from __future__ import annotations

import re

# Match blocos ```lang ... ```
_CODE_BLOCK_PATTERN = re.compile(r"(```[^\n]*\n[\s\S]*?```)")


def protect_code_blocks(text: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Substitui blocos de código por placeholders únicos imunes a regras de markdown.

    Returns:
        tuple[str, list[tuple[str, str]]]: (texto_com_placeholders, lista_de_(placeholder, bloco_original))
    """
    placeholders: list[tuple[str, str]] = []
    
    def replacer(match: re.Match) -> str:
        idx = len(placeholders)
        placeholder = f"@@PROMPTSHRINK_CODE_BLOCK_{idx}@@"
        block = match.group(1)
        placeholders.append((placeholder, block))
        return placeholder

    protected_text = _CODE_BLOCK_PATTERN.sub(replacer, text)
    return protected_text, placeholders


def restore_code_blocks(text: str, placeholders: list[tuple[str, str]]) -> str:
    """
    Restaura os blocos de código originais em seus respectivos placeholders.
    """
    restored = text
    for placeholder, original_block in placeholders:
        restored = restored.replace(placeholder, original_block)
    return restored
