#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name              = 'libhdhomerun',
    version           = '0.1.0',
    description       = 'Bindings to libhdhomerun',
    long_description  = 'Bindings to the libhdhomerun shared library',
    author            = 'Gary Buhrmaster',
    author_email      = 'gary.buhrmaster@gmail.com',
    py_modules        = ['libhdhomerun'],
    url               = 'https://github.com/garybuhrmaster/python-libhdhomerun/tarball/master',
    license           = "Apache License 2.0",
    classifiers       = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Libraries'
    ],
)

