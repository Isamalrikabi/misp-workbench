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
        self.attributes = Table("attributes", metadata, autoload=True)
        self.events = Table("events", metadata, autoload=True)
        self.organisations = Table("organisations", metadata, autoload=True)
        self.threat_levels = Table("threat_levels", metadata, autoload=True)
        self.users = Table("users", metadata, autoload=True)

        self.tags = Table("tags", metadata, autoload=True)
        self.event_tags = Table("event_tags", metadata, autoload=True)

        self.r = StrictRedis(unix_socket_path=redis_socket)

    # ####### Full import no respect of ACL ########

    def import_table(self, table):
        p = self.r.pipeline(False)
        tab_name = table.name
        for row in self.connection.execute(select([table])):
            p.sadd(tab_name, row['id'])
            p.hmset('{}:{}'.format(tab_name[:-1], row['id']), dict(row))
        p.execute()

    def import_all_tables(self):
        # Mass import of everything
        self.import_table(self.attributes)
        self.import_table(self.events)
        self.import_table(self.organisations)
        self.import_table(self.threat_levels)
        self.import_table(self.users)
        # Specific import
        p = self.r.pipeline(False)
        tag_ids = {}
        for row in self.connection.execute(select([self.tags])):
            tag_ids[row['id']] = row['name']
            p.sadd('tags', row['name'])
        p.execute()
        p = self.r.pipeline(False)
        for row in self.connection.execute(select([self.event_tags])):
            tag_name = tag_ids[row['tag_id']]
            p.sadd('event:{}:tags'.format(row['event_id']), tag_name)
            p.sadd('{}:events'.format(tag_name), row['event_id'])
        p.execute()
        # Create usefull helpers & correlations
        p = self.r.pipeline(False)
        for a in self.connection.execute(select([self.attributes])):
            p.sadd('event_attrs:{}'.format(a['event_id']), a['id'])
            # Hashing the values again avoid very long entries (snort/yara rules)
            hash_value = SHA256.new(a['value1'].strip().lower()).hexdigest()
            p.sadd(hash_value, a['event_id'])
            p.sadd('event_vals:{}'.format(a['event_id']), hash_value)
            p.set('val:{}'.format(hash_value), a['value1'])
            p.sadd('{}:attrs'.format(hash_value), a['id'])
            if a['value2'].strip():
                hash_value = SHA256.new(a['value2'].strip().lower()).hexdigest()
                p.sadd(hash_value, a['event_id'])
                p.sadd('event_vals:{}'.format(a['event_id']), hash_value)
                p.set('val:{}'.format(hash_value), a['value2'])
        p.execute()

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
