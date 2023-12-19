from datetime import datetime, timezone

from exchange.markets.Instrument import InstrumentCode
from exchange.matchingengine.Order import Side
from exchange.utils import get_logger

logger = get_logger()


def get_standard_margin(
    all_positions,
    all_open_orders,
    new_order=None,
):
    positions_margin = get_standard_margin_for_positions(
        all_positions
    )
    open_orders_margin = get_standard_margin_for_orders(
        all_open_orders
    )
    new_order_margin = get_standard_margin_for_order(
            new_order
        )

    return calculate_total_standard_margin(
        positions_margin,
        open_orders_margin,
        new_order_margin,
    )


def calculate_total_standard_margin(
    postions_margin,
    open_orders_margin,
    new_order_margin,
):
    return (postions_margin + open_orders_margin + new_order_margin)


"""
For active positions
"""


def get_standard_margin_for_positions(
    all_positions,
):
    total_margin = 0
    for instrument_name in all_positions:
        position = all_positions[instrument_name]
        margin = get_standard_margin_for_positon(position)
        total_margin += margin

    return total_margin


def get_standard_margin_for_positon(position):
    try:
        return position["margin"]
    except:
        return 0


"""
For existing orders in the orderbook
"""


def get_standard_margin_for_orders(
    all_open_orders,
):
    total_margin = 0
    for instrument_name in all_open_orders:
        for order_id in all_open_orders[instrument_name]:
            margin = get_standard_margin_for_order(
                all_open_orders[instrument_name][order_id],
            )
            total_margin += margin
    return total_margin



def get_standard_margin_for_order(open_order):

    try:
        return (open_order["remainingToFill"] * open_order["price"])/open_order["leverage"]
    except:
        return 0



