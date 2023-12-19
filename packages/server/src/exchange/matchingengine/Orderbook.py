# from typing import List, Union
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import utc
from sortedcontainers import SortedList

from exchange.matchingengine.Trade import Trade
from exchange.producer import get_redpanda_producer
from exchange.utils import get_logger

from .Order import CancelOrder, LimitOrder, MarketOrder, Side

logger = get_logger("Orderbook")


class OrderBook(object):
    """
    An orderbook.
    -------------
    It can store and process orders.
    """

    def __init__(self, name, index, kind):
        self.producer = get_redpanda_producer()
        self.instrument_name = name
        self.bids = SortedList()
        self.asks = SortedList()
        self.state = "open"
        self.trades = []
        self.last_trade = None
        self.cancelled_orders = []
        self.filled_orders = []
        self.index = index
        self.kind = kind
        self.last_24h_prices = []
        self.open_interest = 0
        self.aggregated_bids_size_depth = 0
        self.aggregated_asks_size_depth = 0
        self.volume_usd = 0
        self.volume = 0
        self.volume_timestamp = int(1e6 * (time.time()))
        # self.last_5_min_trades = q/stac
        # self.5_min_ema=None
        self.logger = get_logger("Orderbook")
        self.stats = {
            "volume_usd": 0,
            "volume": 0,
            "price_change": 0,
            "low": 0,
            "high": 0,
        }
        sched = BackgroundScheduler(timezone=utc)
        sched.start()
        # daily_stats_trigger = CronTrigger(
        #     hour="12",
        #     minute="0",
        #     second="0",
        #     timezone=utc,
        # )
        daily_update_trigger = CronTrigger(
            day="*/1",
            timezone=utc,
        )
        fast_stats_trigger = CronTrigger(
            year="*",
            month="*",
            day="*",
            hour="*",
            minute="*",
            second="*/5",
            timezone=utc,
        )
        sched.add_job(
            self.daily_stats_update, trigger=daily_update_trigger, name="daily stats"
        )
        sched.add_job(
            self.daily_stats_trigger, trigger=fast_stats_trigger, name="daily stats"
        )

    def daily_stats_update(self):
        self.volume_timestamp = int(1e6 * (time.time()))
        self.last_24h_prices = []
        self.volume = 0
        self.volume_usd = 0

    def daily_stats_trigger(self):

        self.stats["volume_usd"] = self.volume_usd
        self.stats["volume"] = self.volume
        if len(self.last_24h_prices) != 0:
            self.stats["low"] = min(self.last_24h_prices)
            self.stats["high"] = max(self.last_24h_prices)
            self.stats["price_change"] = (
                self.last_24h_prices[-1] - self.last_24h_prices[0]
            )
        # self.logger.info(self.stats)

    def get_best_bid(self):
        return (self.get_best_bid_size(), self.get_best_bid_price())

    def get_best_ask(self):
        return (self.get_best_ask_size(), self.get_best_ask_price())

    def get_best_bid_size(self):
        return self.bids[0].remainingToFill if len(self.bids) > 0 else 0

    def get_best_ask_size(self):
        return self.asks[0].remainingToFill if len(self.asks) > 0 else 0

    def get_best_bid_price(self):
        return self.bids[0].price if len(self.bids) > 0 else 0

    def get_best_ask_price(self):
        return self.asks[0].price if len(self.asks) > 0 else 0

    def get_last_price(self):
        return self.last_trade.price if self.last_trade is not None else 0

    def get_open_interest(self):
        return self.open_interest

    def process_order(self, incomingOrder):

        # `filled_orders`: orders completely filled during incoming order execution
        filled_orders = {}
        # `updated_orders`: orders partially filled during incoming order execution
        updated_orders = {}
        # `cancelled_orders`: orders cancelled during incoming order execution
        cancelled_orders = {}
        # account to send notification about updated orders
        involved_accounts = set({})

        """
        Processes an order

        Depending on the type of order the following can happen:
        - Market Order
        - Limit Order
        - Cancel Order
        """

        trades = []

        if incomingOrder.__class__ == CancelOrder:
            for order in self.bids:
                if incomingOrder.order_id == order.order_id:
                    self.bids.discard(order)
                    self.aggregated_bids_size_depth -= order.remainingToFill
                    # add to cancelled orders
                    cancelled_orders[incomingOrder.order_id] = incomingOrder.get_obj()
                    break

            for order in self.asks:
                if incomingOrder.order_id == order.order_id:
                    self.asks.discard(order)
                    self.aggregated_asks_size_depth -= order.remainingToFill
                    # add to cancelled orders
                    cancelled_orders[incomingOrder.order_id] = incomingOrder.get_obj()
                    break

            return (
                trades,
                updated_orders,
                filled_orders,
                cancelled_orders,
                involved_accounts,
            )

        def whileClause():
            """
            Determined whether to continue the while-loop
            """
            if incomingOrder.side == Side.BUY:
                if incomingOrder.__class__ == LimitOrder:
                    return (
                        len(self.asks) > 0 and incomingOrder.price >= self.asks[0].price
                    )  # Limit order on the BUY side
                elif incomingOrder.__class__ == MarketOrder:
                    return len(self.asks) > 0  # Market order on the BUY side
            else:
                if incomingOrder.__class__ == LimitOrder:
                    return (
                        len(self.bids) > 0 and incomingOrder.price <= self.bids[0].price
                    )  # Limit order on the SELL side
                elif incomingOrder.__class__ == MarketOrder:
                    return len(self.bids) > 0  # Market order on the SELL side

        # while there are orders and the orders requirements are matched
        while whileClause():
            bookOrder = None
            if incomingOrder.side == Side.BUY:
                bookOrder = self.asks.pop(0)
            else:
                bookOrder = self.bids.pop(0)

            if (
                incomingOrder.remainingToFill == bookOrder.remainingToFill
            ):  # if the same volume
                volume = incomingOrder.remainingToFill
                incomingOrder.remainingToFill -= volume
                bookOrder.remainingToFill -= volume

                # update aggregate
                self._update_size_aggregates(incomingOrder.side, volume)

                trade = Trade(
                    incomingOrder.fromaddr,
                    bookOrder.fromaddr,
                    incomingOrder.side,
                    bookOrder.price,
                    volume,
                    incomingOrder.order_id,
                    bookOrder.order_id,
                )

                # add to filled orders
                filled_orders[bookOrder.order_id] = bookOrder.get_obj()
                filled_orders[incomingOrder.order_id] = incomingOrder.get_obj()
                # add both accounts to involved accounts
                involved_accounts.add(bookOrder.fromaddr)
                involved_accounts.add(incomingOrder.fromaddr)

                if bookOrder.fromaddr != incomingOrder.fromaddr:
                    self._execute_trade(trade)
                    trades.append(trade)
                break

            elif (
                incomingOrder.remainingToFill > bookOrder.remainingToFill
            ):  # incoming has greater volume
                volume = bookOrder.remainingToFill
                incomingOrder.remainingToFill -= volume
                bookOrder.remainingToFill -= volume

                # update aggregate
                self._update_size_aggregates(incomingOrder.side, volume)

                trade = Trade(
                    incomingOrder.fromaddr,
                    bookOrder.fromaddr,
                    incomingOrder.side,
                    bookOrder.price,
                    volume,
                    incomingOrder.order_id,
                    bookOrder.order_id,
                )
                # add bookOrder to filled orders as it'e been completely filled
                filled_orders[bookOrder.order_id] = bookOrder.get_obj()
                # add incomingOrder to updated order as it has been only been partially filled so far
                updated_orders[incomingOrder.order_id] = incomingOrder.get_obj()

                # add both accounts to involved accounts
                involved_accounts.add(bookOrder.fromaddr)
                involved_accounts.add(incomingOrder.fromaddr)

                if bookOrder.fromaddr != incomingOrder.fromaddr:
                    self._execute_trade(trade)
                    trades.append(trade)

            elif (
                incomingOrder.remainingToFill < bookOrder.remainingToFill
            ):  # book has greater volume
                volume = incomingOrder.remainingToFill
                incomingOrder.remainingToFill -= volume
                bookOrder.remainingToFill -= volume

                # update aggregate
                self._update_size_aggregates(incomingOrder.side, volume)

                trade = Trade(
                    incomingOrder.fromaddr,
                    bookOrder.fromaddr,
                    incomingOrder.side,
                    bookOrder.price,
                    volume,
                    incomingOrder.order_id,
                    bookOrder.order_id,
                )
                # add incomingOrder to filled orders as it's been completely filled
                filled_orders[incomingOrder.order_id] = incomingOrder.get_obj()
                # add bookOrder to updated orders as it's only been partially filled so far
                updated_orders[bookOrder.order_id] = bookOrder.get_obj()

                # add both accounts to involved accounts
                involved_accounts.add(bookOrder.fromaddr)
                involved_accounts.add(incomingOrder.fromaddr)

                if bookOrder.fromaddr != incomingOrder.fromaddr:
                    self._execute_trade(trade)
                    trades.append(trade)

                if bookOrder.side == Side.SELL:
                    self.asks.add(bookOrder)
                else:
                    self.bids.add(bookOrder)

                break

        if (
            incomingOrder.remainingToFill > 0
            and incomingOrder.__class__ == LimitOrder
            and incomingOrder.time_in_force == "GTC"
        ):
            if incomingOrder.side == Side.BUY:
                self.bids.add(incomingOrder)
                self.aggregated_bids_size_depth += incomingOrder.remainingToFill
            else:
                self.asks.add(incomingOrder)
                self.aggregated_asks_size_depth += incomingOrder.remainingToFill

            # add incoming to involved accounts, in case no matches found during execution
            involved_accounts.add(incomingOrder.fromaddr)
            # add incomingOrder to updated orders as it's either been only partially filled or not at all
            updated_orders[incomingOrder.order_id] = incomingOrder.get_obj()
        elif incomingOrder.time_in_force == "IOC":
            # add incoming to involved accounts, in case no matches found during execution
            involved_accounts.add(incomingOrder.fromaddr)
            # cancel remaining IOC order
            cancelled_orders[incomingOrder.order_id] = incomingOrder.get_obj()

        # return all trades executed while processing this order
        return (
            trades,
            updated_orders,
            filled_orders,
            cancelled_orders,
            involved_accounts,
        )

    def __len__(self):
        return len(self.asks) + len(self.bids)

    def _execute_trade(self, trade: Trade):
        self.trades.append(trade)
        self.producer.produce(
            {
                "instrument_name": self.instrument_name,
                "kind": self.kind,
                "trade": trade.getObj(),
            },
            "trades",
        )
        self.last_trade = trade
        if trade.side == "buy":
            self.open_interest += trade.size
        else:
            self.open_interest -= trade.size
        if trade.timestamp > self.volume_timestamp:
            self.volume += abs(trade.size)
            self.volume_usd += abs(trade.size) * abs(trade.price)
        self.last_24h_prices.append(abs(self.last_trade.price))

    def _update_size_aggregates(self, incomingOrderSide, size):
        # update aggregate
        if incomingOrderSide == Side.BUY:
            self.aggregated_asks_size_depth -= size
        else:
            self.aggregated_bids_size_depth -= size


