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

    
    def get_orderbook(self, instrument_name) -> dict:
        # logger.info("%s --> %s", symbol, aggregate_price)
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "public/get_order_book",
                "params": {
                    "instrument_name": instrument_name,
                    "depth": 10
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


    def get_account(self, address) -> dict:
        # logger.info("%s --> %s", symbol, aggregate_price)
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "private/get_account_details",
                "params":{
                    "from": f"{address}",
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


