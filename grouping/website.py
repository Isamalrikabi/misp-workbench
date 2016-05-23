#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from connector import SnapshotConnector
from pecorrelator import PECorrelator
from fti import search
import string

nav = Nav()


@nav.navigation()
def mynavbar():
    return Navbar(
        'Event grouping interface',
        View('Events', 'events_list'),
        View('Groups', 'groups_list'),
        View('Full text search', 'search_events'),
        View('Compilation Timestamps', 'pe_ts'),
    )

app = Flask(__name__)
Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.debug = True
nav.init_app(app)


@app.route('/', methods=['GET'])
def index():
    return events_list()


@app.route('/events', methods=['GET'])
def events_list():
    return render_template('events.html', events=connector.get_events())


def merge_events(eids):
    correlations, total = connector.events_similarities(*eids)
    attr_digests = [('\n'.join(attr[0]), '\n'.join(attr[1]))
                    for attr in connector.key_values_digests(connector.intersection(eids))]
    return render_template('merged.html', correlations=correlations,
                           total=total, event_digests=connector.get_events(eids),
                           attr_digests=attr_digests)


@app.route('/merged', methods=['POST'])
def merged_details():
    to_merge = request.form.getlist("to_merge")
    return merge_events(to_merge)


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


@app.route('/search', methods=['GET', 'POST'])
def search_events():
    if request.form.get('query'):
        eids = search(request.form.get('query'))
        return merge_events(eids)
    return render_template('search.html')


@app.route('/pe_timestamps/', defaults={'timestamp': None})
@app.route('/pe_timestamps/<int:timestamp>', methods=['GET'])
def pe_ts(timestamp=None):
    if not timestamp:
        timestamps = pe.get_timestamps()
        return render_template('all_timestamps.html', timestamps=timestamps, timestamp=None)
    else:
        samples = pe.get_samples_timestamp(timestamp)
        return render_template('all_timestamps.html', timestamp=timestamp, samples=samples)


@app.route('/pe_sample_info/', defaults={'sha256': None})
@app.route('/pe_sample_info/<sha256>', methods=['GET'])
def pe_sample_info(sha256=None):
    if not sha256:
        samples = pe.get_all_samples()
        s_details = [(s, pe.get_sample_info(s)) for s in samples]
        keys = list(s_details[0][1].keys())
        keys.remove('ssdeep')
        keys.remove('md5')
        keys.remove('path')
        keys.remove('filename')
        keys.remove('sha1')
        return render_template('samples.html', samples=s_details, keys=keys)
    else:
        s_details = [(sha256, pe.get_sample_info(sha256))]
        keys = list(s_details[0][1].keys())
        return render_template('samples.html', samples=s_details, keys=keys)

if __name__ == '__main__':
    connector = SnapshotConnector()
    pe = PECorrelator()
    app.run()
