from exchange.markets.Currency import Currency
from exchange.markets.Index import Index
from exchange.markets.Instrument import FutureContract
from exchange.matchingengine.Order import LimitOrder,MarketOrder,Side
import asyncio
from exchange.utils import get_logger
import time
from threading import Thread
from uuid import uuid1


logger = get_logger()

# price simulation from 1980 to 2020
async def setgetprice(index: Index):
    index.set_price_feed(price_feed={index.name: 2000})
    upward = True
    while True:
        price = index.get_index_price()
        if (price > 2020):
            upward = False
        if(price < 1980):
            upward = True
        if(upward):
            index.set_price_feed(price_feed={index.name: (price + 0.1)})
        else:
            index.set_price_feed(price_feed={index.name: (price - 0.1)})

        # logger.info(f"Price of ${index.name} is ${price}")
        await asyncio.sleep(1)


def run_async_function_in_thread(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))
    loop.close()

async def getPrice(instrument: FutureContract):
    while True:
        logger.info(f"Index pr`ice is ${instrument.get_index_price()}")
        logger.info(f"Mark pric`e is ${instrument.get_mark_price()}")
        time.sleep(5)




if __name__== "__main__":

    usdc = Currency("USDC")
    eth = Currency("ETH")
    btc = Currency("BTC")

    ethUsdcIndex = Index(eth, usdc)

    # Thread to keep increasing price side by side
    thread = Thread(target=run_async_function_in_thread, args=(setgetprice, ethUsdcIndex), daemon=True)
    thread.start()


    # time.sleep(7)
    # price = ethUsdcIndex.get_index_price()
    # logger.info(f"Price after 10 seconds is ${price}")

    instrument = FutureContract("ETH-20DEC23", ethUsdcIndex, 1, eth, usdc, 0.1, 1702019809)
    logger.info(instrument.get_specs())

    instrument.start_futures_processes()
    # time.sleep(10)
    logger.info("########################## Empty order book infos #####################")
    logger.info(f"best bid price is ${instrument.orderbook.get_best_bid_price()}")
    logger.info(f"best bid size is ${instrument.orderbook.get_best_bid_size()}")
    logger.info(f"best bid price is ${instrument.orderbook.get_best_bid_price()}")
    logger.info(f"best bid size is ${instrument.orderbook.get_best_bid_size()}")
    logger.info(f"best ask price is ${instrument.orderbook.get_best_ask_price()}")
    logger.info(f"best ask size is ${instrument.orderbook.get_best_ask_size()}")
    logger.info(f"best ask price is ${instrument.orderbook.get_best_ask_price()}")
    logger.info(f"best ask size is ${instrument.orderbook.get_best_ask_size()}")
    logger.info(f"OI is ${instrument.orderbook.get_open_interest()}")
    logger.info(f"Last price is ${instrument.orderbook.get_last_price()}")
    time.sleep(5)
    logger.info(f"Stats are ${instrument.orderbook.stats}")

    logger.info("######################## Placing buy side limit orders ######################")

        # check order limits
    for i in range(1,201):
        order = LimitOrder(
                fromaddr=f"abc{i}def",
                order_id=str(uuid1()),
                side=Side.BUY,
                size=2*i,
                price=1980+i*0.1,
                time_in_force="GTC",
            )
        instrument.orderbook.process_order(order)

    logger.info("########################## Buy Limit orders stats #####################")
    logger.info(f"best bid price is ${instrument.orderbook.get_best_bid_price()}")
    logger.info(f"best bid size is ${instrument.orderbook.get_best_bid_size()}")
    logger.info(f"best bid price is ${instrument.orderbook.get_best_bid_price()}")
    logger.info(f"best bid size is ${instrument.orderbook.get_best_bid_size()}")
    logger.info(f"best ask price is ${instrument.orderbook.get_best_ask_price()}")
    logger.info(f"best ask size is ${instrument.orderbook.get_best_ask_size()}")
    logger.info(f"best ask price is ${instrument.orderbook.get_best_ask_price()}")
    logger.info(f"best ask size is ${instrument.orderbook.get_best_ask_size()}")

    logger.info(f"OI is ${instrument.orderbook.get_open_interest()}")
    logger.info(f"Last price is ${instrument.orderbook.get_last_price()}")
    logger.info(f"Stats are ${instrument.orderbook.stats}")

    logger.info("######################## Placing sell side limit orders ######################")

        # check order limits
    for i in range(1,201):
        order = LimitOrder(
                fromaddr=f"abc{i}def",
                order_id=str(uuid1()),
                side=Side.SELL,
                size=2*i,
                price=2000+i*0.1,
                time_in_force="GTC",
            )
        instrument.orderbook.process_order(order)


    logger.info("########################## Sell Limit orders stats #####################")
    logger.info(f"best bid price is ${instrument.orderbook.get_best_bid_price()}")
    logger.info(f"best bid size is ${instrument.orderbook.get_best_bid_size()}")
    logger.info(f"best bid price is ${instrument.orderbook.get_best_bid_price()}")
    logger.info(f"best bid size is ${instrument.orderbook.get_best_bid_size()}")
    logger.info(f"best ask price is ${instrument.orderbook.get_best_ask_price()}")
    logger.info(f"best ask size is ${instrument.orderbook.get_best_ask_size()}")
    logger.info(f"best ask price is ${instrument.orderbook.get_best_ask_price()}")
    logger.info(f"best ask size is ${instrument.orderbook.get_best_ask_size()}")

    logger.info(f"OI is ${instrument.orderbook.get_open_interest()}")
    logger.info(f"Last price is ${instrument.orderbook.get_last_price()}")
    logger.info(f"Stats are ${instrument.orderbook.stats}")

    logger.info("########################## Placing 50 market orders #####################")
    buy = True
    for i in range(1,51):
        if(buy):
            orderSide = Side.BUY
        else:
            orderSide = Side.SELL

        order = MarketOrder(
                fromaddr=f"abc{i}def",
                order_id=str(uuid1()),
                side= orderSide,
                size=5*i,
                time_in_force="GTC",
        )
        buy = not buy
        instrument.orderbook.process_order(order)

    logger.info("########################## Market orders stats #####################")
    logger.info(f"best bid price is ${instrument.orderbook.get_best_bid_price()}")
    logger.info(f"best bid size is ${instrument.orderbook.get_best_bid_size()}")
    logger.info(f"best bid price is ${instrument.orderbook.get_best_bid_price()}")
    logger.info(f"best bid size is ${instrument.orderbook.get_best_bid_size()}")
    logger.info(f"best ask price is ${instrument.orderbook.get_best_ask_price()}")
    logger.info(f"best ask size is ${instrument.orderbook.get_best_ask_size()}")
    logger.info(f"best ask price is ${instrument.orderbook.get_best_ask_price()}")
    logger.info(f"best ask size is ${instrument.orderbook.get_best_ask_size()}")
    time.sleep(10)
    logger.info(f"OI is ${instrument.orderbook.get_open_interest()}")
    logger.info(f"Last price is ${instrument.orderbook.get_last_price()}")
    logger.info(f"Stats are ${instrument.orderbook.stats}")


    asyncio.run(getPrice(instrument=instrument))