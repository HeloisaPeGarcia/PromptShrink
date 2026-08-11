"""
Otimizador e minificador de formatos estruturados (JSON, XML, YAML).
Protege texto de prosa com code_fence durante a minificação inline.
"""

from __future__ import annotations

import json
import re

from promptshrink.code_fence import protect_code_blocks, restore_code_blocks


def _minify_json(json_str: str) -> str:
    """Minifica string JSON removendo indentação e espaços desnecessários."""
    try:
        data = json.loads(json_str)
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    except Exception:
        return json_str


def _minify_xml(xml_str: str) -> str:
    """Minifica XML/HTML básico removendo espaços e quebras entre tags."""
    cleaned = re.sub(r"<!--[\s\S]*?-->", "", xml_str)
    cleaned = re.sub(r">\s+<", "><", cleaned)
    return cleaned.strip()


def minify_formats(text: str) -> tuple[str, bool]:
    """
    Minifica blocos JSON/XML ou JSON inline em prompts.

    Returns:
        tuple[str, bool]: (texto_minificado, se_houve_alteração)
    """
    changed = False

    # 1. Blocos de código json explicitos
    json_block_pattern = re.compile(r"```json\n([\s\S]*?)```", re.IGNORECASE)

    def replace_json_block(m: re.Match) -> str:
        nonlocal changed
        content = m.group(1)
        minified = _minify_json(content)
        if minified != content:
            changed = True
        return f"```json\n{minified}\n```"

    text = json_block_pattern.sub(replace_json_block, text)

    # 2. Blocos de código xml / html explicitos
    xml_block_pattern = re.compile(r"```(xml|html)\n([\s\S]*?)```", re.IGNORECASE)

    def replace_xml_block(m: re.Match) -> str:
        nonlocal changed
        lang = m.group(1)
        content = m.group(2)
        minified = _minify_xml(content)
        if minified != content:
            changed = True
        return f"```{lang}\n{minified}\n```"

    text = xml_block_pattern.sub(replace_xml_block, text)

    # 3. Inline JSON em prosa (protegendo blocos de código já processados)
    protected_text, code_blocks = protect_code_blocks(text)
    inline_json_pattern = re.compile(r"(\{[\s\n]*\"[^\"]+\"\s*:[\s\S]*?\})")

    def replace_inline_json(m: re.Match) -> str:
        nonlocal changed
        candidate = m.group(1)
        if "\n" in candidate:
            minified = _minify_json(candidate)
            if minified != candidate:
                changed = True
                return minified
        return candidate

    protected_text = inline_json_pattern.sub(replace_inline_json, protected_text)
    text = restore_code_blocks(protected_text, code_blocks)

    return text, changed
