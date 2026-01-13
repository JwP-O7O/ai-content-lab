import pytest
import sys
import os

sys.path.append(os.getcwd())
from src.playground.string_reverser import reverse_string
from loguru import logger

class TestStringReverser:
    def test_empty_string(self):
        assert reverse_string("") == ""

    def test_single_character_string(self):
        assert reverse_string("a") == "a"

    def test_simple_string(self):
        assert reverse_string("hello") == "olleh"

    def test_string_with_spaces(self):
        assert reverse_string("hello world") == "dlrow olleh"

    def test_string_with_special_characters(self):
        assert reverse_string("!@#$%^") == "^%$#@!"

    def test_string_with_mixed_case(self):
        assert reverse_string("HeLlO") == "OlLeH"

    def test_string_with_unicode(self):
        assert reverse_string("你好世界") == "界世好你"

    def test_none_input(self):
        assert reverse_string(None) == ""

    def test_integer_input(self):
        assert reverse_string(123) == ""

    def test_list_input(self):
        assert reverse_string([1, 2, 3]) == ""

    def test_float_input(self):
        assert reverse_string(3.14) == ""