"""
Testes para o módulo sanitizer (Nível 1).
"""

from promptshrink.sanitizer import sanitize


class TestNormalizeEncoding:
    def test_curly_quotes_replaced(self):
        result = sanitize("\u201cHello\u201d")
        assert '"Hello"' in result.sanitized
        assert "normalize_encoding" in result.rules_applied

    def test_em_dash_replaced(self):
        result = sanitize("foo\u2014bar")
        assert "foo--bar" in result.sanitized

    def test_non_breaking_space_replaced(self):
        result = sanitize("hello\u00a0world")
        assert "hello world" in result.sanitized

    def test_zero_width_space_removed(self):
        result = sanitize("hel\u200blo")
        assert "hello" in result.sanitized


class TestCollapseSpaces:
    def test_multiple_spaces_collapsed(self):
        result = sanitize("hello   world")
        assert "hello world" in result.sanitized
        assert "collapse_spaces" in result.rules_applied

    def test_tabs_collapsed(self):
        result = sanitize("hello\t\tworld")
        assert "hello world" in result.sanitized

    def test_code_block_indentation_preserved(self):
        text = "```python\n    def foo():\n        pass\n```"
        result = sanitize(text)
        assert "    def foo():" in result.sanitized


class TestCollapseBlankLines:
    def test_three_blank_lines_become_two(self):
        text = "line1\n\n\n\nline2"
        result = sanitize(text)
        assert "\n\n\n" not in result.sanitized
        assert "line1" in result.sanitized
        assert "line2" in result.sanitized

    def test_two_blank_lines_unchanged(self):
        text = "line1\n\nline2"
        result = sanitize(text)
        assert "line1\n\nline2" in result.sanitized


class TestTrimTrailingSpaces:
    def test_trailing_spaces_removed(self):
        text = "hello   \nworld  "
        result = sanitize(text)
        for line in result.sanitized.split("\n"):
            assert not line.endswith(" ")


class TestDeduplicateLines:
    def test_consecutive_duplicate_lines_removed(self):
        text = "faça X\nfaça X\nfaça X"
        result = sanitize(text)
        lines = [l for l in result.sanitized.split("\n") if l.strip()]
        assert lines.count("faça X") == 1
        assert "deduplicate_lines" in result.rules_applied

    def test_non_consecutive_duplicates_kept(self):
        text = "faça X\nfaça Y\nfaça X"
        result = sanitize(text)
        assert result.sanitized.count("faça X") == 2


class TestRemoveRedundantMarkdown:
    def test_empty_bold_removed(self):
        result = sanitize("antes **** depois")
        assert "****" not in result.sanitized

    def test_empty_italic_removed(self):
        result = sanitize("antes __ depois")
        assert "__" not in result.sanitized


class TestEmojiStripping:
    def test_emojis_kept_by_default(self):
        result = sanitize("hello 🔥 world")
        assert "🔥" in result.sanitized

    def test_emojis_removed_when_requested(self):
        result = sanitize("hello 🔥 world", strip_emojis=True)
        assert "🔥" not in result.sanitized
        assert "strip_emojis" in result.rules_applied


class TestStripOuterWhitespace:
    def test_leading_trailing_stripped(self):
        result = sanitize("   hello world   ")
        assert result.sanitized == "hello world"


class TestNoChanges:
    def test_clean_text_unchanged(self):
        text = "Escreva uma função Python que ordena uma lista."
        result = sanitize(text)
        assert result.sanitized == text
        assert result.rules_applied == []
        assert result.chars_removed == 0
