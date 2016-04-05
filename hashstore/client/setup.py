#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup
import misp_fast_lookup


setup(
    name='misp-fast-lookup',
    version=misp_fast_lookup.__version__,
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    url='https://github.com/MISP/misp-redis-datastore',
    description='API for MISP Redis Datastore.',
    packages=['misp_fast_lookup'],
    scripts=['bin/misp_fast_lookup'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Internet',
    ],
#    test_suite="tests",
    install_requires=['requests'],
)
