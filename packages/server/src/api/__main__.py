import asyncio
import json
import os
import time
from aiokafka import AIOKafkaConsumer
import uvicorn
from fastapi import Depends, FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from jsonrpcserver import Error, Result, Success, async_dispatch, method
from uvicorn import Config, Server
from api.utils import get_logger
from api.exchange_rpc_client import ExchangeRpcClient
from api.producer import get_redpanda_producer

# logger = get_logger()

ticker_connections = {}
index_connections = {}
orderbook_connections = {}
chart_connections = {}
history_connections = {}
account_connections = {}
exchange_rpc_client = ExchangeRpcClient("127.0.0.1:8081/api")
producer = get_redpanda_producer()

from fastapi import FastAPI, WebSocket
app = FastAPI()

@app.websocket("/ticker/{client_id}")
async def ticker_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    ticker_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
    except Exception as e:
        # Handle disconnection
        del ticker_endpoint[client_id]


@app.websocket("/chart/{client_id}")
async def chart_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    chart_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
    except Exception as e:
        # Handle disconnection
        del chart_connections[client_id]


@app.websocket("/index/{client_id}")
async def index_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    index_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
    except Exception as e:
        # Handle disconnection
        del index_connections[client_id]




@app.websocket("/orderbook/{client_id}")
async def orderbook_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    orderbook_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
    except Exception as e:
        # Handle disconnection
        del orderbook_connections[client_id]


@app.websocket("/account/{client_id}")
async def account_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    account_connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
    except Exception as e:
        # Handle disconnection
        del account_connections[client_id]



# @app.websocket("/history/{client_id}/{from}/{to}")
# async def historical_data(websocket: WebSocket, client_id: str):
#     await websocket.accept()
#     history_connections[client_id] = websocket  
#     params1 = {

#     }  
#     producer.produce(
#         {
#             "req_id": client_id,
#             "method": "public/get_tradingview_chart_data",
#             "params": params1,
#             "api_in": time.time(),
#         },
#                 "chartReqs",
#             )
#     try:
#         while True:
#             data = await websocket.receive_text()
#             # print(req)
#     except Exception as e:
#         del historical_data[client_id]



async def consume():
    consumer = AIOKafkaConsumer('public_subs', bootstrap_servers='localhost:9092')
    await consumer.start()
    try:
        async for msg in consumer:
            # Process message and send to relevant WebSocket connections
            # logger.info(msg.value)
            data = json.loads((msg.value).decode('utf-8'))
            if("price_index" in str(data["channel"])):
                for client_id, ws in index_connections.items():
                    try:
                        await ws.send_text(json.dumps(data))
                    except:
                        pass
            if("ticker" in str(data["channel"])):
                for client_id, ws in ticker_connections.items():
                    try:
                        await ws.send_text(json.dumps(data))
                    except:
                        pass
            if("chart.trade" in str(data["channel"])):
                for client_id, ws in chart_connections.items():
                    try:
                        await ws.send_text(json.dumps(data))
                    except:
                        pass
    finally:
        await consumer.stop()


# async def consusme_responses():
#     consumer = AIOKafkaConsumer('responses', bootstrap_servers='localhost:9092')
#     await consumer.start()
#     try:
#         async for msg in consumer:
#             data = json.loads((msg.value).decode('utf-8'))
#             req_id= data["req_id"]
#             try:
#                 ws = historical_data[req_id]
#                 await ws.send_text(json.dumps(data))
#             except:
#                 pass
#     finally:
#         await consumer.stop()



async def get_orderbook():
    while True:
        ethOrderbook = exchange_rpc_client.get_orderbook(instrument_name="ETH-20DEC23")
        btcOrderbook = exchange_rpc_client.get_orderbook(instrument_name="BTC-20DEC23")
        aptOrderbook = exchange_rpc_client.get_orderbook(instrument_name="APT-20DEC23")
        # print(ethOrderbook)
        for client_id, ws in orderbook_connections.items():
            try:
                await ws.send_text(json.dumps({"ethOrderbook": ethOrderbook, "btcOrderbook": btcOrderbook, "aptOrderbook":aptOrderbook}))
            except:
                pass
        await asyncio.sleep(2)


async def get_account():
    while True:
        # ethOrderbook = exchange_rpc_client.get_orderbook(instrument_name="ETH-20DEC23")
        # btcOrderbook = exchange_rpc_client.get_orderbook(instrument_name="BTC-20DEC23")
        # print(ethOrderbook)
        for client_id, ws in account_connections.items():
            try:
                account = exchange_rpc_client.get_account(client_id)
                await ws.send_text(json.dumps(account))
            except:
                pass
        await asyncio.sleep(2)


@app.on_event("startup")
async def start_consumer():
    asyncio.create_task(consume())
    asyncio.create_task(get_orderbook())
    asyncio.create_task(get_account())



if __name__ == "__main__":
    uvicorn.run(app,port=8082)
