#!/usr/bin/env python
# -*- coding: utf-8 -*

import touchwizard
from touchwizard import event
import clutter
import candies2

class SamplePanel(candies2.container.ContainerAdapter, event.User,
                                             clutter.Actor, clutter.Container):
    __gtype_name__ = 'SamplePanel'
    
    def __init__(self):
        candies2.container.ContainerAdapter.__init__(self)
        clutter.Actor.__init__(self)
        event.User.__init__(self)
        
        self.label = clutter.Text()
        self.label.set_text('Welcome to the Touchwizard Test Page !')
        self.label.set_font_name('Sans 26')
        self.add(self.label)
        
        self.button = candies2.ClassicButton('Quit')
        self.button.set_reactive(True)
        self.button.connect('button-press-event', on_button_pressed)
        self.add(self.button)
        
        self.next_page = 'test2'
    
    def on_button_pressed(self, button, event):
        self.launch_event('change_page', self.next_page)
        return True
    
    def do_get_preferred_width(self, for_height):
        label_prefs = self.label.get_preferred_width(for_height)
        button_prefs = self.button.get_preferred_width(for_height)
        return (
            label_prefs[0] + button_prefs[0],
            label_prefs[1] + button_prefs[1],
        )
    
    def do_get_preferred_height(self, for_width):
        label_prefs = self.label.get_preferred_height(for_width)
        button_prefs = self.button.get_preferred_height(for_width)
        return (
            max(label_prefs[0], button_prefs[0]),
            max(label_prefs[1], button_prefs[1]),
        )
    
    def do_allocate(self, box, flags):
        self.label.allocate_available(5, 5, box.x2 - 10, box.y2 - 10, flags)
        
        bbox = clutter.ActorBox()
        bbox.x1 = (box.x2 - box.x1) / 3
        bbox.x2 = bbox.x1 * 2
        bbox.y1 = (box.y2 - box.y1) / 3
        bbox.y2 = bbox.y1 * 2
        self.button.allocate(bbox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)

class Page(touchwizard.Page):
    title = 'Test Page 1/2'
    name = 'test1'
    panel = SamplePanel

if __name__ == '__main__':
    touchwizard.quick_launch(Page)
