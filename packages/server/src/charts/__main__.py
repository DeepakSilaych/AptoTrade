import asyncio

from .consumer import get_redpanda_consumer, scheduler
from .utils import get_logger

loop = asyncio.get_event_loop()

logger = get_logger("ChartAndStats")

if __name__ == "__main__":
    ## Initialize Instruments

    consumer = get_redpanda_consumer()
    scheduler.start()
    logger.debug("Started scheduler -------")
    logger.debug("Consuming Trades -------")
    loop.run_until_complete(consumer.consume())

    loop.run_forever()