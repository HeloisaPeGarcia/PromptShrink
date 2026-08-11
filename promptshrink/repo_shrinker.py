"""
Codebase Context Shrinker — promptshrink repo

Varre diretórios de projetos de código, aplica sanitização, remoção de comentários,
docstrings e minificação em cada arquivo, combinando-os em um único payload Markdown
otimizado para LLMs.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from promptshrink.code_stripper import strip_code_blocks
from promptshrink.format_optimizer import minify_formats

_IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", "build", "dist", ".idea", ".vscode"
}

_SUPPORTED_EXTS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
    ".hpp", ".go", ".rs", ".json", ".xml", ".yaml", ".yml", ".md", ".txt"
}


def shrink_codebase(
    dir_path: Path,
    output_path: Optional[Path] = None,
    max_file_size_kb: int = 500,
) -> dict[str, Any]:
    """
    Varre o repositório e gera um payload de contexto otimizado para LLMs.
    """
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Diretório não encontrado: {dir_path}")

    files_processed = 0
    total_orig_bytes = 0
    total_opt_bytes = 0
    content_blocks: list[str] = []

    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in _IGNORE_DIRS]

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in _SUPPORTED_EXTS:
                continue

            fpath = Path(root) / fname
            size_kb = fpath.stat().st_size / 1024
            if size_kb > max_file_size_kb:
                continue

            try:
                raw_text = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if not raw_text.strip():
                continue

            rel_path = fpath.relative_to(dir_path)
            orig_len = len(raw_text)

            lang = ext.lstrip(".")
            if ext in (".py", ".js", ".ts", ".c", ".cpp", ".java"):
                wrapped = f"```{lang}\n{raw_text}\n```"
                opt_text, _ = strip_code_blocks(wrapped)
            elif ext in (".json", ".xml", ".yaml", ".yml"):
                wrapped = f"```{lang}\n{raw_text}\n```"
                opt_text, _ = minify_formats(wrapped)
            else:
                opt_text = raw_text

            opt_len = len(opt_text)
            files_processed += 1
            total_orig_bytes += orig_len
            total_opt_bytes += opt_len

            content_blocks.append(f"### File: {rel_path}\n{opt_text}\n")

    final_payload = "\n".join(content_blocks)
    bytes_saved = max(0, total_orig_bytes - total_opt_bytes)
    percent_saved = (bytes_saved / total_orig_bytes * 100) if total_orig_bytes > 0 else 0.0

    if output_path:
        output_path.write_text(final_payload, encoding="utf-8")

    return {
        "files_processed": files_processed,
        "total_orig_bytes": total_orig_bytes,
        "total_opt_bytes": total_opt_bytes,
        "bytes_saved": bytes_saved,
        "percent_saved": round(percent_saved, 1),
        "payload": final_payload,
    }
