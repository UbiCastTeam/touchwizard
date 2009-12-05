#!/usr/bin/env python
# -*- coding: utf-8 -*

import touchwizard
import easyevent
import clutter
import candies2
import os

__path__ = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
touchwizard.icon_path = __path__

class SamplePanel(candies2.container.ContainerAdapter, easyevent.User,
                                             clutter.Actor, clutter.Container):
    __gtype_name__ = 'SamplePanel'
    
    def __init__(self):
        candies2.container.ContainerAdapter.__init__(self)
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        self.connect('notify::visible', self.on_show)
        
        self.label = clutter.Text()
        #self.label.set_text('Welcome to the Touchwizard Test Page !')
        self.label.set_font_name('Sans 26')
        self.add(self.label)
        
        self.button = candies2.ClassicButton('Quit')
        self.button.set_reactive(True)
        self.button.connect('button-press-event', self.on_button_pressed)
        self.add(self.button)
        
        self.next_page = 'test2'
    
    def on_show(self, panel, event):
        self.launch_event('info_message', 'Welcome to the Touchwizard Test Page !')
    
    def on_button_pressed(self, button, event):
        self.launch_event('next_page', self.next_page)
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
        self.label.allocate_available_size(5, 5, box.x2 - 10, box.y2 - 10, flags)
        
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
    '''
    stage = clutter.Stage()
    stage.set_size(800, 480)
    stage.connect('destroy', clutter.main_quit)
    
    panel = SamplePanel()
    panel.set_position(0, 23)
    panel.set_size(800, 360)
    
    stage.add(panel)
    stage.show()

    clutter.main()
    '''
