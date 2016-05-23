#!/usr/bin/env python
# -*- coding: utf-8 -*-

from redis import StrictRedis
from config import redis_socket
import datetime


class PECorrelator(object):

    def __init__(self):
        self.r = StrictRedis(unix_socket_path=redis_socket, decode_responses=True)

    def get_all_samples(self):
        return self.r.smembers('hashes_sha256')

    def get_sample_info(self, sha256):
        return self.r.hgetall(sha256)

    def get_timestamps_iso(self, num=-1):
        return [(datetime.datetime.fromtimestamp(ts).isoformat(), val) for ts, val in self.r.zrevrange('timestamps', 0, num, withscores=True)]

    def get_timestamps(self, num=-1):
        return self.r.zrevrange('timestamps', 0, num, withscores=True)

    def get_samples_timestamp(self, timestamp):
        return self.r.smembers('timestamp:{}'.format(timestamp))

    def get_imphashs(self, num=-1):
        return self.r.zrevrange('imphashs', 0, num, withscores=True)

    def get_samples_imphash(self, imphash):
        return self.r.smembers('imphash:{}'.format(imphash))

    def get_entrypoints(self, num=-1):
        return self.r.zrevrange('entrypoints', 0, num, withscores=True)

    def get_samples_entrypoint(self, entrypoint):
        return self.r.smembers('entrypoint:{}'.format(entrypoint))

    def get_secnumbers(self, num=-1):
        return self.r.zrevrange('secnumbers', 0, num, withscores=True)

    def get_samples_secnumber(self, secnumber):
        return self.r.smembers('secnumber:{}'.format(secnumber))

    def get_originalfilenames(self, num=-1):
        return self.r.zrevrange('originalfilenames', 0, num, withscores=True)

    def get_samples_originalfilename(self, originalfilename):
        return self.r.smembers('originalfilename:{}'.format(originalfilename))

    def get_sample_secnames(self, sha256):
        return self.r.smembers('{}:secnames'.format(sha256))
