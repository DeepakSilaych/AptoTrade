import logging
from datetime import datetime, timezone


# input ->
def getTimestamp(year, month, day, hour, min, sec):
    return datetime(year, month, day, hour, min, sec).timestamp()


# input -> local time
# output -> consider it a UTC time and return its timestamp
def getUTCTimestamp(year, month, day, hour, min, sec):
    return (
        datetime(year, month, day, hour, min, sec)
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )


def getTimestampFromDatetime(datetime):
    return datetime.timestamp()


def getUTCTimestampFromDatetime(datetime):
    return datetime.replace(tzinfo=timezone.utc).timestamp()


def getFormattedDatetime(datetime):
    return datetime.strftime("%Y-%m-%d %H:%M:%S")


def getFormattedDatetimeFromTimestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")


def getNumberOfYearsLeftTillExpiry(expiryTimestamp):
    time1 = datetime.fromtimestamp(expiryTimestamp)
    time2 = datetime.fromtimestamp(
        datetime.now().replace(tzinfo=timezone.utc).timestamp()
    )
    time_difference = time1 - time2
    return time_difference.total_seconds() / 31536000


def getTimeDifferenceInNumberOfYears(timestampA, timestampB):
    time1 = datetime.fromtimestamp(timestampA)
    time2 = datetime.fromtimestamp(timestampB)
    time_difference = time1 - time2
    return time_difference.total_seconds() / 31536000


def current_time():
    return getUTCTimestampFromDatetime(datetime.now())


# Hardcoded to make compatible with other programming languages
def calcIVShock(_daysToExpiry, _maxIVShock):
    if _daysToExpiry == 1:
        return (2.774191114672181086) * _maxIVShock
    elif _daysToExpiry == 2:
        return (2.253343380842655263) * _maxIVShock
    elif _daysToExpiry == 3:
        return (1.995262314968879601) * _maxIVShock
    elif _daysToExpiry == 4:
        return (1.830283560902908193) * _maxIVShock
    elif _daysToExpiry == 5:
        return (1.711769859409705096) * _maxIVShock
    elif _daysToExpiry == 6:
        return (1.620656596692762435) * _maxIVShock
    elif _daysToExpiry == 7:
        return (1.547415577210813198) * _maxIVShock
    elif _daysToExpiry == 8:
        return (1.486652208354811124) * _maxIVShock
    elif _daysToExpiry == 9:
        return (1.435038734166447413) * _maxIVShock
    elif _daysToExpiry == 10:
        return (1.390389170315909340) * _maxIVShock
    elif _daysToExpiry == 11:
        return (1.351196684358816215) * _maxIVShock
    elif _daysToExpiry == 12:
        return (1.316382204334237413) * _maxIVShock
    elif _daysToExpiry == 13:
        return (1.285148668852711344) * _maxIVShock
    elif _daysToExpiry == 14:
        return (1.256892010748450414) * _maxIVShock
    elif _daysToExpiry == 15:
        return (1.231144413344916284) * _maxIVShock
    elif _daysToExpiry == 16:
        return (1.207536818784484880) * _maxIVShock
    elif _daysToExpiry == 17:
        return (1.185773389749696123) * _maxIVShock
    elif _daysToExpiry == 18:
        return (1.165613650690715747) * _maxIVShock
    elif _daysToExpiry == 19:
        return (1.146859710523995303) * _maxIVShock
    elif _daysToExpiry == 20:
        return (1.129346935456855451) * _maxIVShock
    elif _daysToExpiry == 21:
        return (1.112937018100641562) * _maxIVShock
    elif _daysToExpiry == 22:
        return (1.097512744819048451) * _maxIVShock
    elif _daysToExpiry == 23:
        return (1.082973988494612448) * _maxIVShock
    elif _daysToExpiry == 24:
        return (1.069234599991188026) * _maxIVShock
    elif _daysToExpiry == 25:
        return (1.056219968439258170) * _maxIVShock
    elif _daysToExpiry == 26:
        return (1.043865085949640968) * _maxIVShock
    elif _daysToExpiry == 27:
        return (1.032112997428190034) * _maxIVShock
    elif _daysToExpiry == 28:
        return (1.020913547691436184) * _maxIVShock
    elif _daysToExpiry == 29:
        return (1.010222360469755772) * _maxIVShock
    elif _daysToExpiry == 30:
        return (1.000000000000000000) * _maxIVShock


# def checkDelta(testResult, actualResult):
#     print("Actual Result -> ", actualResult)
#     print("Test Result -> ", testResult)
#     print("Delta ->", testResult - actualResult)

LOGGING_PROPERTIES = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "level": logging.DEBUG,
}


def get_logger(name="SyndrRiskExchange"):
    logging.getLogger("kafka").setLevel(logging.ERROR)
    (logging.getLogger("apscheduler.executors.default")).setLevel(logging.ERROR)
    (logging.getLogger("apscheduler.scheduler")).setLevel(logging.ERROR)
    (logging.getLogger("numba.core.interpreter")).setLevel(logging.ERROR)
    (logging.getLogger("numba.core.byteflow")).setLevel(logging.ERROR)
    (logging.getLogger("numba.core.ssa")).setLevel(logging.ERROR)
    logging.getLogger("uvicorn").handlers.clear()
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.disabled = True
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True

    logging.basicConfig(**LOGGING_PROPERTIES)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
