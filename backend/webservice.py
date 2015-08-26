#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, json, request
from redis import StrictRedis
from Crypto.Hash import SHA

from config import redis_socket

app = Flask(__name__)
app.debug = True

authorized_methods = ['search']


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) == type(set()):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


@app.route('/json', methods=['POST'])
def __entry_point():
    """
        Function called when an query is made on /json. Expects a JSON
        object with at least a 'method' entry.
    """
    method = request.json.get('method')
    if method is None:
        return json.dumps({'error': 'No method provided.'})
    if method not in authorized_methods:
        # unauthorized query
        return json.dumps({'error': 'Unauthorized method.'})
    fct = globals().get(method)
    if fct is None:
        # unknown method, the method is authorized, but does not exists...
        return json.dumps({'error': 'Unknown method.'})
    try:
        result = fct(request.json)
        return json.dumps(result, cls=SetEncoder)
    except Exception as e:
        return json.dumps({'error': 'Something went wrong. \n{}'.format(e)})


def search(request):
    if request.get('value'):
        hash_value = SHA.new(request.get('value')).hexdigest()
    else:
        hash_value = request.get('hash_value')
    if hash_value is None:
        return json.dumps({})
    r = StrictRedis(unix_socket_path=redis_socket)
    known_uuids = r.smembers(hash_value)
    to_return = {'known': (len(known_uuids) != 0)}
    if not request.get('quiet'):
        to_return['uuids'] = known_uuids
    return to_return

if __name__ == '__main__':
    app.run()