class PerpsOrderbook(OrderBook):
    """
    An orderbook.
    -------------
    It can store and process orders.
    """

    def __init__(self, name, index, kind, imn, contract_size):
        super().__init__(name, index, kind)
        self.perp_ema = 0
        self.funding_rate = 0
        self.premium_rate = 0
        self.imn = imn  # Impact price notional  (Calculated as 200/IMR, Initial margin rate 5% for 20x)
        self.contract_size = contract_size

    def get_fair_impact_price(self, bid_asks):
        # For linear perps
        running_bid_tot = 0
        last_level = 0
        running_size_tot = 0
        last_size = 0
        # print("arr", bid_asks)
        for order in bid_asks:
            if (
                running_bid_tot
                + ((1 / self.contract_size) * order.remainingToFill * order.price)
                < self.imn
            ):
                running_bid_tot = (
                    running_bid_tot
                    + (1 / self.contract_size) * order.remainingToFill * order.price
                )
                running_size_tot = running_size_tot + order.remainingToFill
                last_size = order.remainingToFill
                last_level = (
                    (1 / self.contract_size) * order.remainingToFill * order.price
                )
        # print("inter", running_bid_tot, running_size_tot, last_size, last_level)
        # print("Imn", self.imn)
        if (running_bid_tot - last_level) + (running_size_tot - last_size) == 0:
            return 0
        fair_impact_denom = (
            (self.imn - ((1 / self.contract_size) * (running_bid_tot)))
            / (running_bid_tot - last_level)
        ) + ((1 / self.contract_size) * (running_size_tot - last_size))
        # print("denom", fair_impact_denom)
        # print("last levels",  (running_bid_tot - last_level), (running_size_tot - last_size))
        fair_impact = (self.imn) / fair_impact_denom
        return fair_impact

    def update_perp_ema(self):
        # calculate 30s ema of fair price - index
        # ema = price(current_sec) * k + ema(last_sec) * (1 – k)
        # k = 2/(N+1)
        # self.perp_ema = (((self.get_best_bid_price() + self.get_best_ask_proce()) / 2) - self.index.get_index_price())
        self.perp_ema = 0
        while True:
            # calculate fair impact bid and ask price
            # print("IMN", self.imn)
            fair_impact_bid = self.get_fair_impact_price(self.bids)
            fair_impact_ask = self.get_fair_impact_price(self.asks)
            self.perp_ema = (
                (
                    ((fair_impact_bid + fair_impact_ask) / 2)
                    - self.index.get_index_price()
                )
                * (2 / 31)
            ) + (self.perp_ema * (1 - (2 / 31)))
            time.sleep(1)

    def update_funding_rate(self):
        # Funding rate = Interest Rate + Premium Rate
        while True:
            count_tot = 0
            interest_rate = 0.01  # Constant
            avg_premium_index = 0
            # premium index is calculates every five seconds, Number of dataPoints = 12*60*8 = 5760
            for i in range(5760):
                try:
                    # Taking time weighted average
                    premium_rate = (
                        max(
                            0,
                            self.get_fair_impact_price(self.bids)
                            - self.index.get_index_price(),
                        )
                        - max(
                            0,
                            self.index.get_index_price()
                            - self.get_fair_impact_price(self.asks),
                        )
                    ) / self.index.get_index_price()
                    # print("Premium rate is " + premium_rate)
                    logger.info(f"Premium Index is ${premium_rate}")
                    avg_premium_index = (
                        avg_premium_index * count_tot + (i + 1) * premium_rate
                    ) / (count_tot + (i + 1))
                    logger.info(f"avg premium rate ${avg_premium_index}")
                    self.funding_rate = interest_rate

                    if (interest_rate - avg_premium_index) < -0.05:
                        self.funding_rate = avg_premium_index + 0.05
                    elif (interest_rate - avg_premium_index) > 0.05:
                        self.funding_rate = avg_premium_index - 0.05

                    # logger.info("funding rate is " , self.funding_rate)
                    if self.funding_rate < -0.75:
                        self.funding_rate = -0.75
                    elif self.funding_rate > 0.75:
                        self.funding_rate = 0.75

                    count_tot = count_tot + (i + 1)
                    self.funding_rate = self.funding_rate / 100
                except:
                    self.funding_rate = interest_rate
                    self.funding_rate = self.funding_rate / 100
                    logger.info(f"Funding Rate is ${self.funding_rate}")
                time.sleep(5)

    def get_mark_price(self):
        # check for extremes and fair impact price calculations
        # Order - fromaddr: str, order_id: str, side: Side, size: int, price: int
        # Check clipping conds
        index_price = self.index.get_index_price()
        mark_price = mark_price = index_price + self.perp_ema
        if self.perp_ema >= 0.005 * index_price:
            mark_price = 1.005 * index_price
        elif self.perp_ema <= 0.005 * index_price:
            mark_price = 0.995 * index_price

        return mark_price



