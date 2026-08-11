"""
Detector de risco de Prompt Injection.

Analisa o prompt em busca de instruções maliciosas ou tentativas de jailbreak/subversão
de comportamento da IA.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_INJECTION_PATTERNS: list[tuple[str, re.Pattern, float]] = [
    ("IGNORE_INSTRUCTIONS", re.compile(r"\bignore\s+(?:(?:all|previous|prior|system)\s+)*instructions\b", re.IGNORECASE), 0.9),
    ("FORGET_SYSTEM", re.compile(r"\bforget\s+(?:(?:everything|what|all)\s+)*(?:you\s+)*(?:know|were\s+told|learned)\b", re.IGNORECASE), 0.8),
    ("ROLEPLAY_OVERRIDE", re.compile(r"\byou\s+are\s+now\s+(?:a|an)?\s*(?:unrestricted|DAN|jailbroken|evil|developer|root)\b", re.IGNORECASE), 0.95),
    ("DISREGARD_RULES", re.compile(r"\bdisregard\s+(?:(?:your|all|previous|safety)\s+)*rules\b", re.IGNORECASE), 0.85),
    ("SYSTEM_PROMPT_LEAK", re.compile(r"\b(?:print|show|display|output|reveal)\s+(?:your\s+)?(?:system\s+)?prompt\b", re.IGNORECASE), 0.7),
]


@dataclass
class InjectionCheckResult:
    risk_score: float  # 0.0 a 1.0
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    detected_threats: list[str] = field(default_factory=list)


def check_prompt_injection(text: str) -> InjectionCheckResult:
    """
    Avalia a presença de padrões de Prompt Injection.
    """
    max_score = 0.0
    threats = []

    for name, pattern, score in _INJECTION_PATTERNS:
        if pattern.search(text):
            threats.append(name)
            if score > max_score:
                max_score = score

    if max_score >= 0.8:
        level = "HIGH"
    elif max_score >= 0.5:
        level = "MEDIUM"
    else:
        level = "LOW"

    return InjectionCheckResult(risk_score=round(max_score, 2), risk_level=level, detected_threats=threats)
