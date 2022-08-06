import time

import redis
from flask import Flask
from flask import request

app = Flask(__name__)
redisClient = redis.Redis(host='redis', port=6379)


def get_hit_count():
    retries = 5
    while True:
        try:
            return redisClient.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.get('/')
def hello():
    count = get_hit_count()
    return 'Hello from FABA! I have been seen {} times.\n'.format(count)


@app.get('/ping')
def pong():
    return 'Pong!'


@app.post('/api/queue/push')
def push():
    retries = 5
    while True:
        try:
            request_data = request.get_json()
            name = request_data['name']
            message = request_data['message']

            redisClient.rpush(name, message)
            return 'Pushed on {}'''.format(name)

        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.get('/api/queue/pop')
def pop():
    retries = 5
    while True:
        try:
            name = request.args.get('name')
            return redisClient.lpop(name)

        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)
