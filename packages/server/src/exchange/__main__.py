import asyncio

from exchange.instrument_list import instruments,tradable_assets, currencies, indices
from exchange.Exchange import Exchange
from exchange.utils import get_logger
import time
from pydantic import BaseModel
from threading import Thread
import uvicorn
from fastapi import FastAPI, Request, Response
from jsonrpcserver import Result, Success, async_dispatch, method
from fastapi.middleware.cors import CORSMiddleware
import random
# from aptos_sdk.types import EntryFunctionPayload, TransactionPayload, ChainId


logger = get_logger()

# ECONIA_ADDR = "0xcac06482852f65b5ca07b5b3fdc623750f0535dbe44dfb0b28e7adc492aff99b"
# FAUCET_ADDR = "0x71c55932c638ad8ec8607f55cdc81ef4ba13e7f920524d7f2193ed9db77320bd"
# MANAGER_ADDR = "0x9b0ab538f63666b4901f6bfbe587213e06979ce761342d6025f0d1ce193bab4b"
# COIN_TYPE_APT = f"{FAUCET_ADDR}::apt::APT"
# COIN_TYPE_USDC = f"{FAUCET_ADDR}::usdc::USDC"
# COIN_TYPE_ETH = f"{FAUCET_ADDR}::eth::ETH"
# COIN_TYPE_BTC = f"{FAUCET_ADDR}::btc::BTC"


# payload = EntryFunctionPayload (
#     function=f"{MANAGER_ADDR}::manager::place_limit_order_user_entry",
#     type_arguments=[COIN_TYPE_BTC,COIN_TYPE_USDC]
#     arguments=[1000, 1, ECONIA_ADDR, False, 50, 2000]
# )


# price simulation
async def marketMaker(exchange: Exchange):
    buyOrderIds = {}
    sellOrderIds = {}

    for instrument in exchange.instruments:
        buyOrderIds[instrument.name] = []
        sellOrderIds[instrument.name] = []


    while True:
        for instrument in exchange.instruments:
            index_price = instrument.index.get_index_price()

            # ## Cancel previos buy orders
            for order_id in buyOrderIds[instrument.name]:
                exchange._cancelOrder("0x01", order_id=order_id, instrument_name=instrument.name)

            buyOrderIds[instrument.name] = []
            
            # ## Cancel previos sell orders
            for order_id in sellOrderIds[instrument.name]:
                exchange._cancelOrder("0x02", order_id=order_id, instrument_name=instrument.name)

            sellOrderIds[instrument.name] = []


            # ## place buy limit orders at price and below
            for i in range (1,21):
                order_price = index_price - 0.05*(i-1)
                if(order_price < 0):
                    order_price = 0
                order_id = exchange._marketMakerLimitOrder(from_addr="0x01",instrument_name=instrument.name,buy=True, contracts_size=20*(random.randint(1, 50)),price=order_price)
                buyOrderIds[instrument.name].append(order_id)

            # ## place sell limit orders at price and above
            for i in range (1,21):
                order_id = exchange._marketMakerLimitOrder(from_addr="0x02",instrument_name=instrument.name,buy=False, contracts_size=20*(random.randint(1, 50)),price=index_price+0.05*(i))
                sellOrderIds[instrument.name].append(order_id)

            ## place a sell limit order
            exchange._marketTakerMarketOrder(from_addr="0x02",instrument_name=instrument.name,buy=False,contracts_size=1)

        await asyncio.sleep(5)

async def infinite_run():
    while True:
        time.sleep(50)

def run_async_function_in_thread(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))
    loop.close()






class Data(BaseModel):
    jsonrpc: str
    id: int
    method: str
    params: object | None = None


