FROM ubuntu:latest
#FROM balenalib/rpi-raspbian:latest

ENV LC_CTYPE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV PYTHONIOENCODING utf-8

COPY . /app
WORKDIR /app

RUN apt-get update

RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD [ "python3", "app.py" ]