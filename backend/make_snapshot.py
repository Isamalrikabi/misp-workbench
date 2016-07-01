#!/usr/bin/env python
# -*- coding: utf-8 -*-

from connector import MispMySQLConnector
import argparse

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Create the full snapshot.')
    args = argparser.parse_args()
    connector = MispMySQLConnector()
    print('Export all MISP tables to Redis...')
    connector.import_all_tables()
    print('... done.')
    print('Export all attributes as hashes...')
    connector.cache_attributes(check_ACL=False)
    print('... done.')
