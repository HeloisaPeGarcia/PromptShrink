"""
Roteamento e Otimização de Idioma (Language Router).

Detecta idioma não-inglês (ex: Português) e avalia o ganho de densidade
de tokens ao converter a parte instrucional do prompt para Inglês.
Protege blocos de código markdown contra traduções acidentais.
"""

from __future__ import annotations

import re
from typing import Optional

from promptshrink.models import LanguageAdvice, TokenCount
from promptshrink.tokenizer import count_tokens
from promptshrink.code_fence import protect_code_blocks, restore_code_blocks

_INSTRUCTION_TRANSLATION_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bescreva uma função que\b", re.IGNORECASE), "Write a function to"),
    (re.compile(r"\bimplemente uma solução para\b", re.IGNORECASE), "Implement a solution for"),
    (re.compile(r"\bcrie um script em\b", re.IGNORECASE), "Create a script in"),
    (re.compile(r"\bexplique como funciona\b", re.IGNORECASE), "Explain how works"),
    (re.compile(r"\bresuma o seguinte texto:\b", re.IGNORECASE), "Summarize the following text:"),
    (re.compile(r"\bfaça um resumo sobre\b", re.IGNORECASE), "Summarize"),
    (re.compile(r"\bcorrija os erros no código abaixo:\b", re.IGNORECASE), "Fix errors in the code below:"),
    (re.compile(r"\bconverta o seguinte json para\b", re.IGNORECASE), "Convert the following JSON to"),
    (re.compile(r"\bresponda em português\b", re.IGNORECASE), "Reply in Portuguese"),
    (re.compile(r"\banalise o seguinte código:\b", re.IGNORECASE), "Analyze the following code:"),
    (re.compile(r"\bverifique se há erros em\b", re.IGNORECASE), "Check for errors in"),
    (re.compile(r"\bquais são as melhores práticas para\b", re.IGNORECASE), "What are best practices for"),
    (re.compile(r"\bcomo posso otimizar\b", re.IGNORECASE), "How to optimize"),
    (re.compile(r"\btraduza para o português:\b", re.IGNORECASE), "Translate to Portuguese:"),
    (re.compile(r"\bextraia as informações principais de\b", re.IGNORECASE), "Extract key information from"),
    (re.compile(r"\bmonte uma tabela com\b", re.IGNORECASE), "Create a table with"),
    (re.compile(r"\bgerar um relatório sobre\b", re.IGNORECASE), "Generate a report on"),
    (re.compile(r"\bquais são os prós e contras de\b", re.IGNORECASE), "Pros and cons of"),
    (re.compile(r"\bcompare as diferenças entre\b", re.IGNORECASE), "Compare differences between"),
    (re.compile(r"\brefatore o código abaixo:\b", re.IGNORECASE), "Refactor code below:"),
    (re.compile(r"\bescreva um teste unitário para\b", re.IGNORECASE), "Write a unit test for"),
    (re.compile(r"\bquais são os passos para\b", re.IGNORECASE), "Steps to"),
]

_PT_INDICATORS = ("escreva", "função", "crie", "explique", "responda", "código", "ajudar", "português", "exemplo", "resumo", "analise")
_EXISTING_REPLY_IN_PT_PATTERN = re.compile(r"\b(reply in portuguese|respond in portuguese|responda em português|resposta em pt|pt-br)\b", re.IGNORECASE)


def analyze_language_optimization(
    text: str,
    model: str,
    tok_before: Optional[TokenCount] = None,
) -> Optional[LanguageAdvice]:
    """
    Avalia se o prompt está em português e calcula a redução de tokens caso a instrução seja em inglês.
    """
    text_lower = text.lower()
    is_pt = any(k in text_lower for k in _PT_INDICATORS)

    orig_tokens = tok_before.count if tok_before is not None else count_tokens(text, model).count

    if not is_pt:
        return LanguageAdvice(
            detected_language="en",
            english_instruction_prompt=None,
            original_tokens=orig_tokens,
            translated_tokens=orig_tokens,
            tokens_saved=0,
            percent_saved=0.0,
        )

    protected_text, code_blocks = protect_code_blocks(text)
    translated_text = protected_text

    for pattern, replacement in _INSTRUCTION_TRANSLATION_MAP:
        translated_text = pattern.sub(replacement, translated_text)

    has_existing_instruction = bool(_EXISTING_REPLY_IN_PT_PATTERN.search(translated_text)) or bool(_EXISTING_REPLY_IN_PT_PATTERN.search(text))
    if not has_existing_instruction:
        translated_text += "\nNote: Reply in Portuguese."

    final_translated_text = restore_code_blocks(translated_text, code_blocks)

    trans_tokens = count_tokens(final_translated_text, model).count
    tokens_saved = orig_tokens - trans_tokens
    percent_saved = round((tokens_saved / orig_tokens) * 100, 1) if orig_tokens > 0 else 0.0

    return LanguageAdvice(
        detected_language="pt-br",
        english_instruction_prompt=final_translated_text if tokens_saved > 0 else None,
        original_tokens=orig_tokens,
        translated_tokens=trans_tokens,
        tokens_saved=max(0, tokens_saved),
        percent_saved=max(0.0, percent_saved),
    )
