import pytest
import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.append(os.getcwd())

from src.playground.string_reverser import reverse_string

def test_reverse_string_valid_input():
    """Tests the reverse_string function with a valid string input."""
    assert reverse_string("hello") == "olleh"
    assert reverse_string("Phoenix") == "xeinhoP"
    assert reverse_string("Python 3.10") == "01.3 nohtyP"
    assert reverse_string("") == ""
    assert reverse_string(" ") == " "
    assert reverse_string("  ") == "  "
    assert reverse_string("a") == "a"
    assert reverse_string("abc") == "cba"
    assert reverse_string("!@#$%^") == "^%$#@!"


def test_reverse_string_with_spaces():
    """Tests the reverse_string function with spaces in the input."""
    assert reverse_string("hello world") == "dlrow olleh"
    assert reverse_string("  hello  ") == "  olleh  "
    assert reverse_string(" a b c ") == " c b a "


def test_reverse_string_non_string_input():
    """Tests the reverse_string function with a non-string input (integer)."""
    assert reverse_string(123) == ""
    assert reverse_string(None) == ""
    assert reverse_string(123.45) == ""
    assert reverse_string([1,2,3]) == "" # testing with a list
    assert reverse_string({"a": 1}) == "" # testing with a dict

def test_reverse_string_special_characters():
    """Tests reverse_string with special characters"""
    assert reverse_string("!@#$%^&*()") == ")*&^%$#@!"
    assert reverse_string("Hello, world!") == "!dlrow ,olleH"