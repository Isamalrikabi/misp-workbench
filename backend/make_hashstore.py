#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from connector import MispMySQLConnector

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Create the hashstore')
    argparser.add_argument('-i', default=False, action='store_true', help='Ignore ACL')
    args = argparser.parse_args()
    connector = MispMySQLConnector()
    if args.i:
        connector.cache_attributes(check_ACL=False)
    else:
        connector.import_auth()
        connector.cache_attributes()
