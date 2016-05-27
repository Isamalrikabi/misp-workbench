#!/usr/bin/env python
# -*- coding: utf-8 -*-

from whoosh.index import create_in, open_dir
from whoosh.fields import NGRAMWORDS, ID, Schema, KEYWORD
from whoosh.qparser import MultifieldParser, OrGroup


def index_all(connector, schema):
    ix = create_in("indexdir", schema)
    writer = ix.writer(limitmb=2048, procs=4, multisegment=True)
    for eid, value1, value2, comment in connector.get_all_value_digest():
        event = connector.get_event_digest(eid)
        writer.add_document(eid=eid, info=event['info'], value=value1 + ' ' + value2,
                            comment=comment, tags=' '.join(list(event['tags'])))
    writer.commit()


def search(query, fields=None):
    all_fields = ['info', 'value', 'comment', 'tags']
    # If field is None, search in all
    if not fields:
        search_fields = all_fields
    elif isinstance(fields, list):
        for f in fields:
            if f not in all_fields:
                raise Exception('Invalid Fieldname')
        search_fields = fields
    else:
        search_fields = [fields]
    ix = open_dir("indexdir")
    mparser = MultifieldParser(search_fields, schema=ix.schema, group=OrGroup)
    with ix.searcher() as searcher:
        q = mparser.parse(query)
        responses = searcher.search(q)
        return set([r['eid'] for r in responses])

if __name__ == '__main__':
    from connector import SnapshotConnector
    connector = SnapshotConnector()
    schema = Schema(eid=ID(stored=True), info=NGRAMWORDS(minsize=4, queryor=True),
                    value=KEYWORD(lowercase=True),
                    comment=NGRAMWORDS(minsize=4, queryor=True),
                    tags=NGRAMWORDS(minsize=4, queryor=True))
    index_all(connector, schema)
