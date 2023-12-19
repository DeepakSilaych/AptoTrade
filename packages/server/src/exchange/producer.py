"""
Produce responses and subscription data to respective consumers
"""
import json
import os
import time
from dataclasses import dataclass

from kafka import KafkaProducer

from exchange.utils import get_logger

logger = get_logger("exchange producer")


@dataclass
class ProducerConfig:
    """a Dataclass for storing our producer configs"""

    # the Redpanda bootstrap servers will be pulled from the
    # REDPANDA_BROKERS environment variable. Ensure this is set
    # before running the code
    bootstrap_servers = 'localhost:9092'
    logger.info(os.getenv("REDPANDA_BROKERS", ""))
    topic = "responses"


def connect_producer():
    producer = None
    config = ProducerConfig()
    try:
        producer = KafkaProducer(
            bootstrap_servers=config.bootstrap_servers,
            key_serializer=str.encode,
            value_serializer=lambda m: json.dumps(m).encode(),
        )
        logger.info("########################## Connection to kafka successful ###################")
        return producer
    except Exception as e:
        time.sleep(1)
        logger.debug("Retrying connection with broker")
        producer = connect_producer()
        return producer


class ExchangeProducer:
    def __init__(self, config: ProducerConfig):
        # instantiate a Kafka producer client. This client is compatible
        # with Redpanda brokers
        self.client = connect_producer()
        self.topic = config.topic

    def produce(self, message, topic=None):
        """Produce a single message to a Redpanda topic"""
        try:
            topic = topic if topic is not None else self.topic
            # send a message to the topic
            future = self.client.send(topic, key="exchange_server", value=message)

            # this line will block until the message is sent (or timeout).
            _ = future.get(timeout=10)
            # print(f"Successfully produced message to topic: {self.topic}")
        except Exception as e:
            logger.info("Could not produce to %s --> Got Error: %s", topic, e)
            raise

    def produce_multiple(self, messages, topic=None):
        """Produce a single message to a Redpanda topic"""
        try:
            # send a message to the topic
            # produce asynchronously
            topic = topic if topic is not None else self.topic

            for msg in messages:
                self.client.send(topic, key="exchange_server", value=msg)

            # this line will block until the message is sent (or timeout).
            self.client.flush()
            # print(f"Successfully produced all messages to topic: {self.topic}")
        except Exception as e:
            logger.info("Could not produce to %s --> Got Error: %s", topic, e)
            raise


# create a config and producer instance
def get_redpanda_producer():
    config = ProducerConfig()
    return ExchangeProducer(config)
