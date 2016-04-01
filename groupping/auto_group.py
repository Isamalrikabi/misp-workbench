#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import fnmatch
import json
from connector_snapshot import SnapshotConnector
from fti import search


def load_galaxy():
    root = 'misp-galaxy'
    to_return = {}
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, '*.json'):
                if not to_return.get(os.path.basename(path)):
                    to_return[os.path.basename(path)] = {}
                content = json.loads(open(os.path.join(path, name), 'r').read())
                fn, ext = os.path.splitext(name)
                to_return[os.path.basename(path)].update({fn: content})
    return to_return


def adversary_groups(galaxy):
    connector = SnapshotConnector()
    content = galaxy['elements']['adversary-groups']
    for group in content['details']:
        eids = search(group['group'])
        if group.get('synonyms'):
            for syn in group.get('synonyms'):
                eids.update(search(syn))
        if eids:
            connector.update_group(group['group'], *eids)


def tools(galaxy):
    connector = SnapshotConnector()
    content = galaxy['elements']['threat-actor-tools']
    for tool in content['values']:
        eids = search(tool['value'])
        if tool.get('synonyms'):
            for syn in tool.get('synonyms'):
                eids.update(search(syn))
        if eids:
            connector.update_group(tool['value'], *eids)


if __name__ == '__main__':
    g = load_galaxy()
    adversary_groups(g)
    tools(g)
