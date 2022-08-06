import time

import redis
from flask import Flask
from flask import request

app = Flask(__name__)
lists = redis.Redis(host='redis', port=6379)


def get_hit_count():
    retries = 5
    while True:
        try:
            return lists.incr('hits')
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


@app.route('/json-example', methods=['POST'])
def json_example():
    request_data = request.get_json()

    language = request_data['language']
    framework = request_data['framework']

    # two keys are needed because of the nested object
    python_version = request_data['version_info']['python']

    # an index is needed because of the array
    example = request_data['examples'][0]

    boolean_test = request_data['boolean_test']

    return '''
           The language value is: {}
           The framework value is: {}
           The Python version is: {}
           The item at index 0 in the example list is: {}
           The boolean value is: {}'''.format(language, framework, python_version, example, boolean_test)


@app.post('/api/queue/push')
def push():
    request_data = request.get_json()
    name = request_data['name']
    message = request_data['message']
    lists.rpush(name, message)
    return 'OK'


@app.get('/api/queue/pop')
def pop():
    name = request.args.get('name')
    return lists.lpop(name)
