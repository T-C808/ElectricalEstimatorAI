from __future__ import annotations

from decimal import Decimal

from app.domain.pricing import calculate_totals, labor_sell, material_sell


def test_material_markup_behavior() -> None:
    assert material_sell(Decimal("100.00"), Decimal("0.25")) == Decimal("125.00")


def test_labor_rate_behavior() -> None:
    assert labor_sell(Decimal("8"), Decimal("125.00")) == Decimal("1000.00")


def test_overhead_profit_contingency_behavior() -> None:
    totals = calculate_totals(
        material_sell_total=Decimal("125.00"),
        labor_sell_total=Decimal("1000.00"),
        overhead_percent=Decimal("0.10"),
        profit_percent=Decimal("0.15"),
        contingency_percent=Decimal("0.05"),
        tax_percent=Decimal("0.00"),
    )
    assert totals["material_subtotal"] == Decimal("125.00")
    assert totals["labor_subtotal"] == Decimal("1000.00")
    assert totals["overhead_total"] == Decimal("112.50")
    assert totals["profit_total"] == Decimal("185.63")
    assert totals["contingency_total"] == Decimal("71.16")
    assert totals["grand_total"] == Decimal("1494.29")
