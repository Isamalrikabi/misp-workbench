#!/usr/bin/env python
# -*- coding: utf-8 -*-

from redis import StrictRedis
from config import redis_socket
from Crypto.Hash import SHA256


class SnapshotConnector(object):

    def __init__(self):
        self.r = StrictRedis(unix_socket_path=redis_socket)

    # ##### Values functions #####

    def make_hashed_value(self, value):
        return SHA256.new(value.strip().lower()).hexdigest()

    def get_value_details(self, hashed_value):
        attributes_ids = self.r.smembers('{}:attrs'.format(hashed_value))
        return [self.r.hgetall('attribute:{}'.format(attrid)) for attrid in attributes_ids]

    def get_value_digest(self, hashed_value):
        attrids = self.r.smembers('{}:attrs'.format(hashed_value))
        digest = [self.r.hmget('attribute:{}'.format(aid), 'value1', 'value2', 'comment') for aid in attrids]
        values = set()
        comments = set()
        for v1, v2, comment in digest:
            if comment:
                comments.add(comment)
            values.add(v1)
            if v2:
                values.add(v2)
        return values, comments

    def get_events_digest(self, hashed_value):
        eids = self.r.smembers(hashed_value)
        infos = sorted([self.get_event_digest(eid) for eid in eids], key=lambda tup: int(tup[0]))
        return infos

    # ##### Similarities #####

    def intersection_details(self, key):
        return [self.get_value_digest(hashed_value) for hashed_value in self.r.smembers(key)]

    # ##### Event functions #####

    def get_event_digest(self, eid):
        return eid, self.r.hmget('event:{}'.format(eid), 'info', 'date'), self.r.smembers('event:{}:tags'.format(eid))

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

    def get_merged_group_key(self, group_name):
        return self.merge(self.r.smembers(group_name))

    def groups_similarities(self, *merged_events):
        return self.r.scard(self.intersection_groups(merged_events)), self.r.scard(self.merge_groups(merged_events))

    def group_similarities(self, *group_names):
        merged = [self.get_merged_group_key(g_name) for g_name in group_names]
        return self.groups_similarities(*merged)
