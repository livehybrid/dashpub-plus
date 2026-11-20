# Alpine (musl) — project preference. Mirror reduces Docker Hub anonymous rate limits in CI.
FROM public.ecr.aws/docker/library/python:3.15-alpine

RUN apk update && apk upgrade -a && apk add --no-cache \
    build-base \
    libffi-dev \
  && rm -rf /var/cache/apk/*


# Create a non-root user and group
RUN addgroup -S apigroup && adduser -S apiuser -G apigroup

# Set working directory
WORKDIR /code

# Copy requirements
COPY ./apicache/requirements.txt /code/requirements.txt

# pip (and the msgpack and urllib3 it vendors) and the base image's old
# setuptools are only needed to install. Nothing imports them at runtime, and
# left in the image they are a standing source of scanner findings, so they
# are taken out once the requirements are in.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt \
  && python -m pip uninstall -y setuptools pip

# Copy application code
COPY ./apicache/app /code/app

# Change ownership of the working directory
RUN chown -R apiuser:apigroup /code

# Switch to non-root user
USER apiuser

# Command
CMD ["gunicorn", "--config", "app/gunicorn_conf.py", "--bind", "0.0.0.0:8080", "app.main:app"]
