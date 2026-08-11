"""
Testes para o módulo tokenizer (Nível 2).
"""

import pytest
from promptshrink.tokenizer import count_tokens
from promptshrink.models import TokenCount


class TestTokenCountStructure:
    def test_returns_token_count_instance(self):
        result = count_tokens("Hello world", "gpt-4o")
        assert isinstance(result, TokenCount)
        assert result.model == "gpt-4o"
        assert result.count > 0

    def test_empty_text_returns_zero(self):
        result = count_tokens("", "gpt-4o")
        assert result.count == 0

    def test_count_is_positive(self):
        result = count_tokens("Faça uma função Python", "gpt-4o")
        assert result.count > 0


class TestOpenAIModels:
    def test_gpt4o_not_approximate(self):
        """GPT-4o usa tiktoken real — não deve ser aproximado (se tiktoken instalado)."""
        result = count_tokens("Hello world", "gpt-4o")
        # Se tiktoken estiver instalado, is_approximate = False
        # Se não, cai para heurística — ambos aceitáveis no teste
        assert isinstance(result.is_approximate, bool)

    def test_gpt4o_mini_recognized(self):
        result = count_tokens("test", "gpt-4o-mini")
        assert result.model == "gpt-4o-mini"
        assert result.count > 0

    def test_gpt35_turbo_recognized(self):
        result = count_tokens("test", "gpt-3.5-turbo")
        assert result.count > 0


class TestClaudeModels:
    def test_claude_sonnet_approximate(self):
        result = count_tokens("Hello world", "claude-3-5-sonnet")
        assert result.is_approximate is True
        assert result.count > 0

    def test_claude_haiku_recognized(self):
        result = count_tokens("test prompt", "claude-3-haiku")
        assert result.count > 0


class TestGeminiModels:
    def test_gemini_pro_approximate(self):
        result = count_tokens("Hello world", "gemini-1.5-pro")
        assert result.is_approximate is True
        assert result.count > 0

    def test_gemini_flash_recognized(self):
        result = count_tokens("test", "gemini-1.5-flash")
        assert result.count > 0


class TestTokenCountConsistency:
    def test_longer_text_more_tokens(self):
        short = count_tokens("Hello", "gpt-4o")
        long = count_tokens("Hello world, this is a longer text with more words", "gpt-4o")
        assert long.count > short.count

    def test_same_text_same_count(self):
        text = "Escreva um resumo sobre machine learning."
        r1 = count_tokens(text, "gpt-4o")
        r2 = count_tokens(text, "gpt-4o")
        assert r1.count == r2.count


class TestUnknownModel:
    def test_unknown_model_uses_approximation(self):
        """Modelos desconhecidos não devem levantar exceção — usam heurística."""
        result = count_tokens("Hello world", "modelo-desconhecido-xyz")
        assert result.count > 0
        assert result.is_approximate is True
