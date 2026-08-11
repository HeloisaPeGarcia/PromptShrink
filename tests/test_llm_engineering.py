"""
Testes unitários para os módulos avançados de Engenharia de LLM:
- Code Stripper
- Format Optimizer
- Normalizer
- Output Budget Advisor
- Model Router
- Cache Advisor
- Language Router
"""

# pyrefly: ignore [missing-import]
import pytest
from promptshrink.code_stripper import strip_code_blocks
from promptshrink.format_optimizer import minify_formats
from promptshrink.normalizer import normalize_connectives_and_numbers
from promptshrink.output_budget import analyze_output_budget
from promptshrink.model_router import analyze_model_routing
from promptshrink.cache_advisor import analyze_prompt_caching
from promptshrink.language_router import analyze_language_optimization
from promptshrink.optimizer import optimize


class TestCodeStripper:
    def test_python_docstring_removed(self):
        text = '```python\ndef foo():\n    """Docstring aqui"""\n    return 42\n```'
        result, changed = strip_code_blocks(text)
        assert changed is True
        assert "Docstring aqui" not in result
        assert "return 42" in result

    def test_python_comments_removed(self):
        text = '```python\n# Comentário de linha\nx = 10\n```'
        result, changed = strip_code_blocks(text)
        assert changed is True
        assert "Comentário de linha" not in result

    def test_generic_code_comments_removed(self):
        text = '```js\n// Comentário JS\nconst x = 5;\n```'
        result, changed = strip_code_blocks(text)
        assert changed is True
        assert "Comentário JS" not in result
        assert "const x = 5;" in result


class TestFormatOptimizer:
    def test_json_block_minified(self):
        text = '```json\n{\n  "nome": "João",\n  "idade": 30\n}\n```'
        result, changed = minify_formats(text)
        assert changed is True
        assert '{"nome":"João","idade":30}' in result

    def test_xml_block_minified(self):
        text = '```xml\n<user>\n  <name>João</name>\n</user>\n```'
        result, changed = minify_formats(text)
        assert changed is True
        assert "<user><name>João</name></user>" in result


class TestNormalizer:
    def test_due_to_the_fact_that_normalized(self):
        text = "I failed due to the fact that it was raining."
        result, changed = normalize_connectives_and_numbers(text)
        assert changed is True
        assert "because" in result

    def test_devido_ao_fato_de_que_normalized(self):
        text = "Falhei devido ao fato de que choveu."
        result, changed = normalize_connectives_and_numbers(text)
        assert changed is True
        assert "porque" in result


class TestOutputBudgetAdvisor:
    def test_code_intent_detected(self):
        text = "Escreva uma função Python para ordenar uma lista."
        advice = analyze_output_budget(text, "gpt-4o")
        assert advice is not None
        assert advice.intent_detected == "Desenvolvimento de Código"
        assert advice.roi_multiplier > 1.0

    def test_json_intent_detected(self):
        text = "Retorne um objeto JSON com o resultado."
        advice = analyze_output_budget(text, "gpt-4o")
        assert advice is not None
        assert "Dados" in advice.intent_detected or "Estruturada" in advice.intent_detected


class TestModelRouter:
    def test_simple_prompt_recommends_cheaper_model(self):
        text = "Qual é a capital da França?"
        rec = analyze_model_routing(text, "gpt-4o")
        assert rec is not None
        assert rec.suggested_model == "gpt-4o-mini"
        assert rec.percent_cheaper > 80.0

    def test_high_reasoning_keeps_model(self):
        text = "Prove o teorema de Fermat e derive a prova matemática avançada."
        rec = analyze_model_routing(text, "gpt-4o")
        assert rec is not None
        assert rec.suggested_model == "gpt-4o"
        assert rec.batch_api_eligible is True


class TestCacheAdvisor:
    def test_short_context_not_cacheable(self):
        text = "Por favor responda X.\n\nContexto:\nDocumento curto com 10 palavras...\n\n"
        advice = analyze_prompt_caching(text, "gpt-4o")
        assert advice is not None
        assert advice.is_cacheable is False

    def test_large_context_block_is_cacheable(self):
        large_doc = "palavra " * 1200
        text = f"Por favor responda X.\n\nContexto:\n{large_doc}\n\n"
        advice = analyze_prompt_caching(text, "gpt-4o")
        assert advice is not None
        assert advice.is_cacheable is True
        assert advice.prefix_tokens >= 1024
        assert advice.break_even_requests is not None


class TestLanguageRouter:
    def test_pt_prompt_suggests_english_instruction(self):
        text = "Escreva uma função que calcula o fatorial de N."
        advice = analyze_language_optimization(text, "gpt-4o")
        assert advice is not None
        assert advice.detected_language == "pt-br"
        assert advice.english_instruction_prompt is not None
        assert "Write a function" in advice.english_instruction_prompt


class TestFullOptimizationWithInsights:
    def test_optimize_returns_all_insights(self):
        text = (
            "Olá! Eu gostaria que você pudesse, por favor, me ajudar a escrever "
            "uma função Python para ordenar uma lista.\n\n"
            "```python\n# Comentário\ndef sort_list(l):\n    return sorted(l)\n```"
        )
        res = optimize(text, model="gpt-4o", level="moderate", enable_llm_insights=True)
        assert res.metrics.tokens_saved > 0
        assert res.model_recommendation is not None
        assert res.output_budget_advice is not None
        d = res.to_dict()
        assert "model_recommendation" in d
        assert "output_budget_advice" in d
        assert "quality" in d
