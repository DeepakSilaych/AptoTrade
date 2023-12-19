"""
Consume requests from API server
"""
import json
import os
import time
from collections import OrderedDict
from dataclasses import dataclass

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from kafka import KafkaConsumer

from .producer import get_redpanda_producer
from .utils import get_logger

logger = get_logger("Trades Consumer")
frontier = int(pd.Timestamp.utcnow().floor("5S").timestamp() * 1000)  # floor to 15 secs
producer = get_redpanda_producer()


all_ohlc_data = {}
row_flags = {}
start_flags = {}


def on_close():
    global row_flags
    global frontier
    global all_ohlc_data
    global start_flags

    for inst_name in row_flags:
        if row_flags[inst_name] and start_flags[inst_name]:

            latest_close_price = float(all_ohlc_data[inst_name]["close"].iloc[-1])
            row = {
                "time": frontier,
                "open": latest_close_price,
                "high": latest_close_price,
                "low": latest_close_price,
                "close": latest_close_price,
                "volume": 0,
            }
            all_ohlc_data[inst_name] = pd.concat(
                [
                    all_ohlc_data[inst_name],
                    pd.DataFrame.from_records([row]),
                ]
            )
            producer.produce(
                {
                    "channel": "chart.trade." + inst_name,
                    "data": row,
                },
                "public_subs",
            )
        row_flags[inst_name] = True

    frontier = int(pd.Timestamp.utcnow().floor("5S").timestamp() * 1000)
    # logger.info(all_ohlc_data)


scheduler = BackgroundScheduler()
scheduler.configure(timezone="utc")
scheduler.add_job(on_close, trigger="cron", second="*/5", id="onClose")

@dataclass
class ConsumerConfig:
    bootstrap_servers = 'localhost:9092'
    topic = ["trades", "chartReqs"]
    consumer_group = "trades-consumer"
    auto_offset_reset = "latest"

def connect_consumer():
    consumer = None
    config = ConsumerConfig()
    try:
        consumer = KafkaConsumer(
            *config.topic,
            bootstrap_servers=config.bootstrap_servers,
            auto_offset_reset=config.auto_offset_reset,
            api_version=(2, 3, 0),
            fetch_max_bytes=209715200,
            max_partition_fetch_bytes=6291456,
            fetch_max_wait_ms=10
            # value_deserializer=lambda m: json.loads(m.decode())
        )
        return consumer
    except Exception:
        time.sleep(1)
        logger.debug("Retrying connection with broker")
        consumer = connect_consumer()
        return consumer
    

class TradesConsumer:
    def __init__(self, config: ConsumerConfig):
        self.client = connect_consumer()
        self.topic = config.topic

        #  instrument_name : data

    async def consume(self):
        global start_flags
        global row_flags
        global all_ohlc_data
        """Consume messages from a Redpanda topic"""
        try:
            for msg in self.client:
                msg_dict = json.loads(msg.value.decode())
                # logger.debug("Got request %s", msg_dict)
                if msg.topic == "chartReqs":
                    if msg_dict["params"]["instrument_name"] not in all_ohlc_data:
                        all_ohlc_data[
                            msg_dict["params"]["instrument_name"]
                        ] = pd.DataFrame(
                            [[frontier, 0, 0, 0, 0, 0]],
                            columns=["time", "open", "high", "low", "close", "volume"],
                        )
                        # logger.debug(
                        #     all_ohlc_data[msg_dict["params"]["instrument_name"]]
                        # )
                        row_flags[msg_dict["params"]["instrument_name"]] = True
                        start_flags[msg_dict["params"]["instrument_name"]] = True

                    inst_ohlc_data = all_ohlc_data[
                        msg_dict["params"]["instrument_name"]
                    ]

                    From = msg_dict["params"]["from"]
                    To = msg_dict["params"]["to"]

                    resampled_df = inst_ohlc_data.copy()

                    resampled_df["ctime"] = pd.to_datetime(
                        resampled_df["time"] / 1000, unit="s"
                    )
                    resampled_df = resampled_df.set_index("ctime")

                    resolution = msg_dict["params"]["resolution"]
                    try:
                        # if resolution is in minutes, so first check if it is an integer, and them add min to it
                        resolution = str(int(resolution)) + "min"

                    except Exception:
                        # if resolution is not an integer, then proceed with the input resolution
                        pass

                    resampled_df = resampled_df.resample(resolution).agg(
                        OrderedDict(
                            [
                                ("time", "first"),
                                ("open", "first"),
                                ("high", "max"),
                                ("low", "min"),
                                ("close", "last"),
                                ("volume", "sum"),
                            ]
                        )
                    )

                    responses = resampled_df[
                        (resampled_df.index >= pd.to_datetime(From / 1000, unit="s"))
                        & (resampled_df.index <= pd.to_datetime(To / 1000, unit="s"))
                    ].to_dict(orient="records")

                    producer.produce(
                        {
                            "req_id": msg_dict["req_id"],
                            "result": responses,
                        },
                        "responses",
                    )

                elif msg.topic == "trades":

                    if msg_dict["instrument_name"] not in all_ohlc_data:
                        all_ohlc_data[msg_dict["instrument_name"]] = pd.DataFrame(
                            columns=["time", "open", "high", "low", "close", "volume"]
                        )
                        start_flags[msg_dict["instrument_name"]] = True
                        row_flags[msg_dict["instrument_name"]] = True
                    await self.process_tick(
                        msg_dict["instrument_name"],
                        msg_dict["trade"],
                    )

        except Exception as e:
            print(f"Could not consume from topic: {self.topic}, got error {e}")
            raise

    async def process_tick(self, instrument_name, tick):
        global frontier
        global row_flags
        global all_ohlc_data

        if row_flags[instrument_name] and (int(tick["timestamp"] / 1000) >= frontier):
            op = tick["price"]
            hi = tick["price"]
            lo = tick["price"]
            cl = tick["price"]
            vol = tick["size"]
            row = {
                "time": frontier,
                "open": op,
                "high": hi,
                "low": lo,
                "close": cl,
                "volume": vol,
            }

            all_ohlc_data[instrument_name] = pd.concat(
                [
                    all_ohlc_data[instrument_name],
                    pd.DataFrame.from_records([row]),
                ]
            )
            producer.produce(
                {
                    "channel": "chart.trade." + instrument_name,
                    "data": row,
                },
                "public_subs",
            )
            row_flags[instrument_name] = False
        else:
            # high
            if tick["price"] > all_ohlc_data[instrument_name].iloc[-1, 2]:
                all_ohlc_data[instrument_name].iloc[-1, 2] = tick["price"]
            # low
            elif tick["price"] < all_ohlc_data[instrument_name].iloc[-1, 3]:
                all_ohlc_data[instrument_name].iloc[-1, 3] = tick["price"]

            # close
            all_ohlc_data[instrument_name].iloc[-1, 4] = tick["price"]
            # volume
            all_ohlc_data[instrument_name].iloc[-1, 5] += tick["size"]
            producer.produce(
                {
                    "channel": "chart.trade." + instrument_name,
                    "data": all_ohlc_data[instrument_name].iloc[-1].to_dict(),
                },
                "public_subs",
            )


def get_redpanda_consumer():
    config = ConsumerConfig()
    return TradesConsumer(config)
