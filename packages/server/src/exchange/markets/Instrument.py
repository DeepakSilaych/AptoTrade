#!/usr/bin/env python3

import uuid
from datetime import datetime
from enum import Enum
from threading import Thread
from time import time

# from Currency import Currency
# from Index import Index
from exchange.markets.Currency import Currency
from exchange.markets.Index import Index
from exchange.matchingengine.Orderbook import (
    FuturesOrderbook,
    PerpsOrderbook,
)


def getExpiryFromTimestamp(timestamp):
    date = datetime.fromtimestamp(timestamp)
    capMonth = date.strftime("%b").upper()
    return date.strftime("%d") + capMonth + date.strftime("%y")


class InstrumentCode(Enum):
    SPOT = 1
    USD_M_PERP = 2
    USD_M_FUTURE = 3
    USD_M_OPTION = 4


class Instrument:
    """Instrument"""

    def __init__(
        self,
        name: str,
        index: Index,
        contract_size: int,
        base_currency: Currency,
        quote_currency: Currency,
        tick_size: int,
        maker_comission=0.0003,
        taker_comission=0.0003,
        block_trade_commission=0.0003,
        max_liquidation_comission=0.0075,
    ):
        self.id = uuid.uuid4()
        self.name = name
        self.index = index
        self.contract_size = contract_size
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.tick_size = tick_size
        self.maker_comission = maker_comission
        self.taker_comission = taker_comission
        self.block_trade_commission = block_trade_commission
        self.max_liquidation_comission = max_liquidation_comission
        # Default vars
        self.created_at = time()
        self.rfq = True
        self.is_active = True
        self.is_expired = False

    def get_index_price(self):
        return self.index.get_index_price()

    def activate_instrument(self):
        self.is_active = True

    def deactivate_instrument(self):
        self.is_active = False

    def enable_rfq(self):
        self.rfq = True

    def disable_rfq(self):
        self.rfq = False


class PerpContract(Instrument):
    """Perpetual futures Contract"""

    def __init__(
        self,
        name: str,
        index: Index,
        contract_size: int,
        base_currency: Currency,
        quote_currency: Currency,
        tick_size: int,
        max_leverage=50,
        settlement_period="perpetual",
        maker_comission=0.0003,
        taker_comission=0.0003,
        block_trade_commission=0.0001,
        max_liquidation_comission=0.0075,
    ):
        super().__init__(
            name,
            index,
            contract_size,
            base_currency,
            quote_currency,
            tick_size,
            maker_comission,
            taker_comission,
            block_trade_commission,
            max_liquidation_comission,
        )
        self.kind = "future"
        self.code = InstrumentCode.USD_M_PERP
        self.max_leverage = max_leverage
        self.funding_rate = 0
        self.settlement_period = settlement_period
        # How much impact $200 has orderbook
        self.impact_price_notional = 200 * self.max_leverage
        self.orderbook = PerpsOrderbook(
            name, index, self.kind, self.impact_price_notional, contract_size
        )
        self.perp_ema = 0.0
        self.t = Thread(target=self.orderbook.update_perp_ema, args=())
        # self.t.start()
        self.t1 = Thread(target=self.orderbook.update_funding_rate, args=())
        # self.t1.start()
        assert self.name == self.base_currency.symbol + "USD-PERP"

    def start_perp_processes(self):
        self.t.start()
        self.t1.start()

    def get_mark_price(self):
        return self.orderbook.get_mark_price()

    def get_funding_rate(self):
        return self.funding_rate

    def get_specs(self):
        return {
            "name": self.name,
            "index": self.index.name,
            "funding_rate": self.funding_rate,
            "is_active": self.is_active,
            "max_leverage": self.max_leverage,
            "contract_size": self.contract_size,
            "base_currency": self.base_currency.symbol,
            "settlement_currency": self.settlement_currency.symbol,
            "quote_currency": self.quote_currency.symbol,
            "tick_size": self.tick_size,
            "kind": self.kind,
            "settlement_period": self.settlement_period,
            "future_type": self.future_type,
            "maker_comission": self.maker_comission,
            "taker_comission": self.taker_comission,
            "block_trade_commission": self.block_trade_commission,
            "max_liquidation_comission": self.max_liquidation_comission,
            "ask": self.orderbook.get_best_ask(),
            "bid": self.orderbook.get_best_bid(),
            "mark_price": self.orderbook.get_mark_price(),
        }


class FutureContract(Instrument):
    """Dated futures Contract"""

    def __init__(
        self,
        name: str,
        index: Index,
        contract_size: int,
        base_currency: Currency,
        quote_currency: Currency,
        tick_size: int,
        expiration,
        max_leverage=50,
        settlement_period="weekly",
        maker_comission=0.0003,
        taker_comission=0.0003,
        block_trade_commission=0.0001,
        max_liquidation_comission=0.0075,
        impact_price_notional=10000,
    ):
        super().__init__(
            name,
            index,
            contract_size,
            base_currency,
            quote_currency,
            tick_size,
            maker_comission,
            taker_comission,
            block_trade_commission,
            max_liquidation_comission,
        )
        self.kind = "future"
        self.code = InstrumentCode.USD_M_FUTURE
        self.max_leverage = max_leverage
        self.settlement_period = settlement_period
        self.expiration = expiration
        if self.expiration < time():
            self.is_expired = True
            self.is_active = False
        self.orderbook = FuturesOrderbook(name, index, self.kind)
        self.perp_ema = 0.0
        self.t = Thread(target=self.orderbook.update_futures_ema, args=())
        # self.t.start()
        name = self.base_currency.symbol + "-" + getExpiryFromTimestamp(self.expiration)
        assert self.name == name

    def start_futures_processes(self):
        self.t.start()

    def get_mark_price(self):
        return self.orderbook.get_mark_price()

    def get_specs(self):
        return {
            "name": self.name,
            "index": self.index.name,
            "is_active": self.is_active,
            "max_leverage": self.max_leverage,
            "contract_size": self.contract_size,
            "base_currency": self.base_currency.symbol,
            "quote_currency": self.quote_currency.symbol,
            "tick_size": self.tick_size,
            "kind": self.kind,
            "settlement_period": self.settlement_period,
            "expiration": self.expiration,
            "maker_comission": self.maker_comission,
            "taker_comission": self.taker_comission,
            "block_trade_commission": self.block_trade_commission,
            "max_liquidation_comission": self.max_liquidation_comission,
            "ask": self.orderbook.get_best_ask(),
            "bid": self.orderbook.get_best_bid(),
            "mark_price": self.orderbook.get_mark_price(),
        }
