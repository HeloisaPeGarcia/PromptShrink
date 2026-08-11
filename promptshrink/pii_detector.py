"""
Detecção e Máscara de PII (Personally Identifiable Information).

Identifica e substitui dados pessoais como CPF, E-mail, Telefone, CNPJ e Cartão de Crédito
por tokens neutros preservando a estrutura semântica.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_PII_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"), "[PESSOA_CPF]"),
    ("CNPJ", re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"), "[EMPRESA_CNPJ]"),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[CONTATO_EMAIL]"),
    ("TELEFONE", re.compile(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-\s]?\d{4}\b"), "[CONTATO_TELEFONE]"),
    ("CARTAO_CREDITO", re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[DADO_CARTAO]"),
]


@dataclass
class PIIMaskResult:
    text: str
    masked_data: dict[str, str] = field(default_factory=dict)
    pii_found_count: int = 0


def mask_pii(text: str) -> PIIMaskResult:
    """
    Substitui informações de PII por placeholders neutros.

    Returns:
        PIIMaskResult com texto mascarado e dicionário de correspondências para desmascaramento.
    """
    current = text
    masked: dict[str, str] = {}
    count = 0

    for pii_type, pattern, placeholder_prefix in _PII_PATTERNS:
        matches = list(pattern.finditer(current))
        for idx, match in enumerate(matches):
            val = match.group(0)
            placeholder = f"{placeholder_prefix[:-1]}_{idx+1}]"
            current = current.replace(val, placeholder, 1)
            masked[placeholder] = val
            count += 1

    return PIIMaskResult(text=current, masked_data=masked, pii_found_count=count)


def unmask_pii(masked_text: str, masked_data: dict[str, str]) -> str:
    """Restaura as informações originais mascaradas."""
    result = masked_text
    for placeholder, val in masked_data.items():
        result = result.replace(placeholder, val)
    return result
