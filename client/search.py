#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import argparse

cache_url = 'http://127.0.0.1:5000/json'
misp_url = 'https://misppriv.circl.lu'


def __prepare_request(query):
    headers = {'content-type': 'application/json'}
    r = requests.post(cache_url, data=json.dumps(query), headers=headers)
    return r.json()


def search(auth_key, value=None, hash_value=None, quiet=False, verbose=False, return_eid=False):
    query = {'method': 'search'}
    query.update({'authkey': auth_key, 'hash_value': hash_value, 'value': value, 'quiet': quiet, 'return_eid': return_eid})
    response = __prepare_request(query)
    if quiet or not verbose:
        return response
    else:
        return [['{}/events/view/{}'.format(misp_url, uuid) for uuid in uuids] for uuids in response]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search if a value is known in a MISP instance.')
    parser.add_argument("-k", "--authkey", help="Authorization key.")
    parser.add_argument("-s", "--value", help="Value tu search.")
    parser.add_argument("-a", "--hash_value", help="Hash of the value (sha256).")
    parser.add_argument("-q", "--quiet", action='store_true', help="Quiet query, doesn't returns UUIDs.")
    parser.add_argument("-e", "--eid", action='store_true', help="Return Event ids instead of UUIDs")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose query, returns URLs.")

    args = parser.parse_args()

    print(search(args.authkey, args.value, args.hash_value, args.quiet, args.verbose, args.eid))
