FROM python:3.8

WORKDIR /usr/cortex
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY cortex ./cortex
