#!/usr/bin/env python
# -*- coding: utf-8 -*

import touchwizard
import clutter
import candies2
import easyevent

class SamplePanel2(candies2.container.ContainerAdapter, easyevent.User,
                                             clutter.Actor, clutter.Container):
    __gtype_name__ = 'SamplePanel2'
    
    def __init__(self):
        candies2.container.ContainerAdapter.__init__(self)
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        self.connect('notify::visible', self.on_show)
        
        self.label = clutter.Text()
        #self.label.set_text('Really quit ?')
        self.label.set_font_name('Sans 26')
        self.add(self.label)
        
        self.ok = candies2.ClassicButton('Yeah!')
        self.ok.set_reactive(True)
        self.ok.connect('button-press-event', self.on_ok_pressed)
        self.add(self.ok)
        
        self.cancel = candies2.ClassicButton('Oops..')
        self.cancel.set_reactive(True)
        self.cancel.connect('button-press-event', self.on_cancel_pressed)
        self.add(self.cancel)
    
    def on_show(self, panel, event):
        self.launch_event('info_message', 'Really quit ?')
    
    def on_ok_pressed(self, button, event):
        self.launch_event('request_quit')
        return True
    
    def on_cancel_pressed(self, button, event):
        self.launch_event('previous_page')
        return True
    
    def do_get_preferred_width(self, for_height):
        label_prefs = self.label.get_preferred_width(for_height)
        ok_prefs = self.ok.get_preferred_width(for_height)
        cancel_prefs = self.cancel.get_preferred_width(for_height)
        return (
            label_prefs[0] + max(ok_prefs[0], cancel_prefs[0]),
            label_prefs[1] + max(ok_prefs[1], cancel_prefs[1]),
        )
    
    def do_get_preferred_height(self, for_width):
        label_prefs = self.label.get_preferred_height(for_width)
        ok_prefs = self.ok.get_preferred_height(for_width)
        cancel_prefs = self.cancel.get_preferred_height(for_width)
        return (
            max(label_prefs[0], ok_prefs[0] + cancel_prefs[0]),
            max(label_prefs[1], ok_prefs[1] + cancel_prefs[1]),
        )
    
    def do_allocate(self, box, flags):
        self.label.allocate_available_size(5, 5, box.x2 - 10, box.y2 - 10, flags)
        
        bbox = clutter.ActorBox()
        btn_width = (box.x2 - box.x1) / 5
        bbox.x1 = btn_width
        bbox.x2 = btn_width * 2
        bbox.y1 = (box.y2 - box.y1) / 3
        bbox.y2 = bbox.y1 * 2
        self.ok.allocate(bbox, flags)
        
        bbox = clutter.ActorBox()
        bbox.x1 = btn_width * 3
        bbox.x2 = btn_width * 4
        bbox.y1 = (box.y2 - box.y1) / 3
        bbox.y2 = bbox.y1 * 2
        self.cancel.allocate(bbox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)

class Page(touchwizard.Page):
    title = 'Test Page 2/2'
    name = 'test2'
    panel = SamplePanel2

if __name__ == '__main__':
    touchwizard.quick_launch(Page)
