import json

import requests

from .utils import get_logger

logger = get_logger("exchange_rpc")

headers = {"Content-Type": "application/json"}

class ExchangeRpcClient:
    def __init__(self, exchange_rpc):
        self.exchange_rpc = exchange_rpc
        self.exchange_rpc_url = "http://" + self.exchange_rpc
        self.flag = False
        logger.info(exchange_rpc)

    async def health_check(self) -> str:
        payload = json.dumps({"jsonrpc": "2.0", "method": "health_check", "id": 1, "params": {}})

        response = await requests.request(
            "POST", self.exchange_rpc_url, headers=headers, data=payload
        )
        return response.json()
    
    def handle_pricefeed_updates(self, instrument_name, price) -> dict:
        # logger.info("%s --> %s", symbol, aggregate_price)
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "private/handle_pricefeed_updates",
                "params": {
                    "index_name": f"{instrument_name}C",
                    "price": price
                },
                "id": 1,
            }
        )

        try:
            response = requests.request(
                "POST", self.exchange_rpc_url, headers=headers, data=payload
            )
            if not self.flag:
                self.flag = True
                logger.info("******** Exchange Available ******")
            return response.json()
        except Exception as e:
            # logger.error(e)
            logger.debug("Server not available")
