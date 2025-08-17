FROM node:24-alpine

# Install system dependencies for Chromium
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    && rm -rf /var/cache/apk/*

# Set environment variables for Chromium
ENV CHROME_BIN=/usr/bin/chromium-browser \
    CHROME_PATH=/usr/lib/chromium/ \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

RUN mkdir -p /app

COPY ./screenshotter/package.json /app/package.json
COPY ./screenshotter/index.js /app/index.js
RUN cd /app && yarn install

COPY ./screenshotter/cron.sh /cron.sh
RUN chmod +x /cron.sh
CMD ["/cron.sh"]
