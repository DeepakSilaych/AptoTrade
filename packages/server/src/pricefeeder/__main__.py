#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import os
import signal
import sys
from typing import Any, List
from pythclient.pythaccounts import PythPriceAccount  # noqa
from pythclient.pythclient import PythClient  # noqa
from pythclient.ratelimit import RateLimit  # noqa
from pythclient.utils import get_key  # noqa
from loguru import logger
from pricefeeder.exchange_rpc_client import ExchangeRpcClient


logger.enable("pythclient")

RateLimit.configure_default_ratelimit(overall_cps=9, method_cps=3, connection_cps=3)

to_exit = False

exchange_rpc_client = ExchangeRpcClient("127.0.0.1:8081/api")

def set_to_exit(sig: Any, frame: Any):
    global to_exit
    to_exit = True


signal.signal(signal.SIGINT, set_to_exit)

async def getPythPriceFeed(
    callback=None, supported_symbols=["ETH/USD", "BTC/USD", "APT/USD"]
):
    await asyncio.sleep(15)
    supported_pyth_symbols = list(
        map(lambda symbol: "Crypto." + symbol, supported_symbols)
    )
    global to_exit
    use_program = len(sys.argv) >= 2 and sys.argv[1] == "program"
    v2_first_mapping_account_key = get_key("pythnet", "mapping")
    v2_program_key = get_key("pythnet", "program")
    async with PythClient(
        first_mapping_account_key=v2_first_mapping_account_key,
        program_key=v2_program_key if use_program else None,
        solana_endpoint="https://pythnet.rpcpool.com",  # replace with the relevant cluster endpoints
        solana_ws_endpoint="wss://pythnet.rpcpool.com",  # replace with the relevant cluster endpoints
    ) as c:
        await c.refresh_all_prices()
        products = await c.get_products()
        all_prices: List[PythPriceAccount] = []
        for p in products:
            if p.symbol not in supported_pyth_symbols:
                continue
            prices = await p.get_prices()
            for _, pr in prices.items():
                all_prices.append(pr)

        ws = c.create_watch_session()
        await ws.connect()

        print("Subscribing to all prices")
        for account in all_prices:
            await ws.subscribe(account)

        print("Subscribed!")
        while True:
            if to_exit:
                break
            update_task = asyncio.create_task(ws.next_update())
            while True:
                if to_exit:
                    update_task.cancel()
                    break
                done, _ = await asyncio.wait({update_task}, timeout=1)
                if update_task in done:
                    pr = update_task.result()
                    if isinstance(pr, PythPriceAccount):
                        assert pr.product

                        exchange_rpc_client.handle_pricefeed_updates(
                            str(pr.product.symbol).split(".")[1],
                            round(pr.aggregate_price, 2),
                        )
                        # print(str(pr.product.symbol).split(".")[1])
                        # print(pr.aggregate_price)
                        # print(type(pr.aggregate_price))
                        # print('-------------------------------')
                    break

        print("Unsubscribing...")
        if use_program:
            await ws.program_unsubscribe(v2_program_key)
        else:
            for account in all_prices:
                await ws.unsubscribe(account)
        await ws.disconnect()
        print("Disconnected")


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(getPythPriceFeed())

    loop.run_forever()
