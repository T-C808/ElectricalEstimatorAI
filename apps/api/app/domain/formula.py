from __future__ import annotations

import ast
from decimal import Decimal, DivisionByZero, InvalidOperation
from typing import Any

ALLOWED_VARIABLES = {
    "feeder_length_ft",
    "conductor_count",
    "conduit_count",
    "waste_factor",
    "crew_size",
    "difficulty_factor",
    "base_hours",
}


class FormulaError(ValueError):
    pass


def _decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise FormulaError("Boolean values are not valid formula numbers")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise FormulaError(f"Invalid numeric value: {value!r}") from exc


def evaluate_formula(expression: str, variables: dict[str, Any]) -> Decimal:
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise FormulaError("Formula syntax is invalid") from exc
    return _evaluate_node(parsed.body, variables)


def _evaluate_node(node: ast.AST, variables: dict[str, Any]) -> Decimal:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, int | float):
            return _decimal(node.value)
        raise FormulaError("Only numeric constants are allowed in formulas")

    if isinstance(node, ast.Name):
        if node.id not in ALLOWED_VARIABLES:
            raise FormulaError(f"Variable '{node.id}' is not allowed")
        if node.id not in variables:
            raise FormulaError(f"Variable '{node.id}' was not provided")
        return _decimal(variables[node.id])

    if isinstance(node, ast.BinOp):
        left = _evaluate_node(node.left, variables)
        right = _evaluate_node(node.right, variables)
        try:
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
        except DivisionByZero as exc:
            raise FormulaError("Formula division by zero") from exc
        raise FormulaError("Formula operator is not allowed")

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_evaluate_node(node.operand, variables)

    raise FormulaError("Formula contains an unsupported expression")
