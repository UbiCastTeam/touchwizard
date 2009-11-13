# -*- coding: utf-8 -*

import clutter
import easyevent

class InfoBar(clutter.Actor, clutter.Container, easyevent.User):
    __gtype_name__ = 'InfoBar'
    minimal_fontsize = 5
    
    def __init__(self):
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        
        self.info_label = clutter.Text()
        
        self.register_event('info_message')
    
    def evt_info_message(self, event):
        self.info_label.set_text(event.content)
    
    def do_get_preferred_width(self, for_height):
        lbl = clutter.Text()
        lbl.set_text(self.info_label.get_text())
        nat_width = lbl.get_preferred_width(for_height)[1]
        lbl.set_font_name('Sans %s' %(self.minimal_fontsize))
        min_width = lbl.get_width()
        return min_width, nat_width
    
    def do_get_preferred_height(self, for_width):
        lbl = clutter.Text()
        lbl.set_text(self.info_label.get_text())
        nat_height = lbl.get_preferred_height(for_width)[1]
        lbl.set_font_name('Sans %s' %(self.minimal_fontsize))
        min_height = lbl.get_height()
        return min_height, nat_height
    
    def do_allocate(self, box, flags):
        """canvas_width = box.x2 - box.x1
        canvas_height = box.y2 - box.y1
        
        box = clutter.ActorBox()
        box.x1 = 0
        box.y1 = 0
        box.x2 = canvas_width
        box.y2 = self.infobar_height
        self.infobar.allocate(box, flags)
        
        box = clutter.ActorBox()
        box.x1 = 0
        box.y1 = canvas_height - self.iconbar_height
        box.x2 = canvas_width
        box.y2 = canvas_height
        self.iconbar.allocate(box, flags)
        
        if self.current_page is not None:
            box = clutter.ActorBox()
            box.x1 = 0
            box.y1 = self.infobar_height
            box.x2 = canvas_width
            box.y2 = canvas_height - self.iconbar_height
            self.current_page.panel.allocate(box, flags)
        """
    
    def do_foreach(self, func, data=None):
        children = [self.info_label,]
        for child in children:
            func(child, data)
    
    def do_paint(self):
        children = [self.info_label,]
        for child in children:
            child.paint()
    
    def do_pick(self, color):
        self.do_paint()