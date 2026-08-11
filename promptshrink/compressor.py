"""
Nível 3 — Compressão semântica baseada em heurísticas.

Regras determinísticas para remover cortesias, frases verbosas e redundâncias
linguísticas em português (PT-BR) e inglês. Sem chamada a LLM.
Protege blocos de código markdown contra alterações indevidas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from promptshrink.models import CompressResult, CompressionLevel
from promptshrink.code_fence import protect_code_blocks, restore_code_blocks


@dataclass
class Rule:
    name: str
    level: CompressionLevel  # Nível mínimo para ativar
    pattern: re.Pattern
    replacement: str
    description: str


def _r(pattern: str, flags: int = re.IGNORECASE) -> re.Pattern:
    return re.compile(pattern, flags)


RULES: list[Rule] = [
    # LIGHT — Cortesias explícitas
    Rule(
        name="remove_greetings_pt",
        level=CompressionLevel.LIGHT,
        pattern=_r(
            r"\b(olá|oi|hey|e aí|bom dia|boa tarde|boa noite)[,!.]?\s*"
            r"(tudo bem\??|como vai\??|espero que esteja bem[.!]?)?\s*",
        ),
        replacement="",
        description="Remove saudações PT-BR",
    ),
    Rule(
        name="remove_greetings_en",
        level=CompressionLevel.LIGHT,
        pattern=_r(
            r"\b(hi|hello|hey|good morning|good afternoon|good evening)[,!.]?\s*"
            r"(hope you('re| are) (doing well|well)[.!]?)?\s*",
        ),
        replacement="",
        description="Remove greetings EN",
    ),
    Rule(
        name="remove_closings_pt",
        level=CompressionLevel.LIGHT,
        pattern=_r(
            r"\s*(obrigad[oa]|muito obrigad[oa]|agradeço[. !]*|"
            r"desde já agradeço[. !]*|aguardo retorno[. !]*|"
            r"att[,.]?\s+\w+|atenciosamente[,.]?\s*\w*)[. !]*$",
        ),
        replacement="",
        description="Remove fechamentos PT-BR",
    ),
    Rule(
        name="remove_closings_en",
        level=CompressionLevel.LIGHT,
        pattern=_r(
            r"\s*(thanks?[. !]*|thank you[. !]*|best regards?[,.]?\s*\w*|"
            r"sincerely[,.]?\s*\w*|cheers[. !]*)[. !]*$",
        ),
        replacement="",
        description="Remove closings EN",
    ),

    # MODERATE — Frases verbosas
    Rule(
        name="please_simplify_pt",
        level=CompressionLevel.MODERATE,
        pattern=_r(
            r"(eu gostaria que você (pudesse|possa),?\s*(por favor,?\s*)?)"
            r"|(por favor,\s*(você poderia|poderia você|você pode|pode você)\s*)"
            r"|(você poderia,?\s*(por favor,?\s*)?)"
            r"|(se não for (muito\s+)?incômodo,?\s*)"
            r"|(se (possível|puder),?\s*)"
            r"|(por gentileza,?\s*)",
        ),
        replacement="",
        description="Remove verbosidade de pedidos PT-BR",
    ),
    Rule(
        name="please_simplify_en",
        level=CompressionLevel.MODERATE,
        pattern=_r(
            r"(i would (like|appreciate it) if you (could|would),?\s*(please,?\s*)?)"
            r"|(could you (please\s*)?(possibly\s*)?)"
            r"|(would you (mind\s*)?(please\s*)?)"
            r"|(if (it's|it is) not too much trouble,?\s*)"
            r"|(if (possible|you can),?\s*)"
            r"|(please,?\s*)",
        ),
        replacement="",
        description="Remove verbose request forms EN",
    ),
    Rule(
        name="filler_phrases_pt",
        level=CompressionLevel.MODERATE,
        pattern=_r(
            r"\b(basicamente|simplesmente|literalmente|essencialmente|"
            r"na verdade|de fato|é claro que|claro que|obviamente|"
            r"como (eu\s+)?mencionei anteriormente|conforme (dito|mencionado) anteriormente|"
            r"como (você|vc) (sabe|pode ver)|como pode (se\s+)?observar)\b,?\s*",
        ),
        replacement="",
        description="Remove palavras de enchimento PT-BR",
    ),
    Rule(
        name="filler_phrases_en",
        level=CompressionLevel.MODERATE,
        pattern=_r(
            r"\b(basically|simply|literally|essentially|actually|"
            r"in fact|of course|obviously|clearly|"
            r"as (i\s+)?mentioned (earlier|before|previously)|"
            r"as (you )?can see|as (you )?know)\b,?\s*",
        ),
        replacement="",
        description="Remove filler words EN",
    ),

    # AGGRESSIVE — Compressão mais profunda
    Rule(
        name="hedge_words_pt",
        level=CompressionLevel.AGGRESSIVE,
        pattern=_r(
            r"\b(talvez|possivelmente|provavelmente|quem sabe|"
            r"de alguma forma|de certa forma|de certo modo|"
            r"um tanto|meio que|mais ou menos)\b,?\s*",
        ),
        replacement="",
        description="Remove palavras hedge PT-BR",
    ),
    Rule(
        name="hedge_words_en",
        level=CompressionLevel.AGGRESSIVE,
        pattern=_r(
            r"\b(maybe|perhaps|possibly|probably|somehow|"
            r"kind of|sort of|somewhat|more or less|"
            r"in some ways|in a way)\b,?\s*",
        ),
        replacement="",
        description="Remove hedge words EN",
    ),
    Rule(
        name="verbose_question_pt",
        level=CompressionLevel.AGGRESSIVE,
        pattern=_r(
            r"\b(você (consegue|pode|poderia|saberia) me (dizer|explicar|mostrar|informar))\s+",
        ),
        replacement="",
        description="Simplifica perguntas verbosas PT-BR",
    ),
    Rule(
        name="verbose_question_en",
        level=CompressionLevel.AGGRESSIVE,
        pattern=_r(
            r"\b(can you (tell|explain|show|help) me|"
            r"could you (tell|explain|show|help) me|"
            r"would you (be able to|mind)\s+)(explain|tell|show|help)?\s*",
        ),
        replacement="",
        description="Simplifica perguntas verbosas EN",
    ),
]


_LEVEL_ORDER = [
    CompressionLevel.NONE,
    CompressionLevel.LIGHT,
    CompressionLevel.MODERATE,
    CompressionLevel.AGGRESSIVE,
]


def _level_index(level: CompressionLevel) -> int:
    return _LEVEL_ORDER.index(level)


def _rules_for_level(level: CompressionLevel) -> list[Rule]:
    target_idx = _level_index(level)
    return [r for r in RULES if _level_index(r.level) <= target_idx]


def _cleanup_after_compression(text: str) -> str:
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"^\s*\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"^,\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"(?<!\w)\.{2,}(?!\w)", ".", text)
    return text.strip()


def compress(text: str, level: CompressionLevel = CompressionLevel.LIGHT) -> CompressResult:
    """
    Aplica compressão semântica heurística protegendo blocos de código.
    """
    if level == CompressionLevel.NONE:
        return CompressResult(
            original=text,
            compressed=text,
            level=level,
            rules_applied=[],
        )

    protected_text, code_blocks = protect_code_blocks(text)
    current = protected_text
    applied: list[str] = []

    for rule in _rules_for_level(level):
        new_text = rule.pattern.sub(rule.replacement, current)
        if new_text != current:
            applied.append(rule.name)
        current = new_text

    current = _cleanup_after_compression(current)
    final_text = restore_code_blocks(current, code_blocks)

    return CompressResult(
        original=text,
        compressed=final_text,
        level=level,
        rules_applied=applied,
    )
