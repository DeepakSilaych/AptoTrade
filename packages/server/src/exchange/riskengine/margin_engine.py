from exchange.riskengine.standard_margin import get_standard_margin


def calculate_total_margin_required(
    all_positions,
    all_open_orders,
    current_instrument_data=None,
    new_order=None,
):
        return get_standard_margin(
            all_positions,
            all_open_orders,
            new_order,
        )
