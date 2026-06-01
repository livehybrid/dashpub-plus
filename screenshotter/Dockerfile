# Alpine (musl) — project preference. Mirror reduces Docker Hub anonymous rate limits in CI.
FROM public.ecr.aws/docker/library/node:24-alpine

RUN apk update && apk upgrade -a && apk add --no-cache \
    ca-certificates \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ttf-freefont \
    python3 \
    make \
    g++ \
    pkgconf \
  && rm -rf /var/cache/apk/*

RUN npm install -g npm@11.12.1

RUN mkdir -p /tmp/picomatch-fix && \
    cd /tmp/picomatch-fix && \
    npm init -y >/dev/null 2>&1 && \
    npm install picomatch@^4.0.4 >/dev/null 2>&1 && \
    target="/usr/local/lib/node_modules/npm/node_modules/tinyglobby/node_modules/picomatch" && \
    if [ -d "$target" ]; then \
      rm -rf "$target" && \
      cp -r node_modules/picomatch "$target"; \
    fi && \
    rm -rf /tmp/picomatch-fix

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

ENV CHROME_BIN=/usr/bin/chromium \
    CHROME_PATH=/usr/lib/chromium/ \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

RUN mkdir -p /app

COPY ./screenshotter/package.json /app/package.json
COPY ./screenshotter/index.js /app/index.js
RUN npm install -g node-gyp@^11.5.0
RUN cd /app && npm install --no-audit --no-fund

COPY ./screenshotter/cron.sh /cron.sh
RUN chmod +x /cron.sh
CMD ["/cron.sh"]
