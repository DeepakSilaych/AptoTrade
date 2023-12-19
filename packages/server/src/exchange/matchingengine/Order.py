from enum import Enum
from time import time
from uuid import uuid1


class Side(Enum):
    BUY = 0
    SELL = 1


class Order(object):
    def __init__(self, order_id: str, label="", is_liquidation=False):
        self.order_id = order_id if order_id is not None else str(uuid1())
        self.time = int(1e6 * time())
        self.label = label
        self.is_liquidation = is_liquidation

    # Order received earlier has higher priority
    def __lt__(self, other):
        return self.time < other.time

    def __getType__(self):
        return self.__class__


class CancelOrder(Order):
    def __init__(self, fromaddr: str, order_id: str, label="", is_liquidation=False):
        super().__init__(order_id, label, is_liquidation)
        self.fromaddr = fromaddr

    def __repr__(self):
        return "Cancel Order: {}.".format(self.order_id)

    def get_obj(self):
        return {
            "order_id": self.order_id,
            "time": self.time,
            "fromaddr": self.fromaddr,
            "class": "CancelOrder",
            "label": self.label,
            "is_liquidation": self.is_liquidation
        }


class MarketOrder(Order):
    def __init__(
        self, fromaddr: str, order_id: str, side: Side, size: int, leverage: int , time_in_force: str, label="", is_liquidation=False
    ):
        super().__init__(order_id, label, is_liquidation)
        self.fromaddr = fromaddr
        self.side = side
        self.size = self.remainingToFill = size
        self.time_in_force = time_in_force
        self.leverage = leverage

    # Order received earlier has higher priority
    # If received at the same time, order with smaller size has higher priority
    def __lt__(self, other):
        if self.time != other.time:
            return self.time < other.time

        elif self.size != other.size:
            return self.size < other.size

    def __str__(self):
        return "Market Order: {0} {1} units.".format(
            "BUY" if self.side == Side.BUY else "SELL", self.remainingToFill
        )
    
    def getMarketOrderMargin(self, price: int):
        margin = (self.size * price)/self.leverage
        return margin

    def get_obj(self):
        return {
            "order_id": self.order_id,
            "time": self.time,
            "side": "buy" if self.side == Side.BUY else "sell",
            "size": self.size,
            "time_in_force": self.time_in_force,
            "fromaddr": self.fromaddr,
            "remainingToFill": self.remainingToFill,
            "class": "MarketOrder",
            "label": self.label,
            "is_liquidation": self.is_liquidation
        }


class LimitOrder(MarketOrder):
    def __init__(
        self,
        fromaddr: str,
        order_id: str,
        side: Side,
        size: int,
        leverage: int,
        price: int,
        time_in_force: str,
        label="",
        is_liquidation=False
    ):
        super().__init__(fromaddr, order_id, side, size, leverage, time_in_force, label, is_liquidation)
        self.price = price

    # Order received earlier has higher priority
    # If received at the same time, order with smaller size has higher priority
    def __lt__(self, other):
        if self.price != other.price:
            if self.side == Side.BUY:
                return self.price > other.price
            else:
                return self.price < other.price

        elif self.time != other.time:
            return self.time < other.time

        elif self.size != other.size:
            return self.size < other.size
        
    def getLimitOrderMargin(self):
        margin = (self.size * self.price)/self.leverage
        return margin

    def __str__(self):
        return "Limit Order: {0} {1} units at {2}.".format(
            "BUY" if self.side == Side.BUY else "SELL", self.remainingToFill, self.price
        )

    def get_obj(self):
        return {
            "order_id": self.order_id,
            "time": self.time,
            "side": "buy" if self.side == Side.BUY else "sell",
            "size": self.size,
            "time_in_force": self.time_in_force,
            "price": self.price,
            "fromaddr": self.fromaddr,
            "remainingToFill": self.remainingToFill,
            "class": "LimitOrder",
            "label": self.label,
            "is_liquidation": self.is_liquidation
        }
