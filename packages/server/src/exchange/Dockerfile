#!/bin/bash
FROM --platform=linux/amd64 python:3.10

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./ /src/exchange

CMD ["python", "-m", "exchange"]
