FROM python:alpine3.19
LABEL maintainer="pzkpw31@gmail.com"

ENV PYTHOUNNBUFFERED=1

WORKDIR /app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN apk update && apk add postgresql-client

COPY . .
RUN mkdir -p /files/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user /files/media
RUN chmod -R 755 /files/media

USER my_user
