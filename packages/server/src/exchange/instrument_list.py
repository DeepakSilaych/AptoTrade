# import asyncio
import logging
import sys

# from exchange.api.app.webSocketClient import WebSocketClient
from exchange.markets.Currency import Currency
from exchange.markets.Index import Index

from exchange.markets.Instrument import FutureContract, PerpContract

logging.basicConfig(level=logging.ERROR, stream=sys.stdout)



usdc = Currency("USDC")
eth = Currency("ETH")
btc = Currency("BTC")
apt = Currency("APT")

# Initialize Indices
btc_usdc_index = Index(btc, usdc)
eth_usdc_index = Index(eth, usdc)
apt_usdc_index = Index(apt, usdc)


tradable_assets = [btc, eth, apt]
currencies = [usdc]
indices = [btc_usdc_index, eth_usdc_index, apt_usdc_index]
instruments = [
    FutureContract(
        name="BTC-20DEC23",
        index=btc_usdc_index,
        contract_size=1,
        base_currency=btc,
        quote_currency=usdc,
        settlement_period="daily",
        tick_size=0.01,
        expiration=1703075400,
        max_leverage=50
    ),
    FutureContract(
        name="ETH-20DEC23",
        index=eth_usdc_index,
        contract_size=1,
        base_currency=eth,
        quote_currency=usdc,
        settlement_period="daily",
        tick_size=0.01,
        expiration=1703075400,
        max_leverage=50
    ),
    FutureContract(
        name="APT-20DEC23",
        index=apt_usdc_index,
        contract_size=1,
        base_currency=apt,
        quote_currency=usdc,
        settlement_period="daily",
        tick_size=0.01,
        expiration=1703075400,
        max_leverage=50
    )
]
