#!/usr/bin/env python
# -*- coding: utf-8 -*-

from connector_misp import MispMySQLConnector
import csv
import sys

m = MispMySQLConnector()
a = m.get_CVE_events()

writer = csv.writer(sys.stdout)
for eid, cves in a.items():
    writer.writerow([eid] + cves)