class FuturesOrderbook(OrderBook):
    """
    A Futures orderbook.
    -------------
    It can store and process orders.
    """

    def __init__(self, name, index, kind):
        super().__init__(name, index, kind)
        self.futures_ema = 0

    def update_futures_ema(self):
        # calculate 30s ema of fair price - index
        # ema = price(current_sec) * k + ema(last_sec) * (1 – k)
        # k = 2/(N+1)
        # self.perp_ema = (((self.get_best_bid_price() + self.get_best_ask_proce()) / 2) - self.index.get_index_price())
        self.futures_ema = 0
        while True:
            # calculate futures market price
            best_ask_price = self.get_best_ask_price()
            best_bid_price = self.get_best_bid_price()
            last_trade_price = self.get_last_price()
            index_price = self.index.get_index_price()
            futures_mkt_price = last_trade_price

            if last_trade_price < best_bid_price:
                futures_mkt_price = best_bid_price
            elif last_trade_price > best_ask_price:
                futures_mkt_price = best_ask_price

            self.futures_ema = ((futures_mkt_price - index_price) * (2 / 31)) + (
                self.futures_ema * (1 - (2 / 31))
            )
            # logger.info(f"ema is ${self.futures_ema}")

            time.sleep(1)

    def get_mark_price(self):
        index_price = self.index.get_index_price()
        mark_price = index_price + self.futures_ema
        if self.futures_ema >= 0.005 * index_price:
            mark_price = 1.0000003 * index_price
        elif self.futures_ema <= 0.005 * index_price:
            mark_price = 0.9999997 * index_price

        return mark_price
