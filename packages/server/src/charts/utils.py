import logging

LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "level": logging.DEBUG,
}


def get_logger(name="Stats"):
    logging.getLogger("kafka").setLevel(logging.ERROR)
    (logging.getLogger("apscheduler.executors.default")).setLevel(logging.ERROR)
    (logging.getLogger("apscheduler.scheduler")).setLevel(logging.ERROR)
    logging.getLogger("uvicorn").handlers.clear()
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.disabled = True
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True
    logging.basicConfig(**LOGGING_PROPERTIES)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
