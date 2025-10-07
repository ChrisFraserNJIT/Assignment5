import pytest
from decimal import Decimal
from unittest.mock import patch
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import ValidationError, OperationError
from app.operations import OperationFactory
from tempfile import TemporaryDirectory
from pathlib import Path
from app import calculator_repl  # import the REPL for testing

@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        config = CalculatorConfig(base_dir=Path(temp_dir))
        yield Calculator(config=config)

# Test undo with empty stack
def test_undo_empty(calculator):
    assert not calculator.undo()

# Test redo with empty stack
def test_redo_empty(calculator):
    assert not calculator.redo()

# Test perform_operation raises OperationError when operation fails
def test_perform_operation_no_operation(calculator):
    with pytest.raises(OperationError):
        calculator.perform_operation(1, 2)

# Test ValidationError path
def test_perform_operation_validation_error(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    with patch('app.calculator.InputValidator.validate_number', side_effect=ValidationError("Invalid")):
        with pytest.raises(ValidationError):
            calculator.perform_operation(1, 2)

# Test CalculatorMemento to/from dict
def test_memento_serialization(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    memento = CalculatorMemento(calculator.history)
    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)
    assert restored.history[0].result == Decimal('5')


def test_redo_without_undo():
    calc = Calculator()
    op = OperationFactory.create_operation('add')
    calc.set_operation(op)
    calc.perform_operation(2, 3)

    # Clear undo and redo stacks to simulate edge case
    calc.undo_stack.clear()
    calc.redo_stack.clear()

    # Attempt redo — should not raise an exception
    try:
        calc.redo()
    except Exception:
        pytest.fail("Redo raised an exception on empty redo stack")

    # Verify redo stack is still empty
    assert calc.redo_stack == []

    # Verify history did not change after redo attempt
    assert calc.history[-1].result == Decimal("5")


# ------------------- REPL Tests -------------------

def test_repl_exit(tmp_path):
    """Test the 'exit' command triggers save and exits cleanly."""
    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)

    with patch('builtins.input', side_effect=['exit']), \
         patch('builtins.print') as mock_print, \
         patch.object(calc, 'save_history') as mock_save, \
         patch('app.calculator_repl.Calculator', return_value=calc):
        calculator_repl.calculator_repl()

    mock_save.assert_called_once()
    printed = [args[0] for args, _ in mock_print.call_args_list]
    assert any("Goodbye!" in line for line in printed)


def test_repl_help_and_unknown_command():
    """Test 'help' output and unknown command handling."""
    calc = Calculator()
    inputs = ['help', 'foobar', 'exit']
    with patch('builtins.input', side_effect=inputs), \
         patch('builtins.print') as mock_print, \
         patch('app.calculator_repl.Calculator', return_value=calc):
        calculator_repl.calculator_repl()

    printed = [args[0] for args, _ in mock_print.call_args_list]
    assert any("Available commands:" in line for line in printed)
    assert any("Unknown command: 'foobar'" in line for line in printed)


def test_repl_arithmetic_operations():
    """Test basic arithmetic commands in the REPL."""
    calc = Calculator()
    inputs = ['add', '2', '3', 'exit']
    with patch('builtins.input', side_effect=inputs), \
         patch('builtins.print') as mock_print, \
         patch('app.calculator_repl.Calculator', return_value=calc):
        calculator_repl.calculator_repl()

    printed = [args[0] for args, _ in mock_print.call_args_list]
    assert any("Result: 5" in line for line in printed)


def test_repl_undo_redo_clear_history():
    """Test undo, redo, clear, and history commands in REPL."""
    calc = Calculator()
    op = OperationFactory.create_operation('add')
    calc.set_operation(op)
    calc.perform_operation(1, 1)

    inputs = ['undo', 'redo', 'clear', 'history', 'exit']
    with patch('builtins.input', side_effect=inputs), \
         patch('builtins.print') as mock_print, \
         patch('app.calculator_repl.Calculator', return_value=calc):
        calculator_repl.calculator_repl()

    printed = [args[0] for args, _ in mock_print.call_args_list]
    assert any("Operation undone" in line for line in printed)
    assert any("Operation redone" in line for line in printed)
    assert any("History cleared" in line or "No calculations in history" in line for line in printed)


def test_repl_save_load(tmp_path):
    """Test 'save' and 'load' commands in REPL."""
    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config=config)
    op = OperationFactory.create_operation('add')
    calc.set_operation(op)
    calc.perform_operation(2, 3)

    inputs = ['save', 'load', 'exit']
    with patch('builtins.input', side_effect=inputs), \
         patch('builtins.print') as mock_print, \
         patch('app.calculator_repl.Calculator', return_value=calc):
        calculator_repl.calculator_repl()

    printed = [args[0] for args, _ in mock_print.call_args_list]
    assert any("History saved successfully" in line for line in printed)
    assert any("History loaded successfully" in line for line in printed)
