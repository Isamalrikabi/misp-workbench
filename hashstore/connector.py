#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Crypto.Hash import SHA256
from redis import StrictRedis
try:
    from config import redis_socket
    if not redis_socket:
        raise ImportError
except:
    from config import redis_host, redis_port


class MispRedisConnector(object):

    def __init__(self):
        if redis_socket:
            self.r = StrictRedis(unix_socket_path=redis_socket, decode_responses=True)
        else:
            self.r = StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    def search(self, authkey, values=None, hash_values=None, return_eid=False, quiet=False):
        if isinstance(values, list):
            hash_values = [SHA256.new(v.lower()).hexdigest() for v in values]
        elif values:
            hash_values = [SHA256.new(values.lower()).hexdigest()]
        elif not isinstance(hash_values, list):
            hash_values = [hash_values]

        if not hash_values:
            raise Exception('No value to search.')

        org = self.__get_org_by_auth(authkey)
        if not org:
            raise Exception('Invalid authkey')

        key = 'hashstore:'
        key_acl = 'hashstore:{}:'.format(org)

        if quiet:
            return [(self.r.exists(key + h) or self.r.exists(key_acl + h)) for h in hash_values]
        uuid_by_hashes = [self.r.smembers(key + h).union(self.r.smembers(key_acl + h)) for h in hash_values]
        if not return_eid:
            to_return = uuid_by_hashes
        else:
            to_return = []
            for h in uuid_by_hashes:
                to_return.append([self.r.hget('uuid_id', uuid) for uuid in h])
        return to_return

    def __get_org_by_auth(self, authkey):
        return self.r.get(authkey)
