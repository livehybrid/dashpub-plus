FROM python:3.13

RUN apt-get update && apt-get upgrade -y  && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./apicache/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install setuptools

COPY ./apicache/app /code/app

CMD ["gunicorn", "--conf", "app/gunicorn_conf.py", "--bind", "0.0.0.0:80", "app.main:app"] 
