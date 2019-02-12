FROM ubuntu:latest
MAINTAINER Dmitry Muzyka

RUN apt-get update && \
    apt-get install -y python python-pip && \
    pip install pythonwhois && \
    apt-get remove python-pip -y && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm /var/lib/apt/lists/*.lz4 && \
    mkdir -p /app

ADD . /app
