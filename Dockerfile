# Use ./setup.sh script to build image

FROM python:3.12-alpine3.21
RUN apk add git

ENV INSTALL_PATH=/home/basic
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD archive.tgz $INSTALL_PATH
