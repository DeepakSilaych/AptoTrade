import asyncio

from exchange.markets.Currency import Currency


class Index:
    """Index for a instrument"""

    def __init__(self, base_currency: Currency, quote_currency: Currency) -> None:
        self.name = base_currency.symbol + "/" + quote_currency.symbol
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.price_feed = {}
        # self._logger = get_logger()

    def set_price_feed(self, price_feed):
        self.price_feed = price_feed

    def get_index_price(self):
        if self.price_feed is not None:
            if self.name in self.price_feed:
                return self.price_feed[self.name]
            else:
                try:
                    base_price_in_usd = self.price_feed[
                        self.base_currency.symbol + "/USD"
                    ]
                    quote_price_in_usd = self.price_feed[
                        self.quote_currency.symbol + "/USD"
                    ]
                    return float(base_price_in_usd) / float(quote_price_in_usd)
                except Exception as e:
                    return 0
        else:
            return 0


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()

    usdc = Currency("Circle USD", "USDC", 6)
    eth = Currency("Ethereum", "ETH", 18)
    btc = Currency("Bitcoin", "BTC", 8)
    apt = Currency("Aptos", "APT")

    i = Index(eth, usdc)
    # price = loop.run_until_complete(i.get_index_price())
    # print(price)
