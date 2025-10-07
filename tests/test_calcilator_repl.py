# tests/test_calculator_repl.py

import pytest
from unittest.mock import patch
from decimal import Decimal
from app.calculator_repl import calculator_repl
from app.exceptions import ValidationError, OperationError

def test_calculator_repl_exit_immediately():
    with patch("builtins.input", side_effect=["exit"]), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list]
        assert any("Goodbye" in text for text in printed_texts)

def test_calculator_repl_help_and_unknown():
    inputs = ["help", "foobar", "exit"]
    with patch("builtins.input", side_effect=inputs), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list]
        assert any("Available commands" in text for text in printed_texts)
        assert any("Unknown command" in text for text in printed_texts)

def test_calculator_repl_arithmetic_cancel_and_error():
    inputs = ["add", "cancel", "add", "one", "2", "exit"]
    with patch("builtins.input", side_effect=inputs), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list]
        assert any("Operation cancelled" in text for text in printed_texts)
        assert any("Error" in text for text in printed_texts)

def test_calculator_repl_undo_redo_clear_history():
    inputs = ["undo", "redo", "clear", "exit"]
    with patch("builtins.input", side_effect=inputs), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list]
        assert any("Nothing to undo" in text or "Operation undone" in text for text in printed_texts)
        assert any("Nothing to redo" in text or "Operation redone" in text for text in printed_texts)
        assert any("History cleared" in text for text in printed_texts)

def test_calculator_repl_save_load():
    inputs = ["save", "load", "exit"]
    with patch("builtins.input", side_effect=inputs), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list]
        assert any("History saved" in text or "Error saving" in text for text in printed_texts)
        assert any("History loaded" in text or "Error loading" in text for text in printed_texts)

@pytest.mark.parametrize("command,a,b,expected", [
    ("add", "3", "2", Decimal("5")),
    ("subtract", "5", "2", Decimal("3")),
    ("multiply", "3", "4", Decimal("12")),
    ("divide", "8", "2", Decimal("4")),
    ("power", "2", "3", Decimal("8")),
    ("root", "9", "2", Decimal("3")),
])
def test_calculator_repl_arithmetic_operations(command, a, b, expected):
    inputs = [command, a, b, "exit"]
    with patch("builtins.input", side_effect=inputs), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list if args]
        result_lines = [line for line in printed_texts if "Result" in line]
        assert any(str(expected) in line for line in result_lines)

def test_calculator_repl_cancel_second_operand():
    inputs = ["add", "3", "cancel", "exit"]
    with patch("builtins.input", side_effect=inputs), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list]
        assert any("Operation cancelled" in text for text in printed_texts)

def test_calculator_repl_invalid_second_operand():
    inputs = ["add", "3", "xyz", "exit"]
    with patch("builtins.input", side_effect=inputs), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list]
        assert any("Error" in text for text in printed_texts)

def test_calculator_repl_eof_error(monkeypatch):
    def eof(*args, **kwargs):
        raise EOFError
    with patch("builtins.input", side_effect=eof), \
         patch("builtins.print") as mock_print:
        calculator_repl()
        printed_texts = [args[0] for args, _ in mock_print.call_args_list]
        assert any("Input terminated" in text for text in printed_texts)
