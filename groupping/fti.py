#!/usr/bin/env python
# -*- coding: utf-8 -*-

from connector_snapshot import SnapshotConnector
from whoosh.index import create_in
from whoosh.fields import TEXT, ID, Schema
from whoosh.qparser import QueryParser
import os


def init_whoosh():
    schema = Schema(info=TEXT(stored=True), eid=ID(stored=True),
                    value1=TEXT, value2=TEXT, comment=TEXT, tags=TEXT)
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    ix = create_in("indexdir", schema)
    return ix


def index_all(connector, whoosh_index):
    attrs = connector.get_all_value_digest()
    writer = whoosh_index.writer()
    for eid, value1, value2, comment in attrs:
        event = connector.get_event_digest(eid)
        writer.add_document(info=event['info'], eid=eid, value1=value1, value2=value2,
                            comment=comment, tags=' '.join(event['tags']))
    writer.commit()


def search(whoosh_index, query):
    with whoosh_index.searcher() as searcher:
        q = QueryParser("comment", schema=whoosh_index.schema).parse(query)
        return searcher.search(q)

if __name__ == '__main__':
    connector = SnapshotConnector()
    whoosh_index = init_whoosh()
    index_all(connector, whoosh_index)
