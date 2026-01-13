import pytest
import sys
import os

sys.path.append(os.getcwd())  # Add current working directory to sys.path
from src.playground.string_reverser import reverse_string


class TestStringReverser:
    def test_empty_string(self):
        assert reverse_string("") == ""

    def test_simple_string(self):
        assert reverse_string("abc") == "cba"

    def test_string_with_spaces(self):
        assert reverse_string("hello world") == "dlrow olleh"

    def test_string_with_special_characters(self):
        assert reverse_string("!@#$%^") == "^%$#@!"

    def test_string_with_unicode(self):
        assert reverse_string("你好世界") == "界世好你"  # Example using Chinese characters

    def test_string_with_mixed_case(self):
        assert reverse_string("HeLlO") == "OlLeH"

    def test_non_string_input(self):
        with pytest.raises(TypeError):
            reverse_string(123)

    def test_none_input(self):
        with pytest.raises(TypeError):
            reverse_string(None)

    def test_long_string(self):
        long_string = "a" * 1000
        reversed_long_string = reverse_string(long_string)
        assert reversed_long_string == "a" * 1000  # Ensure the long string is correctly reversed.

    def test_string_with_leading_and_trailing_spaces(self):
        assert reverse_string("  abc  ") == "  cba  " # Check that leading/trailing spaces are preserved