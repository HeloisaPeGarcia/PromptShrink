"""
Normalização de numéricos por extenso e conectivos verbosos.
Usa proteção de código para não alterar strings embutidas em código.
"""

from __future__ import annotations

import re
from promptshrink.code_fence import protect_code_blocks, restore_code_blocks

_VERBOSE_CONNECTIVES: list[tuple[re.Pattern, str]] = [
    # PT-BR
    (re.compile(r"\bdevido ao fato de que\b", re.IGNORECASE), "porque"),
    (re.compile(r"\bpor conta do fato de que\b", re.IGNORECASE), "porque"),
    (re.compile(r"\bno que diz respeito a\b", re.IGNORECASE), "sobre"),
    (re.compile(r"\bcom a finalidade de\b", re.IGNORECASE), "para"),
    (re.compile(r"\bcom o objetivo de\b", re.IGNORECASE), "para"),
    (re.compile(r"\bna medida em que\b", re.IGNORECASE), "como"),
    (re.compile(r"\blevando em consideração que\b", re.IGNORECASE), "como"),
    # EN
    (re.compile(r"\bdue to the fact that\b", re.IGNORECASE), "because"),
    (re.compile(r"\bin order to\b", re.IGNORECASE), "to"),
    (re.compile(r"\bwith the purpose of\b", re.IGNORECASE), "to"),
    (re.compile(r"\bat this point in time\b", re.IGNORECASE), "now"),
    (re.compile(r"\bin the event that\b", re.IGNORECASE), "if"),
    (re.compile(r"\bfor the purpose of\b", re.IGNORECASE), "for"),
    (re.compile(r"\bwith regard to\b", re.IGNORECASE), "about"),
    (re.compile(r"\bas well as\b", re.IGNORECASE), "and"),
]


def normalize_connectives_and_numbers(text: str) -> tuple[str, bool]:
    """
    Substitui conectivos verbosos por formas concisas e normaliza números básicos fora de blocos de código.
    """
    protected_text, code_blocks = protect_code_blocks(text)
    current = protected_text
    changed = False

    for pattern, replacement in _VERBOSE_CONNECTIVES:
        new_text = pattern.sub(replacement, current)
        if new_text != current:
            changed = True
            current = new_text

    final_text = restore_code_blocks(current, code_blocks)
    return final_text, changed
