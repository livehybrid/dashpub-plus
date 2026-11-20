"""The whole chain: browser -> nginx -> cache API -> (stub) dashpub.

Proves nginx/public.conf still routes /api/ to the cache API and everything
else straight to dashpub. Skipped unless NGINX_URL is set, so the cache API
tests can run without nginx.
"""
import json
import os
import urllib.request
import uuid

import pytest

NGINX = os.environ.get("NGINX_URL", "").rstrip("/")
STUB = os.environ.get("STUB_URL", "http://127.0.0.1:3000").rstrip("/")

pytestmark = pytest.mark.skipif(not NGINX, reason="NGINX_URL not set")


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as res:
        return res.status, res.read().decode("utf-8")


def upstream_hits(path):
    return json.loads(fetch(STUB + "/__hits")[1]).get(path, 0)


def test_pages_go_straight_to_dashpub():
    status, body = fetch(NGINX + "/")
    assert status == 200
    assert "Stub dashboards" in body


def test_api_requests_go_through_the_cache():
    path = f"/api/data/{uuid.uuid4().hex}"
    first = json.loads(fetch(NGINX + path)[1])
    second = json.loads(fetch(NGINX + path)[1])
    assert first == {"path": path, "n": 1}
    assert second == first
    # Once: nginx sent both requests to the cache API, not to dashpub.
    assert upstream_hits(path) == 1