if __name__=="__main__":
    exchange = Exchange(
        indices=indices,
        currencies=currencies,
        instruments=instruments,
        tradable_assets=tradable_assets
    )

    logger.info("#################### Starting Sample trades ####################")
    thread = Thread(target=run_async_function_in_thread, args=(marketMaker, exchange), daemon=True)
    thread.start()
    # # connections = {}

    app = FastAPI()
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def working():
        return {"status": "success", "response": "Api working"}
    

    @app.post("/api/")
    async def api(data: Data):
        try:
            method = data.method
            params = data.params
            resp = exchange.handle_msg(msg_dict={
                "method": method, 
                "params":params
            })
            return resp
        except Exception as e:
            logger.error(e)
            resp = {
                "status": "failed", "response": "some error occured"
            }
            return resp
    
    uvicorn.run(app,port=8081)

    # logger.info("#################### Initial Pricefeed ####################")
    # logger.info(exchange.price_feed)

    # # asyncio.run(asyncio.create_task(consume()))
    # time.sleep(10)
    # logger.info("#################### Prices after 10 secs ####################")
    # logger.info(exchange.price_feed)

    # logger.info("#################### Initial ticker ####################")
    # logger.info(exchange.tickers)

    # logger.info("#################### Starting price feeds ####################")
    # # thread = Thread(target=run_async_function_in_thread, args=(setPrices, exchange), daemon=True)
    # # thread.start()
    # time.sleep(10)
    # logger.info("#################### Ticker after 10 secs ####################")
    # logger.info(exchange.tickers)


    # logger.info("######################## public/get_trades_by_instrument #####################")
    # resp = exchange.handle_public_msg(msg_dict={
    #     "method": "public/get_trades_by_instrument", 
    #     "params":{ 
    #         "instrument_name":"ETH-08DEC23"
    #     }
    # })
    # logger.info(resp)


    # logger.info("######################## public/get_index_price_names #####################")
    # resp = exchange.handle_public_msg(msg_dict={
    #     "method": "public/get_index_price_names", 
    #     "params":{}
    # })
    # logger.info(resp)


    # logger.info("######################## public/get_currencies #####################")
    # resp = exchange.handle_public_msg(msg_dict={
    #     "method": "public/get_currencies", 
    #     "params":{}
    # })
    # logger.info(resp)

    # logger.info("######################## public/ticker #####################")
    # resp = exchange.handle_public_msg(msg_dict={
    #     "method": "public/ticker", 
    #     "params":{
    #         "instrument_name":"ETH-08DEC23"
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## public/get_index_price #####################")
    # resp = exchange.handle_public_msg(msg_dict={
    #     "method": "public/get_index_price", 
    #     "params":{
    #         "index_name":"BTC/USDC"
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## public/get_all_instrument_names #####################")
    # resp = exchange.handle_public_msg(msg_dict={
    #     "method": "public/get_all_instrument_names", 
    #     "params":{}
    # })
    # logger.info(resp)

    # logger.info("######################## public/get_instruments #####################")
    # resp = exchange.handle_public_msg(msg_dict={
    #     "method": "public/get_instruments", 
    #     "params":{}
    # })
    # logger.info(resp)


    # logger.info("######################## public/get_order_book #####################")
    # resp = exchange.handle_public_msg(msg_dict={
    #     "method": "public/get_order_book", 
    #     "params":{
    #         "instrument_name":"ETH-08DEC23",
    #         "depth": 10
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/deposits #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/deposit", 
    #     "params":{
    #         "from":"0x1234567",
    #         "currency": "USDC",
    #         "amount": 3000000
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_deposits #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_deposits", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/withdrawls #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/withdraw", 
    #     "params":{
    #         "from":"0x1234567",
    #         "currency": "USDC",
    #         "amount": 50000
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_withdrawals #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_withdrawals", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)


    # logger.info("######################## private/get_collateral #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_collateral", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_all_trades #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_all_trades", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_positions #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_positions", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_account_summary #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_account_summary", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_open_orders #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_open_orders", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_account_details of user 1 before #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_account_details", 
    #     "params":{
    #         "from":"0x123457082",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_account_details2 of user 2 before #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_account_details", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)
    # time.sleep(8)
    # logger.info("######################## private/buy #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/buy", 
    #     "params":{
    #         "from":"0x1234567",
    #         "instrument_name": "ETH-20DEC23",
    #         "type": "market",
    #         "amount": 2,
    #         "leverage": 10,
    #         "price": 2000
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/buy2 #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/buy", 
    #     "params":{
    #         "from":"0x1234567",
    #         "instrument_name": "BTC-20DEC23",
    #         "type": "limit",
    #         "amount": 2,
    #         "leverage": 10,
    #         "price": 1900
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/buy3 #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/buy", 
    #     "params":{
    #         "from":"0x1234567",
    #         "instrument_name": "ETH-20DEC23",
    #         "type": "limit",
    #         "amount": 8,
    #         "leverage": 100,
    #         "price": 1800
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/sell #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/sell", 
    #     "params":{
    #         "from":"0x1234567",
    #         "instrument_name": "BTC-20DEC23",
    #         "type": "limit",
    #         "amount": 8,
    #         "leverage": 10,
    #         "price": 2200
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/sell2 #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/sell", 
    #     "params":{
    #         "from":"0x1234567",
    #         "instrument_name": "BTC-20DEC23",
    #         "type": "limit",
    #         "amount": 8,
    #         "leverage": 10,
    #         "price": 2400
    #     }
    # })
    # logger.info(resp)


    # logger.info("######################## private/get_open_orders #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_open_orders", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_positions #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_positions", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/sell #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/sell", 
    #     "params":{
    #         "from":"0x123457082",
    #         "instrument_name": "BTC-20DEC23",
    #         "type": "market",
    #         "amount": 2,
    #         "leverage": 10,
    #     }
    # })
    # logger.info(resp)


    # logger.info("######################## private/get_account_details of user 1 after #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_account_details", 
    #     "params":{
    #         "from":"0x123457082",
    #     }
    # })
    # logger.info(resp)

    # logger.info("######################## private/get_account_details2 of user 2 after #####################")
    # resp = exchange.handle_msg(msg_dict={
    #     "method": "private/get_account_details", 
    #     "params":{
    #         "from":"0x1234567",
    #     }
    # })
    # logger.info(resp)


    # Infinite program run
    asyncio.run(infinite_run())