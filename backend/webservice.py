#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, json, request
from connector import MispRedisConnector


app = Flask(__name__)
app.debug = True

authorized_methods = ['search']

connector = MispRedisConnector()


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
    if not request.get('authkey'):
        return json.dumps({'error': 'The authkey is required.'})
    return connector.search(request.get('authkey'), request.get('value'),
                            request.get('hash_value'), request.get('quiet'))


if __name__ == '__main__':
    app.run()
