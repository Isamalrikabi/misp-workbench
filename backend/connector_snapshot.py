#!/usr/bin/env python
# -*- coding: utf-8 -*-

from redis import StrictRedis
from config import redis_socket
from Crypto.Hash import SHA256


class SnapshotConnector(object):

    def __init__(self):
        self.r = StrictRedis(unix_socket_path=redis_socket, decode_responses=True)

    # ##### Helpers web interface #####

    def get_groups(self):
        for g in sorted(self.r.smembers('groups')):
            for eid in sorted(self.r.smembers(g), key=int, reverse=True):
                yield g, eid, self.r.hmget('event:{}'.format(eid), 'info', 'date'), self.r.smembers('event:{}:tags'.format(eid))

    def get_events(self):
        for eid in sorted(self.r.smembers('events'), key=int, reverse=True):
            yield eid, self.r.hmget('event:{}'.format(eid), 'info', 'date'), self.r.smembers('event:{}:tags'.format(eid))

    # ##### Values functions #####

    def make_hashed_value(self, value):
        '''
            Hash the value to search
        '''
        return SHA256.new(value.strip().lower()).hexdigest()

    def get_value_details(self, hashed_value):
        '''
            Returns all attributes of a value
        '''
        attributes_ids = self.r.smembers('{}:attrs'.format(hashed_value))
        return [self.r.hgetall('attribute:{}'.format(attrid)) for attrid in attributes_ids]

    def get_value_digest(self, hashed_value):
        '''
            Returns value1 & 2 and comment, deduplicate
        '''
        attrids = self.r.smembers('{}:attrs'.format(hashed_value))
        digest = [self.r.hmget('attribute:{}'.format(aid), 'value1', 'value2', 'comment') for aid in attrids]
        values = set()
        comments = set()
        for v1, v2, comment in digest:
            values.add(v1)
            if v2:
                values.add(v2)
            if comment:
                comments.add(comment)
        return values, comments

    def get_events_digest_from_value(self, hashed_value):
        '''
            Returns digests of events the value is listed in.
        '''
        eids = self.r.smembers(hashed_value)
        infos = sorted([self.get_event_digest(eid) for eid in eids], key=lambda tup: int(tup[0]))
        return infos

    # ##### Keys functions #####

    def key_values_digests(self, key):
        '''
            Returns value digests of all values in a key
        '''
        return [self.get_value_digest(hashed_value) for hashed_value in self.r.smembers(key)]

    # ##### Event functions #####

    def get_event_digest(self, eid):
        '''
            Returns info and date of the event
        '''
        return eid, self.r.hmget('event:{}'.format(eid), 'info', 'date'), self.r.smembers('event:{}:tags'.format(eid))

    def merge(self, events):
        '''
            Merge a list of events into one set.
            The key of the set is <event1>|<event2>|<event3>|...
        '''
        events = sorted(events, key=int)
        keys = ['event_vals:{}'.format(eid) for eid in events]
        out_key = '|'.join(map(str, events))
        self.r.sunionstore(out_key, *keys)
        self.r.expire(out_key, 300)
        return out_key

    def intersection(self, events):
        '''
            Keeps only the values in *all* the sets
            The key of the set is <event1>&<event2>&<event3>&...
        '''
        events = sorted(events, key=int)
        keys = ['event_vals:{}'.format(eid) for eid in events]
        out_key = '&'.join(map(str, events))
        self.r.sinterstore(out_key, *keys)
        self.r.expire(out_key, 300)
        return out_key

    def events_similarities(self, *events):
        '''
            Returns the intersection and the total amount of values in multiple events
        '''
        return self.r.scard(self.intersection(events)), self.r.scard(self.merge(events))

    # ##### Group functions #####

    def get_events_in_group(self, name):
        return self.r.smembers(name)

    def make_group(self, name, *events):
        '''
            Create a group of events
        '''
        if not self.r.exists(name):
            self.r.sadd(name, *events)
            self.r.sadd('groups', name)
        else:
            raise Exception('Group name already exists, maybe you want to update.')

    def update_group(self, name, *events):
        '''
            Update a group of events
        '''
        self.r.sadd(name, *events)
        self.r.sadd('groups', name)

    def del_group(self, name):
        '''
            Delete a group of events
        '''
        self.r.delete(name)
        self.r.srem('groups', name)

    def merge_groups(self, group_names):
        '''
            Merge groups of events
            The key of the set is <group1>|<group2>|<group3>|...
        '''
        groups = sorted([self.merge(self.r.smembers(group_name)) for group_name in group_names])
        out_key = '|'.join(groups)
        self.r.sunionstore(out_key, *groups)
        self.r.expire(out_key, 300)
        return out_key

    def intersection_groups(self, group_names):
        '''
            Keeps only the values in *all* the sets
            The key of the set is <group1>&<group2>&<group3>&...
        '''

        groups = sorted([self.intersection(self.r.smembers(group_name)) for group_name in group_names])
        out_key = '&'.join(groups)
        self.r.sinterstore(out_key, *groups)
        self.r.expire(out_key, 300)
        return out_key

    def groups_similarities(self, *group_names):
        '''
             Returns the intersection and the total amount of values in multiple groups
        '''
        return self.r.scard(self.intersection_groups(group_names)), self.r.scard(self.merge_groups(group_names))
