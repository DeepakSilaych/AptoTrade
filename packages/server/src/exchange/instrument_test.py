from exchange.markets.Currency import Currency
from exchange.markets.Index import Index
from exchange.markets.Instrument import FutureContract,getExpiryFromTimestamp
import asyncio
from exchange.utils import get_logger
import time
from threading import Thread


logger = get_logger()

async def setgetprice(index: Index):
    while True:
        price = index.get_index_price()
        # logger.info(f"Price of ${index.name} is ${price}")
        index.set_price_feed(price_feed={index.name: (price + 1)})
        await asyncio.sleep(1)


def run_async_function_in_thread(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))
    loop.close()

async def getPrice(instrument: FutureContract):
    while True:
        logger.info(f"Index price is ${instrument.get_index_price()}")
        logger.info(f"Mark price is ${instrument.get_mark_price()}")
        time.sleep(5)




if __name__== "__main__":

    usdc = Currency("USDC")
    eth = Currency("ETH")
    btc = Currency("BTC")

    logger.info("################## Currency Test ###############")
    logger.info(usdc.get_data())
    logger.info(usdc.get_spot_price())

    logger.info("################## Index Test ###############")
    ethUsdcIndex = Index(eth, usdc)


    # Thread to keep increasing price side by side
    thread = Thread(target=run_async_function_in_thread, args=(setgetprice, ethUsdcIndex), daemon=True)
    thread.start()


    logger.info("Other synchronous operations can happen here")
    exp = getExpiryFromTimestamp(1702019809)
    logger.info(exp)
    # time.sleep(7)
    # price = ethUsdcIndex.get_index_price()
    # logger.info(f"Price after 10 seconds is ${price}")

    instrument = FutureContract("ETH-20DEC23", ethUsdcIndex, 1, eth, usdc, 0.1, 1702019809)
    logger.info(instrument.get_specs())

    instrument.start_futures_processes()

    asyncio.run(getPrice(instrument=instrument))