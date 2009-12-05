#!/ur/bin/env python
# -*- coding: utf-8 -*-

''' 
default clutter class struct
author : flavie
date : dec 4 2009
version : none
'''
import sys
import operator
import gobject
import clutter

class Name(clutter.Actor, clutter.Container):
    '''
    Preset class
    '''
    __gtype_name__ = 'Name'
    
    def __init__(self):
        clutter.Actor.__init__(self)
            
    def do_allocate(self, box, flags):
    
    clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        children = (self.,)
        for child in children :
            func(child, data)
    
    def do_paint(self):
        children = (self.,)
        for child in children :
            child.paint()

    def do_pick(self, color):
        children = (self.,)
        for child in children :
            child.paint()

if __name__ == '__main__':

    stage = clutter.Stage()
    stage.connect('destroy',clutter.main_quit)

    name = Name()
    name.set_size(width,height)
    name.set_position(xoff,yoff)
    stage.add(name)

    stage.show()

    clutter.main() 
