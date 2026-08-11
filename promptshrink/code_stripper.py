"""
Remoção de ruído e comentários em blocos de código embutidos.

Analisa blocos demarcados com ```lang ... ``` e remove docstrings, comentários,
espaços e linhas em branco não-funcionais com segurança sintática.
Suporta tags de linguagens variadas (C++, C#, JS, TS, Python, etc.) e maiúsculas/minúsculas.
"""

from __future__ import annotations

import io
import re
import tokenize


def _strip_python_comments_and_docstrings(code: str) -> str:
    """
    Remove docstrings e comentários de código Python de forma segura.
    Usa o tokenizer nativo do Python para evitar alterar strings ou f-strings.
    """
    try:
        tokens = tokenize.generate_tokens(io.StringIO(code).readline)
        out = []

        for toktype, tokval, _, _, _ in tokens:
            if toktype == tokenize.COMMENT:
                if "type:" in tokval or "noqa" in tokval:
                    out.append(tokval)
                continue
            
            if toktype == tokenize.STRING:
                if len(out) > 0 and out[-1] in ("\n", "    ", "\t", ""):
                    if tokval.startswith('"""') or tokval.startswith("'''"):
                        continue

            out.append(tokval)

        cleaned = tokenize.untokenize(out)
        lines = [line.rstrip() for line in cleaned.splitlines()]
        filtered = []
        prev_blank = False
        for line in lines:
            if not line.strip():
                if prev_blank:
                    continue
                prev_blank = True
            else:
                prev_blank = False
            filtered.append(line)
        return "\n".join(filtered)
    except Exception:
        lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") and not ("type:" in stripped or "noqa" in stripped):
                continue
            lines.append(line.rstrip())
        return "\n".join(lines)


def _strip_generic_code(code: str) -> str:
    """Remove comentários // e /* */ em linguagens tipo C/JS/TS/Java/CSS/SQL."""
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)

    lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("-- "):
            continue
        lines.append(line.rstrip())

    result = []
    prev_blank = False
    for line in lines:
        if not line.strip():
            if prev_blank:
                continue
            prev_blank = True
        else:
            prev_blank = False
        result.append(line)

    return "\n".join(result)


def strip_code_blocks(text: str) -> tuple[str, bool]:
    """
    Identifica blocos de código markdown e aplica minificação de comentários/docstrings.
    Suporta tags como python, Python, c++, c#, js, typescript, etc.
    """
    pattern = re.compile(r"```([a-zA-Z0-9_+#\-]*)\s*\n([\s\S]*?)(?:```|\Z)")
    changed = False

    def replace_block(match: re.Match) -> str:
        nonlocal changed
        raw_lang = match.group(1)
        lang = raw_lang.strip().lower()
        code = match.group(2)

        if lang in ("python", "py"):
            cleaned = _strip_python_comments_and_docstrings(code)
        elif lang in ("javascript", "js", "typescript", "ts", "java", "cpp", "c++", "c", "c#", "csharp", "css", "sql", "go"):
            cleaned = _strip_generic_code(code)
        else:
            cleaned = code

        if cleaned.strip() != code.strip():
            changed = True
        return f"```{raw_lang}\n{cleaned.strip()}\n```"

    result = pattern.sub(replace_block, text)
    return result, changed
