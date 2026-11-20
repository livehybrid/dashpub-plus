# Tests

Everything here runs in `.github/workflows/ci.yml` on every pull request,
with no secrets.

| Check | What it proves |
| --- | --- |
| Cache API (standalone), Cache API (cluster) | The real `apicache` image, against a real Redis in each mode, in front of a stub dashpub: a result is forwarded once and then served from cache, the upstream TTL is respected, the dashboard list is never cached, and an upstream error keeps its status and is cached for 15 seconds at most. Also the whole chain through the real nginx image and `nginx/public.conf`. |
| Screenshotter | The real `screenshotter` image takes one round of screenshots of the stub and leaves a full-HD JPEG for the index and for each linked dashboard, and nothing for links outside the site. |
| Image scan | Trivy on the two images. Reported, not required: a new CVE in a base image is not the pull request's fault. |

`stub_upstream.py` stands in for dashpub. It counts requests per path, and the
tests decide "was this cached?" by asking **it**, not the cache API.

## Run it by hand

```bash
export COMPOSE_FILE=tests/docker-compose.yml REDIS_MODE=standalone REDIS_CLUSTER=false
docker compose up -d --build dashpub redis-standalone app nginx
pip install pytest
CACHEAPI_URL=http://127.0.0.1:8080 STUB_URL=http://127.0.0.1:3000 NGINX_URL=http://127.0.0.1:3001 pytest tests -v
docker compose down
```

For cluster mode use `REDIS_MODE=cluster REDIS_CLUSTER=true` and `redis-cluster`.

## Dependency updates

`dependabot-auto-merge.yml` turns on auto-merge for Dependabot pull requests
that are not a major version bump; GitHub merges them when the required checks
(the first three rows above) pass. This relies on branch protection on
`develop` requiring those checks. Without it `gh pr merge --auto` merges
immediately, so if the protection is ever removed, disable that workflow first.

A merge made by auto-merge does not trigger other workflows, so the publish
workflow does not run for it. `publish-catch-up.yml` checks hourly whether the
head of `develop` has a publish run and starts one if not.

What this does not cover: a real dashpub and a real Splunk. That is the render
suite in the dashpub repository, which also asserts the `.url2png-cheese`
marker the screenshotter waits for.
