from __future__ import annotations

import pytest

from app.domain.formula import FormulaError, evaluate_formula
from app.domain.rules import evaluate_condition


def test_formula_evaluates_approved_expression() -> None:
    result = evaluate_formula(
        "feeder_length_ft * conductor_count * waste_factor",
        {"feeder_length_ft": 125, "conductor_count": 4, "waste_factor": 1.1},
    )
    assert result == 550


def test_formula_rejects_unsafe_expression() -> None:
    with pytest.raises(FormulaError):
        evaluate_formula("__import__('os').system('date')", {})


def test_condition_operators() -> None:
    params = {"conduit_type": "RIGID", "service_size_amps": 600, "tags": "ats"}
    assert evaluate_condition(
        {"field": "conduit_type", "operator": "equals", "value": "RIGID"}, params
    )
    assert not evaluate_condition(
        {"field": "conduit_type", "operator": "not_equals", "value": "RIGID"}, params
    )
    assert evaluate_condition(
        {"field": "service_size_amps", "operator": "greater_than_or_equal", "value": 400}, params
    )
    assert not evaluate_condition(
        {"field": "service_size_amps", "operator": "less_than", "value": 400}, params
    )
    assert evaluate_condition(
        {"field": "tags", "operator": "in", "value": ["ats", "panel"]}, params
    )
    assert not evaluate_condition({"field": "missing", "operator": "exists"}, params)


def test_compound_conditions() -> None:
    condition = {
        "all": [
            {"field": "service_size_amps", "operator": "greater_than_or_equal", "value": 400},
            {"field": "shutdown_required", "operator": "equals", "value": True},
        ]
    }
    assert evaluate_condition(condition, {"service_size_amps": 600, "shutdown_required": True})
    assert not evaluate_condition(condition, {"service_size_amps": 600, "shutdown_required": False})
