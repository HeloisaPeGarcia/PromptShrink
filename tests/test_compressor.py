"""
Testes para o módulo compressor (Nível 3 — heurísticas semânticas).
"""

from promptshrink.compressor import compress
from promptshrink.models import CompressionLevel


class TestLevelNone:
    def test_none_level_unchanged(self):
        text = "Olá! Eu gostaria que você pudesse, por favor, me ajudar."
        result = compress(text, level=CompressionLevel.NONE)
        assert result.compressed == text
        assert result.rules_applied == []


class TestLightLevel:
    def test_pt_greeting_removed(self):
        text = "Olá! Preciso de ajuda com Python."
        result = compress(text, level=CompressionLevel.LIGHT)
        assert "Olá" not in result.compressed
        assert "Python" in result.compressed

    def test_en_greeting_removed(self):
        text = "Hello! I need help with Python."
        result = compress(text, level=CompressionLevel.LIGHT)
        assert "Hello" not in result.compressed
        assert "Python" in result.compressed

    def test_pt_closing_removed(self):
        text = "Escreva uma função. Obrigado!"
        result = compress(text, level=CompressionLevel.LIGHT)
        assert "Obrigado" not in result.compressed
        assert "função" in result.compressed

    def test_en_closing_removed(self):
        text = "Write a function. Thanks!"
        result = compress(text, level=CompressionLevel.LIGHT)
        assert "Thanks" not in result.compressed
        assert "function" in result.compressed

    def test_rules_tracked(self):
        text = "Olá! Escreva código. Obrigado!"
        result = compress(text, level=CompressionLevel.LIGHT)
        assert len(result.rules_applied) > 0


class TestModerateLevel:
    def test_please_phrase_pt_removed(self):
        text = "Por favor, você poderia escrever uma função?"
        result = compress(text, level=CompressionLevel.MODERATE)
        assert "por favor" not in result.compressed.lower()
        assert "função" in result.compressed

    def test_gostaria_phrase_removed(self):
        text = "Eu gostaria que você pudesse me ajudar com o código."
        result = compress(text, level=CompressionLevel.MODERATE)
        assert "gostaria" not in result.compressed.lower()

    def test_filler_word_pt_removed(self):
        text = "Basicamente, você precisa criar uma função."
        result = compress(text, level=CompressionLevel.MODERATE)
        assert "basicamente" not in result.compressed.lower()
        assert "função" in result.compressed

    def test_filler_word_en_removed(self):
        text = "Basically, you need to create a function."
        result = compress(text, level=CompressionLevel.MODERATE)
        assert "basically" not in result.compressed.lower()
        assert "function" in result.compressed

    def test_as_mentioned_pt_removed(self):
        text = "Como mencionei anteriormente, o código precisa ser eficiente."
        result = compress(text, level=CompressionLevel.MODERATE)
        assert "mencionei anteriormente" not in result.compressed.lower()

    def test_as_mentioned_en_removed(self):
        text = "As mentioned previously, the code needs to be efficient."
        result = compress(text, level=CompressionLevel.MODERATE)
        assert "as mentioned" not in result.compressed.lower()

    def test_includes_light_rules(self):
        """Moderate deve também aplicar regras de light."""
        text = "Olá! Por gentileza, escreva uma função."
        result = compress(text, level=CompressionLevel.MODERATE)
        assert "Olá" not in result.compressed
        assert "por gentileza" not in result.compressed.lower()


class TestAggressiveLevel:
    def test_hedge_words_pt_removed(self):
        text = "Talvez você possa criar uma função."
        result = compress(text, level=CompressionLevel.AGGRESSIVE)
        assert "talvez" not in result.compressed.lower()

    def test_hedge_words_en_removed(self):
        text = "Maybe you can create a function."
        result = compress(text, level=CompressionLevel.AGGRESSIVE)
        assert "maybe" not in result.compressed.lower()

    def test_includes_moderate_rules(self):
        """Aggressive deve incluir regras de moderate e light."""
        text = "Olá! Basicamente, talvez você pudesse me ajudar."
        result = compress(text, level=CompressionLevel.AGGRESSIVE)
        assert "Olá" not in result.compressed
        assert "basicamente" not in result.compressed.lower()
        assert "talvez" not in result.compressed.lower()


class TestSemanticPreservation:
    def test_code_block_preserved(self):
        """Blocos de código não devem ser alterados."""
        text = "```python\ndef hello():\n    print('hello')\n```"
        result = compress(text, level=CompressionLevel.AGGRESSIVE)
        assert "def hello():" in result.compressed
        assert "print('hello')" in result.compressed

    def test_content_meaning_preserved_light(self):
        """Em nível light, apenas cortesias devem ser removidas."""
        text = "Olá! Implemente uma função que calcula o fatorial de N."
        result = compress(text, level=CompressionLevel.LIGHT)
        assert "fatorial" in result.compressed
        assert "função" in result.compressed
        assert "N" in result.compressed


class TestCleanup:
    def test_no_double_spaces_after_compression(self):
        text = "Por gentileza, faça isso."
        result = compress(text, level=CompressionLevel.MODERATE)
        assert "  " not in result.compressed

    def test_result_stripped(self):
        text = "  Olá! Faça isso.  "
        result = compress(text, level=CompressionLevel.LIGHT)
        assert result.compressed == result.compressed.strip()
