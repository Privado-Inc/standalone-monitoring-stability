FROM adoptopenjdk/openjdk15:latest as build
RUN apt update && apt install -y python3 git curl bash python3.8-venv python3-pip
RUN ln -sf python3 /usr/bin/python

ENV SBT_VERSION 1.7.1
ENV SBT_HOME /usr/local/sbt
ENV PATH ${PATH}:${SBT_HOME}/bin
RUN curl -sL "https://github.com/sbt/sbt/releases/download/v$SBT_VERSION/sbt-$SBT_VERSION.tgz" | gunzip | tar -x -C /usr/local
WORKDIR /app/code

RUN python3 -m venv env
RUN . env/bin/activate
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
COPY . .