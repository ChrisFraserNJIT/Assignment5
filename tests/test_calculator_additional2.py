from tempfile import TemporaryDirectory
from pathlib import Path
from decimal import Decimal
import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import OperationFactory
from app.exceptions import OperationError
from app.exceptions import ValidationError


def test_save_load_history():
    """Ensure history can be saved and loaded correctly in isolation."""
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        config = CalculatorConfig(base_dir=tmp_path, max_history_size=1000, auto_save=False)
        calc = Calculator(config=config)

        # Ensure history starts empty
        calc.history.clear()

        op = OperationFactory.create_operation('add')
        calc.set_operation(op)
        calc.perform_operation(1, 2)

        # Save history
        calc.save_history()
        assert config.history_file.exists()

        # Load history into a new calculator instance
        calc2 = Calculator(config=config)
        calc2.history.clear()  # start fresh
        calc2.load_history()
        assert len(calc2.history) == 1
        assert calc2.history[0].result == Decimal("3")

def test_save_load_empty_history():
    """Save/load with empty history should not fail in isolation."""
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        config = CalculatorConfig(base_dir=tmp_path, max_history_size=1000, auto_save=False)
        calc = Calculator(config=config)

        # Ensure empty history
        calc.history.clear()
        assert calc.history == []

        # Save and load should preserve empty history
        calc.save_history()
        calc.load_history()
        assert calc.history == []

def test_operation_error_on_divide_by_zero():
    """Ensure division by zero raises ValidationError."""
    config = CalculatorConfig(auto_save=False)
    calc = Calculator(config=config)
    calc.history.clear()

    op = OperationFactory.create_operation('divide')
    calc.set_operation(op)

    with pytest.raises(ValidationError):  # <- changed from OperationError
        calc.perform_operation(5, 0)

def test_basic_addition():
    config = CalculatorConfig(auto_save=False)
    calc = Calculator(config=config)
    calc.history.clear()

    op = OperationFactory.create_operation('add')
    calc.set_operation(op)

    calc.perform_operation(2, 3)
    assert calc.history[-1].result == Decimal("5")

def test_basic_subtraction():
    config = CalculatorConfig(auto_save=False)
    calc = Calculator(config=config)
    calc.history.clear()

    op = OperationFactory.create_operation('subtract')
    calc.set_operation(op)

    calc.perform_operation(5, 2)
    assert calc.history[-1].result == Decimal("3")

def test_basic_multiplication():
    config = CalculatorConfig(auto_save=False)
    calc = Calculator(config=config)
    calc.history.clear()

    op = OperationFactory.create_operation('multiply')
    calc.set_operation(op)

    calc.perform_operation(3, 4)
    assert calc.history[-1].result == Decimal("12")

def test_basic_division():
    config = CalculatorConfig(auto_save=False)
    calc = Calculator(config=config)
    calc.history.clear()

    op = OperationFactory.create_operation('divide')
    calc.set_operation(op)

    calc.perform_operation(10, 2)
    assert calc.history[-1].result == Decimal("5")
