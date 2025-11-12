FROM python:3.13-alpine

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*


# Create a non-root user and group
RUN addgroup -S apigroup && adduser -S apiuser -G apigroup

# Set working directory
WORKDIR /code

# Copy requirements
COPY ./apicache/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install setuptools

# Copy application code
COPY ./apicache/app /code/app

# Change ownership of the working directory
RUN chown -R apiuser:apigroup /code

# Switch to non-root user
USER apiuser

# Command
CMD ["gunicorn", "--config", "app/gunicorn_conf.py", "--bind", "0.0.0.0:8080", "app.main:app"]
