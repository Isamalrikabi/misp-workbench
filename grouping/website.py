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
import datetime

nav = Nav()


@nav.navigation()
def mynavbar():
    return Navbar(
        'Event grouping interface',
        View('Events', 'events_list'),
        View('Groups', 'groups_list'),
        View('Full text search', 'search_events'),
        View('Samples', 'pe_sample_info'),
        View('Compilation Timestamps', 'pe_ts'),
        View('Original Filenames', 'pe_original_filename'),
        View('Imphahses', 'pe_imphash'),
        View('Entrypoints', 'pe_entrypoint'),
        View('Secnumbers', 'pe_secnumber'),
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
    attr_digests = [(' - '.join(attr[0]), ' - '.join(attr[1])) for attr in connector.key_values_digests(connector.intersection_groups(to_merge))]

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


def search_hashes_fast(samples_hash):
    # NOTE: require EID cache (see SnapshotConnector.rebuild_eid_cache)
    if not (isinstance(samples_hash, list) or isinstance(samples_hash, set)):
        samples_hash = [samples_hash]
    return connector.hashes_eids(samples_hash)


def search_hashes_slow(samples_hash):
    if isinstance(samples_hash, list) or isinstance(samples_hash, set):
        to_search = []
        for h in samples_hash:
            to_search += pe.get_all_hashes(h)
    else:
        to_search = pe.get_all_hashes(samples_hash)
    eids = [e for e, f in search(' '.join(to_search), 'value').most_common()]
    return eids


@app.route('/groups', methods=['GET', 'POST'])
def groups_list():
    if request.form.getlist("to_merge") and request.form.get('new_group_name'):
        connector.make_group(request.form.get('new_group_name'), *request.form.getlist("to_merge"))
    return render_template('groups.html', events_in_groups=sort_groups(connector), quote=strip_char)


@app.route('/search', methods=['GET', 'POST'])
def search_events():
    if request.form.get('query'):
        eids = search(request.form.get('query'))
        if eids:
            top = [e for e, f in eids.most_common(20)]
            return merge_events(top)
    return render_template('search.html')


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


@app.route('/pe_timestamps/', defaults={'timestamp': None})
@app.route('/pe_timestamps/<int:timestamp>', methods=['GET'])
def pe_ts(timestamp=None):
    if not timestamp:
        timestamps = [(t, datetime.datetime.fromtimestamp(int(t)).isoformat(), f) for t, f in pe.get_timestamps()]
        timestamps = [(t, i, f, len(search_hashes_fast(pe.get_samples_timestamp(t)))) for t, i, f in timestamps]
        return render_template('all_timestamps.html', timestamps=timestamps, timestamp=None)
    else:
        samples = pe.get_samples_timestamp(timestamp)
        events = connector.get_events(search_hashes_fast(samples))
        return render_template('all_timestamps.html', timestamp=timestamp, samples=samples, events=events)


@app.route('/pe_original_filename/', defaults={'ofn': None})
@app.route('/pe_original_filename/<ofn>', methods=['GET'])
def pe_original_filename(ofn=None):
    if not ofn:
        ofns = pe.get_originalfilenames()
        ofns = [(o, freq, len(search_hashes_fast(pe.get_samples_originalfilename(o)))) for o, freq in ofns]
        return render_template('orig_filename.html', ofns=ofns, ofn=None)
    else:
        samples = pe.get_samples_originalfilename(ofn)
        events = connector.get_events(search_hashes_fast(samples))
        return render_template('orig_filename.html', ofn=ofn, samples=samples, events=events)


@app.route('/pe_imphash/', defaults={'imphash': None})
@app.route('/pe_imphash/<imphash>', methods=['GET'])
def pe_imphash(imphash=None):
    if not imphash:
        imphashs = pe.get_imphashs()
        imphashs = [(i, freq, len(search_hashes_fast(pe.get_samples_imphash(i)))) for i, freq in imphashs]
        return render_template('imphash.html', imphashs=imphashs, imphash=None)
    else:
        samples = pe.get_samples_imphash(imphash)
        events = connector.get_events(search_hashes_fast(samples))
        return render_template('imphash.html', imphash=imphash, samples=samples, events=events)


@app.route('/pe_entrypoint/', defaults={'ept': None})
@app.route('/pe_entrypoint/<ept>', methods=['GET'])
def pe_entrypoint(ept=None):
    if not ept:
        epts = pe.get_entrypoints()
        epts = [(e, freq, len(search_hashes_fast(pe.get_samples_entrypoint(e)))) for e, freq in epts]
        return render_template('entrypoint.html', epts=epts, ept=None)
    else:
        samples = pe.get_samples_entrypoint(ept)
        events = connector.get_events(search_hashes_fast(samples))
        return render_template('entrypoint.html', ept=ept, samples=samples, events=events)


@app.route('/pe_secnumber/', defaults={'snb': None})
@app.route('/pe_secnumber/<snb>', methods=['GET'])
def pe_secnumber(snb=None):
    if not snb:
        snbs = pe.get_secnumbers()
        snbs = [(s, freq, len(search_hashes_fast(pe.get_samples_secnumber(s)))) for s, freq in snbs]
        return render_template('secnumber.html', snbs=snbs, snb=None)
    else:
        samples = pe.get_samples_secnumber(snb)
        events = connector.get_events(search_hashes_fast(samples))
        return render_template('secnumber.html', snb=snb, samples=samples, events=events)


if __name__ == '__main__':
    connector = SnapshotConnector()
    pe = PECorrelator()
    app.run()
