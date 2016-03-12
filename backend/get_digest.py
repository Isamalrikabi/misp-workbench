#!/usr/bin/env python
# -*- coding: utf-8 -*-

from connector_misp import MispMySQLConnector
import csv
import sys
import datetime


m = MispMySQLConnector()
a = m.get_event_digest()

writer = csv.writer(sys.stdout)
for e in a:
    e[-1] = datetime.datetime.fromtimestamp(e[-1]).isoformat()
    writer.writerow(e)
