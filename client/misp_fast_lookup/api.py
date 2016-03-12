#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False
import json


def __prepare_request(cache_url, query):
    headers = {'content-type': 'application/json'}
    r = requests.post(cache_url, data=json.dumps(query), headers=headers)
    return r.json()


def search(cache_url, misp_url, auth_key, value=None, hash_value=None, quiet=False, verbose=False, return_eid=False):
    if not HAVE_REQUESTS:
        raise Exception('Please install requests package.')

    query = {'method': 'search'}
    query.update({'authkey': auth_key, 'hash_value': hash_value, 'value': value, 'quiet': quiet, 'return_eid': return_eid})
    response = __prepare_request(cache_url, query)
    if quiet or not verbose:
        return response
    else:
        return [['{}/events/view/{}'.format(misp_url, uuid) for uuid in uuids] for uuids in response]
