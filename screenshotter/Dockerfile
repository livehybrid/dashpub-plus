FROM node:24-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies for Chromium + native module builds (Puppeteer deps)
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    chromium \
    fonts-liberation \
    python3 \
    build-essential \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
  && rm -rf /var/lib/apt/lists/*

# Keep the bundled npm reasonably current — Trivy flags HIGH findings in npm's own dependency tree
# (notably `picomatch` via `tinyglobby`) which are not controlled by this service's tiny dependency set.
RUN npm install -g npm@11.12.1

# npm bundles a nested picomatch used by tinyglobby; bump it explicitly for scanners/audits.
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

# npm bundles a nested picomatch used by tinyglobby; bump it explicitly for scanners/audits.
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

# Set environment variables for Chromium
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
