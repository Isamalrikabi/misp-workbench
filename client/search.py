#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import argparse


url = 'http://127.0.0.1:5000/json'


def __prepare_request(query):
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(query), headers=headers)
    return r.json()


def search(hash_value=None, value=None, quiet=False):
    query = {'method': 'search'}
    query.update({'hash_value': hash_value, 'value': value, 'quiet': quiet})
    return __prepare_request(query)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search if a value is known in a MISP instance.')
    parser.add_argument("-v", "--value", help="Value tu search.")
    parser.add_argument("-s", "--sha", help="Hash of the value (sha1).")
    parser.add_argument("-q", "--quiet", action='store_true', help="Quiet query, doesn't returns UUIDs.")

    args = parser.parse_args()

    print(search(args.sha, args.value, args.quiet))
