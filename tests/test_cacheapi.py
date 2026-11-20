"""Integration tests for the cache API (apicache/app/main.py).

Run against the real image, a real Redis and tests/stub_upstream.py standing
in for dashpub: see tests/docker-compose.yml and .github/workflows/ci.yml.

    CACHEAPI_URL   the cache API          (default http://127.0.0.1:8080)
    STUB_URL       the stub upstream      (default http://127.0.0.1:3000)

Whether a response came from the cache is decided by asking the STUB how many
times it was called. The cache API's own body would say the same thing whether
it cached correctly or forwarded twice and got lucky.

Only pytest is needed; requests are made with urllib.
"""
import json
import os
import time
import urllib.error
import urllib.request
import uuid

import pytest

CACHEAPI = os.environ.get("CACHEAPI_URL", "http://127.0.0.1:8080").rstrip("/")
STUB = os.environ.get("STUB_URL", "http://127.0.0.1:3000").rstrip("/")


def get(url):
    """Return (status, headers, parsed JSON body) without raising on 4xx/5xx."""
    try:
        with urllib.request.urlopen(url, timeout=30) as res:
            return res.status, res.headers, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, err.headers, json.loads(err.read().decode("utf-8"))


def upstream_hits(path):
    return get(STUB + "/__hits")[2].get(path, 0)


@pytest.fixture
def key():
    """A path nobody else has asked for: tests never share a cache entry."""
    return uuid.uuid4().hex


def max_age(headers):
    value = headers.get("cache-control", "")
    assert value.startswith("s-maxage="), f"unexpected cache-control: {value!r}"
    return int(value.split("=", 1)[1].split(",", 1)[0])


def test_root_answers_pong():
    status, _, body = get(CACHEAPI + "/")
    assert status == 200
    assert body == {"data": "pong"}


def test_unknown_route_is_404():
    status, _, body = get(CACHEAPI + "/not-an-api-route")
    assert status == 404, body


def test_first_request_is_forwarded_and_second_is_served_from_cache(key):
    path = f"/api/data/{key}"

    status, headers, first = get(CACHEAPI + path)
    assert status == 200
    assert first == {"path": path, "n": 1}
    assert upstream_hits(path) == 1

    status, headers, second = get(CACHEAPI + path)
    assert status == 200
    assert second == first, "the cached body differs from the one upstream sent"
    assert upstream_hits(path) == 1, "the second request reached upstream: nothing was cached"
    # The upstream said s-maxage=4. The cache must not promise longer than that.
    assert 0 < max_age(headers) <= 4


def test_entry_is_fetched_again_after_upstream_ttl(key):
    path = f"/api/data/{key}"
    assert get(CACHEAPI + path)[2]["n"] == 1
    time.sleep(5.5)  # upstream TTL is 4 s
    status, _, body = get(CACHEAPI + path)
    assert status == 200
    assert body["n"] == 2, "entry outlived the TTL upstream asked for"
    assert upstream_hits(path) == 2


def test_dashboard_list_is_never_cached():
    before = upstream_hits("/api/dashboards")
    first = get(CACHEAPI + "/api/dashboards")
    second = get(CACHEAPI + "/api/dashboards")
    assert first[0] == second[0] == 200
    assert upstream_hits("/api/dashboards") == before + 2
    assert second[2]["n"] == first[2]["n"] + 1


def test_upstream_error_keeps_its_status(key):
    """A 502 from dashpub must not reach the browser as a 200."""
    path = f"/api/broken/{key}"
    status, _, body = get(CACHEAPI + path)
    assert status == 502, f"upstream 502 was served as {status}"
    assert body["error"] == "upstream is broken"


def test_upstream_not_found_keeps_its_status(key):
    path = f"/api/missing/{key}"
    status, _, body = get(CACHEAPI + path)
    assert status == 404, f"upstream 404 was served as {status}"
    assert body["error"] == "Datasource not found"


def test_upstream_error_is_cached_only_briefly(key):
    """An error is remembered long enough to protect upstream from a stampede,
    and no longer: a five-minute-old 502 is an outage of our own making."""
    path = f"/api/broken/{key}"

    status, headers, _ = get(CACHEAPI + path)
    assert status == 502
    assert max_age(headers) <= 15

    status, headers, _ = get(CACHEAPI + path)
    assert status == 502, "the cached copy of an error lost its status"
    assert upstream_hits(path) == 1, "errors are not cached at all"
    assert 0 < max_age(headers) <= 15
