from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData, Table
from sqlalchemy.sql import select
from Crypto.Hash import SHA
from redis import StrictRedis
from config import user, password, host, dbname, redis_socket


class MispRedisConnector(object):

    def __init__(self):
        Base = automap_base()
        engine = create_engine('mysql://{}:{}@{}/{}'.format(user, password, host, dbname))

        # reflect the tables
        Base.prepare(engine, reflect=True)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        self.connection = engine.connect()
        self.events = Table("events", metadata, autoload=True)
        self.attributes = Table("attributes", metadata, autoload=True)

        self.r = StrictRedis(unix_socket_path=redis_socket)

    def add_value(self, value, event_uuid, attribute_uuid):
        hash_value = SHA.new(value).hexdigest()
        self.r.set('v:' + hash_value, attribute_uuid)
        self.r.set('v:' + attribute_uuid, value)

        self.r.sadd(event_uuid, attribute_uuid)
        self.r.sadd(attribute_uuid, event_uuid)

        self.r.sadd(hash_value, event_uuid)

    def make_correlations(self):

        # Build hashtable of event ID - event UUID
        eid_uuid = {}
        results = self.connection.execute(select([self.events]))
        for event in results:
            eid_uuid[event['id']] = event['uuid']

        # Create correlations
        results = self.connection.execute(select([self.attributes]))
        for attribute in results:
            try:
                self.add_value(attribute['value1'], eid_uuid[attribute['event_id']], attribute['uuid'])
            except Exception as e:
                print(e)
                print(attribute)

            if len(attribute['value2']) > 0:
                self.add_value(attribute['value2'], eid_uuid[attribute['event_id']], attribute['uuid'])
