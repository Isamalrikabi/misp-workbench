#!/usr/bin/env python
# -*- coding: utf-8 -*-

from connector import SnapshotConnector
from whoosh.index import create_in, open_dir
from whoosh.fields import NGRAMWORDS, ID, Schema
from whoosh.qparser import QueryParser


def index_all(connector, schema):
    ix = create_in("indexdir", schema)
    writer = ix.writer(limitmb=4096, procs=4, multisegment=True)
    for eid, value1, value2, comment in connector.get_all_value_digest():
        event = connector.get_event_digest(eid)
        writer.add_document(eid=eid, content=' '.join([event['info'], value1,
                                                       value2, comment] + list(event['tags'])))
    writer.commit()


def search(query):
    ix = open_dir("indexdir")
    with ix.searcher() as searcher:
        q = QueryParser("content", schema=ix.schema).parse(query)
        return set([r['eid'] for r in searcher.search(q)])

if __name__ == '__main__':
    connector = SnapshotConnector()
    schema = Schema(eid=ID(stored=True), content=NGRAMWORDS(minsize=4, queryor=True))
    index_all(connector, schema)
