FROM python:3.6.8-alpine3.9

MAINTAINER "lsawicki@kbj.com.pl"

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

ENTRYPOINT [ "python" ]

CMD [ "router.py" ]