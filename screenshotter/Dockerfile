FROM node:25-alpine

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

    # Manually patch glob in system npm to fix vulnerabilities
RUN mkdir -p /tmp/glob-fix && \
cd /tmp/glob-fix && \
npm init -y && \
npm install glob@^10.5.0 && \
rm -rf /usr/local/lib/node_modules/npm/node_modules/glob && \
cp -r node_modules/glob /usr/local/lib/node_modules/npm/node_modules/ && \
if [ -d "/usr/local/lib/node_modules/npm/node_modules/node-gyp/node_modules/glob" ]; then \
  rm -rf /usr/local/lib/node_modules/npm/node_modules/node-gyp/node_modules/glob && \
  cp -r node_modules/glob /usr/local/lib/node_modules/npm/node_modules/node-gyp/node_modules/; \
fi && \
rm -rf /tmp/glob-fix

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
