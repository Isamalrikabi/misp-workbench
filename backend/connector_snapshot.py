#!/usr/bin/env python
# -*- coding: utf-8 -*-

from redis import StrictRedis
from config import redis_socket


class SnapshotConnector(object):

    def __init__(self):
        self.r = StrictRedis(unix_socket_path=redis_socket)

    # ##### Event functions #####

    def merge(self, events):
        events = sorted(events, key=int)
        keys = ['event_vals:{}'.format(eid) for eid in events]
        out_key = '|'.join(map(str, events))
        self.r.sunionstore(out_key, *keys)
        self.r.expire(out_key, 300)
        return out_key

    def intersection(self, events):
        events = sorted(events, key=int)
        keys = ['event_vals:{}'.format(eid) for eid in events]
        out_key = '&'.join(map(str, events))
        self.r.sinterstore(out_key, *keys)
        self.r.expire(out_key, 300)
        return out_key

    def events_similarities(self, *events):
        return self.r.scard(self.intersection(events)), self.r.scard(self.merge(events))

    # ##### Group functions #####

    def make_group(self, name, *events):
        if not self.r.exists(name):
            self.r.sadd(name, *events)
            self.r.sadd('groups', name)
        else:
            raise Exception('Group name already exists, maybe you want to update.')

    def update_group(self, name, *events):
        self.r.sadd(name, *events)
        self.r.sadd('groups', name)

    def del_group(self, name):
        self.r.delete(name)
        self.r.srem('groups', name)

    def merge_groups(self, groups):
        groups = sorted(groups)
        out_key = '|'.join(groups)
        self.r.sunionstore(out_key, *groups)
        self.r.expire(out_key, 300)
        return out_key

    def intersection_groups(self, groups):
        groups = sorted(groups)
        out_key = '&'.join(groups)
        self.r.sinterstore(out_key, *groups)
        self.r.expire(out_key, 300)
        return out_key

    def groups_similarities(self, *groups):
        return self.r.scard(self.intersection_groups(groups)), self.r.scard(self.merge_groups(groups))

    def group_similarities(self, *groups):
        merged = [self.merge(self.r.smembers(g)) for g in groups]
        return self.groups_similarities(*merged)
