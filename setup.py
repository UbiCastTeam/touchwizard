#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, imp
from distutils.core import setup

touchwizard = imp.load_source("version", "touchwizard/version.py")
path = 'data/images/'
images = [
    path + f
    for f in os.listdir(path)
    if os.path.isfile(path + f)
]
path = 'data/icons/'
icons = [
    path + f
    for f in os.listdir(path)
    if os.path.isfile(path + f)
]

setup(
    name="touchwizard",
    version=touchwizard.VERSION,
    description="Touchscreen-optimized step-by-step wizard GUI library.",
    author="Florent Thiery, Damien Boucard",
    author_email="florent.thiery@ubicast.eu",
    url="http://code.google.com/p/touchwizard/",
    license="Gnu/LGPL",
    packages = ['touchwizard'],
    data_files = [
        ('share/touchwizard/images', images),
        ('share/touchwizard/icons', icons),
    ],
)
