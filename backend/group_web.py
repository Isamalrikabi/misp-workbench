#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from connector_snapshot import SnapshotConnector

app = Flask(__name__)
Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.debug = True


@app.route('/events', methods=['GET'])
def events_list():
    events = []
    for event_details in connector.get_events():
        t = {'eid': int(event_details[0])}
        t.update(dict(zip(['info', 'date'], event_details[1])))
        t['tags'] = ', '.join(event_details[2])
        events.append(t)
    return render_template('events.html', events=events)


@app.route('/merged', methods=['POST'])
def merged_details():
    to_merge = request.form.getlist("to_merge")
    correlations, total = connector.events_similarities(*to_merge)
    event_digests = [connector.get_event_digest(e) for e in to_merge]
    attr_digests = [('\n'.join(attr[0]), '\n'.join(attr[1])) for attr in connector.key_values_digests(connector.intersection(to_merge))]
    return render_template('merged.html', correlations=correlations,
                           total=total, event_digests=event_digests,
                           attr_digests=attr_digests)


@app.route('/merged_groups', methods=['POST'])
def merged_groups_details():
    to_merge = request.form.getlist("to_merge")
    events_in_groups = {}
    for group in to_merge:
        events_in_groups[group] = [connector.get_event_digest(e) for e in connector.get_events_in_group(group)]
    correlations, total = connector.groups_similarities(*to_merge)
    attr_digests = [('\n'.join(attr[0]), '\n'.join(attr[1])) for attr in connector.key_values_digests(connector.intersection_groups(to_merge))]
    return render_template('merged_groups.html', correlations=correlations,
                           total=total, events_in_groups=events_in_groups,
                           attr_digests=attr_digests)


@app.route('/groups', methods=['GET'])
def groups_list():
    groups = []
    for group_details in connector.get_groups():
        t = {'group': group_details[0], 'eid': int(group_details[1])}
        t.update(dict(zip(['info', 'date'], group_details[2])))
        t['tags'] = ', '.join(group_details[3])
        groups.append(t)
    return render_template('groups.html', groups=groups)




if __name__ == '__main__':
    connector = SnapshotConnector()
    app.run()
