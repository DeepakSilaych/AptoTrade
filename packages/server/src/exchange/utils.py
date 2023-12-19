import logging
from decimal import Decimal

from voluptuous import Any, Range, Required, Schema

LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "level": logging.DEBUG,
}

message_schema = Schema(
    Any(
        {
            "req_id": Any(int, None),
            "method": "public/get_instruments",
            "params": {
                Required("currency"): str,
                "kind": Any("future", "option", "future_combo", "option_combo"),
                "expired": bool,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "public/get_currencies",
            "params": {},
        },
        {
            "req_id": Any(int, None),
            "method": "public/get_orderbook",
            "params": {Required("instrument_name"): str, "depth": int},
        },
        {
            "req_id": Any(int, None),
            "method": "private/buy",
            "params": {
                Required("instrument_name"): str,
                Required("amount"): Any(Decimal, Range(min=0)),
                "type": Any(
                    "limit",
                    "stop_limit",
                    "take_limit",
                    "market",
                    "stop_market",
                    "take_market",
                    "market_limit",
                    "trailing_stop",
                    default="limit",
                ),
                "label": str,
                "price": Any(Decimal, Range(min=0)),
                "time_in_force": Any(
                    "good_til_cancelled",
                    "good_til_day",
                    "fill_or_kill",
                    "immediate_or_cancel",
                    default="good_til_cancelled",
                ),
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/sell",
            "params": {
                Required("instrument_name"): str,
                Required("amount"): Any(Decimal, Range(min=0)),
                "type": Any(
                    "limit",
                    "stop_limit",
                    "take_limit",
                    "market",
                    "stop_market",
                    "take_market",
                    "market_limit",
                    "trailing_stop",
                    default="limit",
                ),
                "label": str,
                "price": Any(Decimal, Range(min=0)),
                "time_in_force": Any(
                    "good_til_cancelled",
                    "good_til_day",
                    "fill_or_kill",
                    "immediate_or_cancel",
                    default="good_til_cancelled",
                ),
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/edit",
            "params": {
                Required("order_id"): str,
                Required("amount"): Any(Decimal, Range(min=0)),
                "price": Any(Decimal, Range(min=0)),
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/cancel",
            "params": {
                Required("order_id"): str,
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/deposit",
            "params": {
                Required("currency"): str,
                Required("address"): str,
                Required("amount"): Any(Decimal, Range(min=0)),
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/withdraw",
            "params": {
                Required("currency"): str,
                Required("address"): str,
                Required("amount"): Any(Decimal, Range(min=0)),
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/toggle_portfolio_margining",
            "params": {
                Required("user_id"): str,
                Required("enabled"): bool,
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/get_portfolio_margins",
            "params": {
                Required("currency"): str,
                "add_positions": bool,
                "simulated_positions": object,
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/get_standard_margins",
            "params": {
                Required("currency"): str,
                "add_positions": Any(bool, default=True),
                "simulated_positions": object,
                Required("from"): str,
                Required("signature"): str,
            },
        },
        {
            "req_id": Any(int, None),
            "method": "private/get_positions",
            "params": {
                Required("currency"): str,
                "kind": Any("option", "future", "future_combo", "option_combo"),
            },
        },
    ),
    required=True,
)


def get_logger(name="Futures Exchande"):
    logging.getLogger("kafka").setLevel(logging.ERROR)
    (logging.getLogger("apscheduler.executors.default")).setLevel(logging.ERROR)
    (logging.getLogger("apscheduler.scheduler")).setLevel(logging.ERROR)
    (logging.getLogger("numba.core.interpreter")).setLevel(logging.ERROR)
    (logging.getLogger("numba.core.byteflow")).setLevel(logging.ERROR)
    (logging.getLogger("numba.core.ssa")).setLevel(logging.ERROR)
    logging.getLogger("uvicorn").handlers.clear()
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.disabled = True
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True

    logging.basicConfig(**LOGGING_PROPERTIES)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
