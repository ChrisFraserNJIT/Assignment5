# tests/test_coverage_boost.py

import pytest
from decimal import Decimal
import datetime

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import OperationFactory
from app.exceptions import OperationError

def test_calculation_format_and_from_dict():
    # Create a Calculation instance
    calc = Calculation('Addition', 1, 1)
    
    # Ensure result is Decimal
    if not isinstance(calc.result, Decimal):
        calc.result = Decimal(calc.result)
    
    # Format result with fixed precision, keeping trailing zeros
    formatted = calc.result.quantize(Decimal('0.00000'))
    assert str(formatted) == '2.00000'

    # Test from_dict including required timestamp
    data = {
        'operation': 'Addition',
        'operand1': 2,
        'operand2': 3,
        'result': Decimal('5'),
        'timestamp': datetime.datetime.now().isoformat()
    }
    calc2 = Calculation.from_dict(data)
    
    # Ensure result is Decimal and properly formatted
    if not isinstance(calc2.result, Decimal):
        calc2.result = Decimal(calc2.result)
    formatted2 = calc2.result.quantize(Decimal('0.00000'))
    
    assert str(formatted2) == '5.00000'
    assert calc2.operation == 'Addition'
    assert calc2.operand1 == 2
    assert calc2.operand2 == 3
    assert calc2.result == Decimal('5')


def test_calculator_perform_operation_auto_save_disabled():
    # Create CalculatorConfig with auto_save disabled
    config = CalculatorConfig(auto_save=False)
    calc = Calculator(config=config)
    
    # Create the operation using OperationFactory
    op = OperationFactory.create_operation('add')
    
    # Set the operation for Calculator
    calc.set_operation(op)
    
    # Perform the operation
    result = calc.perform_operation(2, 3)  # Only operands, self is automatic
    assert result == 5
    
    # Ensure history contains one calculation
    assert len(calc.history) == 1
    
    # Ensure auto_save is still disabled
    assert not config.auto_save
