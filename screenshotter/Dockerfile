# Alpine (musl) — project preference. Mirror reduces Docker Hub anonymous rate limits in CI.
FROM public.ecr.aws/docker/library/node:26-alpine

RUN apk update && apk upgrade -a && apk add --no-cache \
    ca-certificates \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ttf-freefont \
  && rm -rf /var/cache/apk/*

ENV CHROME_BIN=/usr/bin/chromium \
    CHROME_PATH=/usr/lib/chromium/ \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_SKIP_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

RUN mkdir -p /app

COPY ./screenshotter/package.json /app/package.json
COPY ./screenshotter/index.js /app/index.js

# npm is needed to install and never again: the container only ever runs
# `node /app/index.js`. Removing it removes npm's own bundled dependencies
# (tar, brace-expansion, pacote, sigstore, ...), which is where every scanner
# finding in this image has come from. That replaces the previous approach of
# pinning an npm release and patching its bundled packages one by one.
RUN cd /app && npm install --no-audit --no-fund --omit=dev \
  && npm cache clean --force \
  && rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack \
            /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack /root/.npm

COPY ./screenshotter/cron.sh /cron.sh
RUN chmod +x /cron.sh
CMD ["/cron.sh"]
