#!/usr/bin/env python
# -*- coding: utf-8 -*-

from connector import MispRedisConnector

if __name__ == '__main__':
    connector = MispRedisConnector()
    connector.make_correlations()
