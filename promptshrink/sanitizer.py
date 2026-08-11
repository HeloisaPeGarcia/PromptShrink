"""
Nível 1 — Sanitização determinística.

Pipeline de limpeza aplicado em sequência. Cada regra é independente e
rastreável; o caller recebe a lista de regras que foram disparadas.
Usa proteção unificada de blocos de código.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from promptshrink.models import SanitizeResult
from promptshrink.code_fence import protect_code_blocks, restore_code_blocks

# ---------------------------------------------------------------------------
# Mapeamentos de substituição
# ---------------------------------------------------------------------------

_QUOTE_MAP: dict[str, str] = {
    "\u2018": "'",  # '
    "\u2019": "'",  # '
    "\u201c": '"',  # "
    "\u201d": '"',  # "
    "\u201a": "'",  # ‚
    "\u201e": '"',  # „
    "\u2039": "'",  # ‹
    "\u203a": "'",  # ›
    "\u00ab": '"',  # «
    "\u00bb": '"',  # »
}

_DASH_MAP: dict[str, str] = {
    "\u2013": "-",  # –
    "\u2014": "--",  # —
    "\u2012": "-",  # ‒
}

_INVISIBLE_SPACES: tuple[str, ...] = (
    "\u00a0",  # non-breaking space
    "\u200b",  # zero-width space
    "\u200c",  # zero-width non-joiner
    "\u200d",  # zero-width joiner
    "\u2060",  # word joiner
    "\ufeff",  # BOM
    "\u00ad",  # soft hyphen
)

_DECORATIVE_EMOJI_PATTERN = re.compile(
    r"[\U0001f300-\U0001f5ff"
    r"\U0001f600-\U0001f64f"
    r"\U0001f680-\U0001f6ff"
    r"\U0001f700-\U0001f77f"
    r"\U0001f900-\U0001f9ff"
    r"\U0001fa00-\U0001fa6f"
    r"\U0001fa70-\U0001faff"
    r"\u24c2-\u1f251"
    r"]+",
    flags=re.UNICODE,
)

_BOLD_EMPTY = re.compile(r"\*\*\s*\*\*")
_ITALIC_EMPTY = re.compile(r"_\s*_")
_TRIPLE_BACKTICK_BLANK = re.compile(r"```\s*```")


def _normalize_encoding(text: str) -> tuple[str, bool]:
    """Normaliza aspas tipográficas, traços, espaços invisíveis."""
    changed = False
    for src, dst in {**_QUOTE_MAP, **_DASH_MAP}.items():
        if src in text:
            text = text.replace(src, dst)
            changed = True
    for ch in _INVISIBLE_SPACES:
        if ch in text:
            text = text.replace(ch, " " if ch != "\u200b" else "")
            changed = True
    normalized = unicodedata.normalize("NFC", text)
    if normalized != text:
        changed = True
    return normalized, changed


def _remove_control_characters(text: str) -> tuple[str, bool]:
    """Remove caracteres de controle (exceto \\n, \\t, \\r)."""
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return cleaned, cleaned != text


def _collapse_spaces(text: str) -> tuple[str, bool]:
    """Colapsa múltiplos espaços/tabs em um único espaço."""
    collapsed = re.sub(r"[ \t]+", " ", text)
    return collapsed, collapsed != text


def _collapse_blank_lines(text: str) -> tuple[str, bool]:
    """Reduz 3+ linhas em branco consecutivas a 2."""
    cleaned = re.sub(r"\n{3,}", "\n\n", text)
    return cleaned, cleaned != text


def _trim_line_trailing_spaces(text: str) -> tuple[str, bool]:
    """Remove espaços em branco ao final de cada linha."""
    lines = text.split("\n")
    stripped = [line.rstrip() for line in lines]
    changed = stripped != lines
    return "\n".join(stripped), changed


def _remove_decorative_emojis(text: str, strip_emojis: bool = False) -> tuple[str, bool]:
    """Remove emojis decorativos se solicitado."""
    if not strip_emojis:
        return text, False
    cleaned = _DECORATIVE_EMOJI_PATTERN.sub("", text)
    cleaned = re.sub(r"  +", " ", cleaned)
    return cleaned, cleaned != text


def _remove_redundant_markdown(text: str) -> tuple[str, bool]:
    """Remove bold/itálico vazio e backticks triplos vazios."""
    changed = False
    for pattern in (_BOLD_EMPTY, _ITALIC_EMPTY, _TRIPLE_BACKTICK_BLANK):
        new_text = pattern.sub("", text)
        if new_text != text:
            changed = True
        text = new_text
    return text, changed


def _deduplicate_lines(text: str) -> tuple[str, bool]:
    """Remove linhas/parágrafos consecutivos idênticos."""
    lines = text.split("\n")
    result: list[str] = []
    prev: str | None = None
    changed = False

    for line in lines:
        stripped = line.strip()
        if stripped and stripped == prev:
            changed = True
            continue
        result.append(line)
        prev = stripped if stripped else None

    return "\n".join(result), changed


def _strip_outer_whitespace(text: str) -> tuple[str, bool]:
    """Remove espaços no início e no fim do texto inteiro."""
    stripped = text.strip()
    return stripped, stripped != text


def sanitize(text: str, strip_emojis: bool = False) -> SanitizeResult:
    """
    Executa o pipeline completo de sanitização determinística com proteção de código.
    """
    # Protege blocos de código
    protected_text, code_blocks = protect_code_blocks(text)
    current = protected_text
    applied: list[str] = []

    steps: list[tuple[str, callable]] = [
        ("normalize_encoding", lambda t: _normalize_encoding(t)),
        ("remove_control_characters", lambda t: _remove_control_characters(t)),
        ("collapse_spaces", lambda t: _collapse_spaces(t)),
        ("trim_trailing_spaces", lambda t: _trim_line_trailing_spaces(t)),
        ("collapse_blank_lines", lambda t: _collapse_blank_lines(t)),
        ("remove_redundant_markdown", lambda t: _remove_redundant_markdown(t)),
        ("deduplicate_lines", lambda t: _deduplicate_lines(t)),
        ("strip_emojis", lambda t: _remove_decorative_emojis(t, strip_emojis=strip_emojis)),
        ("strip_outer_whitespace", lambda t: _strip_outer_whitespace(t)),
    ]

    for name, fn in steps:
        result, changed = fn(current)
        if changed:
            applied.append(name)
        current = result

    # Restaura blocos de código
    sanitized_final = restore_code_blocks(current, code_blocks)

    return SanitizeResult(original=text, sanitized=sanitized_final, rules_applied=applied)
