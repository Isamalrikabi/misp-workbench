#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData, Table
from sqlalchemy.sql import select
from Crypto.Hash import SHA256
from redis import StrictRedis
from config import user, password, host, dbname, redis_socket


class MispMySQLConnector(object):

    def __init__(self):
        Base = automap_base()
        engine = create_engine('mysql://{}:{}@{}/{}'.format(user, password, host, dbname))

        # reflect the tables
        Base.prepare(engine, reflect=True)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        self.connection = engine.connect()
        self.events = Table("events", metadata, autoload=True)
        self.users = Table("users", metadata, autoload=True)
        self.attributes = Table("attributes", metadata, autoload=True)

        self.r = StrictRedis(unix_socket_path=redis_socket)

    # ####### Other functions ########

    def import_auth(self):
        users = self.connection.execute(select([self.users]))
        for u in users:
            self.r.set(u['authkey'], u['org_id'])

    # ####### Helpers ########

    def __get_all_event_uuid(self):
        # Build hashtable of event ID - event UUID
        eid_uuid = {}
        results = self.connection.execute(select([self.events]))
        for event in results:
            eid_uuid[event['id']] = event['uuid']
            self.r.hset('uuid_id', event['uuid'], event['id'])
        return eid_uuid

    # ####### Get specific information from the database, Auth NOT preserved.#######

    def get_event_digest(self, list_eids=None):
        '''
            Returns a igest of the events in list_eids. If None: all the events.

            List:
                [
                    [id, uuid, info, date of the event, timestamp of the last update],
                    ...
                ]

        '''
        results = self.connection.execute(select([self.events]))
        to_return = []
        for event in results:
            to_add = True
            if list_eids and event['id'] not in list_eids:
                to_add = False
            if to_add:
                to_return.append([event['id'], event['uuid'], event['info'], event['date'], event['timestamp']])
        return to_return

    def get_CVE_events(self, list_eids=None):
        '''
            Returns CVE IDs by events in list_eids. If None: all the events.

            Dict:
                {
                    event_id: [CVE ID, ...].
                    ...
                }
        '''
        to_return = {}
        attributes = self.connection.execute(select([self.attributes]))
        for a in attributes:
            to_add = False
            if a['type'] == 'vulnerability':
                to_add = True
                if list_eids and a['event_id'] not in list_eids:
                    to_add = False
            if to_add:
                if not to_return.get(a['event_id']):
                    to_return[a['event_id']] = []
                to_return[a['event_id']].append(a['value1'])
        return to_return

    # ####### Cache all attributes for fast access. Auth preserved. ########

    def _add_hash(self, event_uuid, value1, value2='', orgid=None):
        if orgid:
            key = '{}:'.format(orgid)
        else:
            key = ''
        hash_value = SHA256.new(value1.lower()).hexdigest()
        self.r.sadd(key + hash_value, event_uuid)
        if value2:
            hash_value = SHA256.new(value2.lower()).hexdigest()
            self.r.sadd(key + hash_value, event_uuid)

    def cache_attributes(self):
        eid_uuid = self.__get_all_event_uuid()
        attributes = self.connection.execute(select([self.attributes]))
        for a in attributes:
            orgid = None
            if a['distribution'] == 0:
                # Limited distribution (this org only)
                result = self.connection.execute(select([self.events.c.org_id]).where(self.events.c.id == a['event_id']))
                for e in result:
                    orgid = e.org_id
            uuid = eid_uuid.get(a['event_id'])
            if not uuid:
                continue
            self._add_hash(uuid, a['value1'], a['value2'], orgid)
