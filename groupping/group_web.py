#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from connector_snapshot import SnapshotConnector
import string

app = Flask(__name__)
Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.debug = True


@app.route('/events', methods=['GET'])
def events_list():
    return render_template('events.html', events=connector.get_events())


@app.route('/merged', methods=['POST'])
def merged_details():
    to_merge = request.form.getlist("to_merge")
    correlations, total = connector.events_similarities(*to_merge)
    attr_digests = [('\n'.join(attr[0]), '\n'.join(attr[1])) for attr in connector.key_values_digests(connector.intersection(to_merge))]
    return render_template('merged.html', correlations=correlations,
                           total=total, event_digests=connector.get_events(to_merge),
                           attr_digests=attr_digests)


@app.route('/merged_groups', methods=['POST'])
def merged_groups_details():
    to_merge = request.form.getlist("to_merge")
    correlations, total = connector.groups_similarities(*to_merge)
    attr_digests = [('<br/>'.join(attr[0]), '<br/>'.join(attr[1])) for attr in connector.key_values_digests(connector.intersection_groups(to_merge))]

    return render_template('merged_groups.html', correlations=correlations,
                           total=total, events_in_groups=sort_groups(connector, to_merge),
                           attr_digests=attr_digests, quote=strip_char)


def sort_groups(connector, names=None):
    to_display = {}
    for g, events in connector.get_groups(names):
        splitted = g.split(':')
        if len(splitted) == 2:
            t, name = splitted
        else:
            t = ''
            name = g
        if not to_display.get(t):
            to_display[t] = []
        to_display[t].append((name, events))
    return to_display


def strip_char(text):
    return ''.join([i for i in text if i in string.ascii_letters + string.digits])


@app.route('/groups', methods=['GET', 'POST'])
def groups_list():
    if request.form.getlist("to_merge") and request.form.get('new_group_name'):
        connector.make_group(request.form.get('new_group_name'), *request.form.getlist("to_merge"))
    return render_template('groups.html', events_in_groups=sort_groups(connector), quote=strip_char)


if __name__ == '__main__':
    connector = SnapshotConnector()
    app.run()
