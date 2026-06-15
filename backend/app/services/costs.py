from decimal import Decimal, ROUND_HALF_UP


def calculate_cost_usd(
    input_tokens: int,
    output_tokens: int,
    input_price_per_1m: Decimal,
    output_price_per_1m: Decimal,
) -> Decimal:
    cost = (Decimal(input_tokens) / Decimal(1_000_000) * input_price_per_1m) + (
        Decimal(output_tokens) / Decimal(1_000_000) * output_price_per_1m
    )
    return cost.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
