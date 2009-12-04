#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Page(object):
    provides = tuple()
    requires = tuple()
    my_icon = None
    title = None
    name = None
    panel = None
    icons = ()
    
    def __init__(self):
        self.panel = self.__class__.panel()
        self.panel.show()
