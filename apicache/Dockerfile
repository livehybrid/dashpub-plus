# Alpine (musl) — project preference. Mirror reduces Docker Hub anonymous rate limits in CI.
FROM public.ecr.aws/docker/library/python:3.13-alpine

RUN apk update && apk upgrade -a && apk add --no-cache \
    build-base \
    libffi-dev \
  && rm -rf /var/cache/apk/*

WORKDIR /code

COPY ./apicache/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install setuptools

COPY ./apicache/app /code/app

CMD ["gunicorn", "--conf", "app/gunicorn_conf.py", "--bind", "0.0.0.0:80", "app.main:app"]
