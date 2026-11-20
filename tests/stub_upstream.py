#!/usr/bin/env python3
"""A stand-in for dashpub, for testing the services that sit in front of it.

Standard library only. It answers the handful of routes the cache API and the
screenshotter use, and counts every request per path so a test can tell
"served from cache" from "asked upstream again" by looking at the upstream,
not at the thing under test.

    /                     index page linking to two dashboards
    /dash_one, /dash_two  a page that becomes "ready for screenshot" after 500 ms
    /api/data/<id>        JSON with a per-path request counter, s-maxage=4
    /api/dashboards       JSON with a counter (a path the cache API never caches)
    /api/broken/<id>      HTTP 502 with a JSON error body
    /api/missing/<id>     HTTP 404 with a JSON error body
    /__hits               the counters, as JSON
    /__reset              zero the counters
"""
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HITS = {}
LOCK = threading.Lock()

INDEX = """<!doctype html><html><head><title>stub dashpub</title></head><body>
<h1>Stub dashboards</h1>
<a href="/dash_one">Dash one</a> <a href="/dash_two">Dash two</a>
<a href="https://example.invalid/elsewhere">Not ours</a>
</body></html>"""

DASHBOARD = """<!doctype html><html><head><title>{name}</title></head>
<body style="background:#204060;color:#fff;font:48px sans-serif">
<h1>stub dashboard {name}</h1><div style="width:900px;height:500px;background:#c06030"></div>
<script>setTimeout(function () {{
  var d = document.createElement('div'); d.className = 'url2png-cheese'; document.body.appendChild(d);
}}, 500);</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # one line per request is enough
        print("stub %s" % (fmt % args), flush=True)

    def send(self, status, body, content_type="application/json", headers=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/__hits":
            with LOCK:
                return self.send(200, json.dumps(HITS))
        if path == "/__reset":
            with LOCK:
                HITS.clear()
            return self.send(200, "{}")

        with LOCK:
            HITS[path] = HITS.get(path, 0) + 1
            n = HITS[path]

        if path == "/":
            return self.send(200, INDEX, "text/html")
        if path in ("/dash_one", "/dash_two"):
            return self.send(200, DASHBOARD.format(name=path[1:]), "text/html")
        if path.startswith("/api/data/"):
            return self.send(
                200,
                json.dumps({"path": path, "n": n}),
                headers={"cache-control": "s-maxage=4, stale-while-revalidate"},
            )
        if path == "/api/dashboards":
            return self.send(200, json.dumps({"dashboards": [], "n": n}))
        if path.startswith("/api/broken/"):
            return self.send(502, json.dumps({"error": "upstream is broken", "n": n}))
        if path.startswith("/api/missing/"):
            return self.send(404, json.dumps({"error": "Datasource not found", "n": n}))
        return self.send(404, json.dumps({"error": "no such route", "path": path}))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    print("stub upstream listening on %d" % port, flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
