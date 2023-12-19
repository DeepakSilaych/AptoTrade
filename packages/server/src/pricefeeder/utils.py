import logging

LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "level": logging.DEBUG,
}


def get_logger(name):
    logging.getLogger("kafka").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.basicConfig(**LOGGING_PROPERTIES)
    logger = logging.getLogger(name)
    # logger.setLevel(logging.DEBUG)
    return logger
