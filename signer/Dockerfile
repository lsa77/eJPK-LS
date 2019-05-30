FROM ubuntu:latest

MAINTAINER "lsawicki@kbj.com.pl"

WORKDIR /app
COPY . /app

RUN apt update -y
RUN apt install openssl -y
RUN apt install libssl-dev -y
EXPOSE 8000

ENTRYPOINT ["./rocket1" ]