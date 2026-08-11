"""
Testes para o utilitário de proteção de blocos de código code_fence.py e refinamentos do fluxo.
"""

from promptshrink.code_fence import protect_code_blocks, restore_code_blocks
from promptshrink.sanitizer import sanitize
from promptshrink.compressor import compress
from promptshrink.normalizer import normalize_connectives_and_numbers
from promptshrink.code_stripper import strip_code_blocks
from promptshrink.semantic_score import calculate_semantic_similarity
from promptshrink.cache_advisor import analyze_prompt_caching


def test_code_fence_extraction_and_restoration():
    text = 'Texto normal\n```python\nx = "due to the fact that"\n# comentario\n```\nFim'
    protected, blocks = protect_code_blocks(text)
    assert "__PROMPTSHRINK_CODE_BLOCK_0__" in protected
    assert len(blocks) == 1
    restored = restore_code_blocks(protected, blocks)
    assert restored == text


def test_normalizer_does_not_touch_code_strings():
    text = '```python\nmsg = "due to the fact that"\n```'
    norm, changed = normalize_connectives_and_numbers(text)
    assert "because" not in norm
    assert "due to the fact that" in norm


def test_compressor_does_not_touch_code_identifiers():
    text = '```javascript\nfunction simply() { return true; }\n```'
    comp = compress(text, level="aggressive")
    assert "function simply()" in comp.compressed


def test_code_stripper_uppercase_and_cpp_tags():
    text = '```Python\n# Comentario\nx = 10\n```\n```c++\n// CPP comment\nint y = 5;\n```'
    stripped, changed = strip_code_blocks(text)
    assert changed is True
    assert "Comentario" not in stripped
    assert "CPP comment" not in stripped
    assert "int y = 5;" in stripped


def test_semantic_similarity_proportional_score():
    orig = "Esta é uma instrução extremamente longa com diversas palavras repetidas e detalhes descritivos complexos para teste."
    opt = "Esta é uma instrução para teste."
    score = calculate_semantic_similarity(orig, opt)
    assert 0.0 < score < 0.90  # Reflete redução realista


def test_cache_advisor_eof_ending():
    doc = "documento " * 1200
    text = f"Contexto:\n{doc}"
    advice = analyze_prompt_caching(text, "gpt-4o")
    assert advice is not None
    assert advice.is_cacheable is True
