import logging

LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "level": logging.DEBUG,
}


def get_logger(name="WebsocketApi"):
    logging.getLogger("kafka").setLevel(logging.ERROR)
    logging.basicConfig(**LOGGING_PROPERTIES)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logging.getLogger("uvicorn").handlers.clear()
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.disabled = True
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True

    return logger
