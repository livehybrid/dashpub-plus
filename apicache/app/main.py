from flask import Flask, make_response, request
from flask_restful import Resource, Api, reqparse
#from redis.cluster import RedisCluster as Redis
from rediscluster import RedisCluster as Redis
import redis
from pprint import pprint
import ast
import time
import json
import requests
from random import random
from time import sleep
import os
import re
import base64
import logging
import sys
import traceback
from dotted_dict import DottedDict

app = Flask('__name__')
api = Api(app)

logging.basicConfig()
logger = logging.getLogger('redis')
logger.setLevel(logging.DEBUG)
logger.propagate = True

redis_port = 6379
#redis_host = os.environ.get("DASHPUB_REDIS","redis")
redis_host = os.environ.get("REDIS_HOST","redis")
redis_user = os.environ.get("REDIS_USER", None)
redis_pass = os.environ.get("REDIS_PASS", None)
redis_ssl = os.environ.get("REDIS_SSL", False)

dashpub_host = os.environ.get("DASHPUB_HOST","dashpub")
dashpub_port = os.environ.get("DASHPUB_PORT", 3000)

print(f"Connecting to redis host={redis_host}")

try:
#    startup_nodes = [{redis_host:{"host": redis_host, "port": redis_port}}]
    startup_nodes = [{"host": redis_host, "port": redis_port, "name": redis_host, "username":redis_user, "password":redis_pass}]
    r = Redis(startup_nodes=startup_nodes, decode_responses=True, skip_full_coverage_check=True, password=redis_pass)
#    r = Redis(host=redis_host, port=redis_port, ssl=redis_ssl, password=redis_pass)
except(Exception) as e:
    traceback.print_exc(file=sys.stdout)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
    print(f"Cannot connect to Redis on host={redis_host} port={redis_port} ")
    exit(999)
print("Connected to redis")
@app.route('/', defaults={'u_path': ''})
@app.route('/<path:u_path>')
def catch_all(u_path):
    path = repr(u_path)
    #print(u_path)
    if u_path == "":
        return {'data': "pong"}, 200
    if u_path.startswith("api/"):
        start_time=time.time()
#        print(request.headers.get('x-amzn-oidc-identity'))
        oidc_data=request.headers.get('x-amzn-oidc-data')
        oidc_email = ""
        oidc_name = ""
        if oidc_data:
            try:
                oidc_header, oidc_payload, oidc_signature = oidc_data.split(".")
                oidc_json = json.loads(base64.b64decode(oidc_payload))
                oidc_name = oidc_json['name']
                oidc_email = oidc_json['email']
            except(Exception) as e:
                print(e)
#        print(request.headers.get('x-amzn-oidc-accesstoken'))
        while True:
            redis_data = r.get(u_path)
            if redis_data == None:
                # Go and get the page, but put a flag in Redis whilst we wait...
                redis_data = {}
                redis_data['value'] = "Pending"
                #"Testing - "+str(random())
                r.set(u_path, json.dumps(redis_data))
                r.expire(u_path,60)

                url = f"http://{dashpub_host}:{dashpub_port}/{u_path}"
                resp = requests.get(url, timeout=60)
                cache_time=300
                if 'cache-control' in resp.headers:
                    #log_resp(start_time, u_path, oidc_email, f"Got cache headers={resp.headers['cache-control']}")
                    z = re.match("s-maxage=([0-9]+)", resp.headers['cache-control'])
                    if z:
                        cache_time=z.groups()[0]
                #print(f"Setting TTL to {cache_time}")

                redis_data['value'] = resp.content.decode("utf-8")
                r.set(u_path, json.dumps(redis_data))
                r.expire(u_path,cache_time)
                log_resp(start_time, u_path, oidc_email, f"cache_time={cache_time}")
                response = make_response(redis_data['value'])
                response.headers['cache-control'] = f"s-maxage={cache_time}, stale-while-revalidate"
                response.status_code = 200
                return response
            elif json.loads(redis_data)['value'] == "Pending":
                #print("Waiting for data...sleeping...")
                sleep(1)
            else:
                cache_time = r.ttl(u_path)
                try:
                    redis_data = redis_data.decode("utf-8")
                except:
                    pass
                redis_data = json.loads(redis_data)
                response = make_response(redis_data['value'])
                response.headers['cache-control'] = f"s-maxage={cache_time}, stale-while-revalidate"
                response.status_code = 200
                log_resp(start_time, u_path, oidc_email, f"Sending cached response with ttl={cache_time}")
                return response
    elif u_path.startswith("olly/"):
        start_time=time.time()
#        print(request.headers.get('x-amzn-oidc-identity'))
        oidc_data=request.headers.get('x-amzn-oidc-data')
        oidc_email = ""
        oidc_name = ""
        if oidc_data:
            try:
                oidc_header, oidc_payload, oidc_signature = oidc_data.split(".")
                oidc_json = json.loads(base64.b64decode(oidc_payload))
                oidc_name = oidc_json['name']
                oidc_email = oidc_json['email']
            except(Exception) as e:
                print(e)
#        print(request.headers.get('x-amzn-oidc-accesstoken'))
        while True:
            redis_data = r.get(u_path)
            if redis_data == None:
                # Go and get the page, but put a flag in Redis whilst we wait...
                redis_data = {}
                redis_data['value'] = "Pending"
                #"Testing - "+str(random())
                r.set(u_path, json.dumps(redis_data))
                r.expire(u_path,60)

                url = f"http://olly_api:80/{u_path}"
                resp = requests.get(url, timeout=60)
                cache_time=300
                if 'cache-control' in resp.headers:
                    #log_resp(start_time, u_path, oidc_email, f"Got cache headers={resp.headers['cache-control']}")
                    z = re.match("s-maxage=([0-9]+)", resp.headers['cache-control'])
                    if z:
                        cache_time=z.groups()[0]
                #print(f"Setting TTL to {cache_time}")

                redis_data['value'] = resp.content.decode("utf-8")
                r.set(u_path, json.dumps(redis_data))
                r.expire(u_path,cache_time)
                log_resp(start_time, u_path, oidc_email, f"cache_time={cache_time}")
                response = make_response(redis_data['value'])
                response.headers['cache-control'] = f"s-maxage={cache_time}, stale-while-revalidate"
                response.status_code = 200
                return response
            elif json.loads(redis_data)['value'] == "Pending":
                #print("Waiting for data...sleeping...")
                sleep(1)
            else:
                cache_time = r.ttl(u_path)
                try:
                    redis_data = redis_data.decode("utf-8")
                except:
                    pass
                redis_data = json.loads(redis_data)
                response = make_response(redis_data['value'])
                response.headers['cache-control'] = f"s-maxage={cache_time}, stale-while-revalidate"
                response.status_code = 200
                log_resp(start_time, u_path, oidc_email, f"Sending cached response with ttl={cache_time}")
                return response
    else:
        return {'data':"Unknown Action"}, 404

def log_resp(start_time, uri, user, message):
    resp_time = time.time() - start_time
    print(f"Responding to uri={uri} for user={user} resp_time={resp_time} - {message}")

def main():
    app.run(host="0.0.0.0", threaded=True)  # run our Flask app

if __name__ == '__main__':
    main()


