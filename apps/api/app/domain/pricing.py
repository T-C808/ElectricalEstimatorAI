from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
THOUSANDTH = Decimal("0.001")


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def quantity(value: Decimal) -> Decimal:
    return Decimal(value).quantize(THOUSANDTH, rounding=ROUND_HALF_UP)


def material_sell(unit_cost: Decimal, markup_percent: Decimal) -> Decimal:
    return money(unit_cost * (Decimal("1") + markup_percent))


def labor_sell(hours: Decimal, labor_rate_per_hour: Decimal) -> Decimal:
    return money(hours * labor_rate_per_hour)


def calculate_totals(
    *,
    material_sell_total: Decimal,
    labor_sell_total: Decimal,
    equipment_sell_total: Decimal = Decimal("0"),
    subcontractor_sell_total: Decimal = Decimal("0"),
    fee_sell_total: Decimal = Decimal("0"),
    overhead_percent: Decimal,
    profit_percent: Decimal,
    contingency_percent: Decimal,
    tax_percent: Decimal,
) -> dict[str, Decimal]:
    subtotal = (
        material_sell_total
        + labor_sell_total
        + equipment_sell_total
        + subcontractor_sell_total
        + fee_sell_total
    )
    overhead = money(subtotal * overhead_percent)
    profit = money((subtotal + overhead) * profit_percent)
    contingency = money((subtotal + overhead + profit) * contingency_percent)
    tax = money(material_sell_total * tax_percent)
    total = money(subtotal + overhead + profit + contingency + tax)
    return {
        "material_subtotal": money(material_sell_total),
        "labor_subtotal": money(labor_sell_total),
        "equipment_subtotal": money(equipment_sell_total),
        "subcontractor_subtotal": money(subcontractor_sell_total),
        "fee_subtotal": money(fee_sell_total),
        "overhead_total": overhead,
        "profit_total": profit,
        "contingency_total": contingency,
        "tax_total": tax,
        "grand_total": total,
    }
