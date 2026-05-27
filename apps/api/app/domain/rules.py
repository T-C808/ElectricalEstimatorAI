from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Any


class RuleError(ValueError):
    pass


def evaluate_condition(condition: Mapping[str, Any], parameters: Mapping[str, Any]) -> bool:
    if "all" in condition:
        return all(evaluate_condition(item, parameters) for item in condition["all"])
    if "any" in condition:
        return any(evaluate_condition(item, parameters) for item in condition["any"])

    field = condition.get("field")
    operator = condition.get("operator")
    expected = condition.get("value")

    if not field or not operator:
        raise RuleError("Rule condition requires field and operator")

    exists = field in parameters and parameters[field] not in (None, "")
    actual = parameters.get(field)

    if operator == "exists":
        return exists
    if not exists:
        return False
    if operator == "equals":
        return actual == expected
    if operator == "not_equals":
        return actual != expected
    if operator == "in":
        if not isinstance(expected, list | tuple | set):
            raise RuleError("Rule 'in' operator requires a list value")
        return actual in expected

    if operator in {
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
    }:
        left = _to_decimal(actual)
        right = _to_decimal(expected)
        if operator == "greater_than":
            return left > right
        if operator == "greater_than_or_equal":
            return left >= right
        if operator == "less_than":
            return left < right
        if operator == "less_than_or_equal":
            return left <= right

    raise RuleError(f"Unsupported condition operator: {operator}")


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise RuleError(f"Value is not numeric: {value!r}") from exc


def target_matches(candidate: str | None, target: str | None) -> bool:
    if not candidate or not target:
        return False
    candidate_norm = _normalize(candidate)
    target_norm = _normalize(target)
    aliases = {
        "conduitinstalllabor": "conduitinstallperft",
        "feederpulllabor": "pullfeederperft",
    }
    return candidate_norm == target_norm or candidate_norm == aliases.get(target_norm)


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())
