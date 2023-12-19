import json
from time import time

from exchange.matchingengine.Order import Side


class Trade(object):
    """
    Trade
    -----

    A trade object
    """

    def __init__(
        self,
        taker: str,
        maker: str,
        incoming_side: Side,
        price: float,
        trade_size: float,
        incoming_order_id: str,
        book_order_id: str,
    ):
        self.timestamp = int(1e6 * time())
        self.side = incoming_side
        self.price = price
        self.size = trade_size
        self.incoming_order_id = incoming_order_id
        self.book_order_id = book_order_id
        self.taker = taker
        self.maker = maker

    def __repr__(self):
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "side": "buy" if self.side == Side.BUY else "sell",
                "price": self.price,
                "size": self.size,
                "incoming_order_id": self.incoming_order_id,
                "book_order_id": self.book_order_id,
                "taker": self.taker,
                "maker": self.maker,
            }
        )

    def toJSON(self):
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "side": "buy" if self.side == Side.BUY else "sell",
                "price": self.price,
                "size": self.size,
                "incoming_order_id": self.incoming_order_id,
                "book_order_id": self.book_order_id,
                "taker": self.taker,
                "maker": self.maker,
            }
        )

    def getObj(self):
        return {
            "timestamp": self.timestamp,
            "side": "buy" if self.side == Side.BUY else "sell",
            "price": self.price,
            "size": self.size,
            "incoming_order_id": self.incoming_order_id,
            "book_order_id": self.book_order_id,
            "taker": self.taker,
            "maker": self.maker,
        }
