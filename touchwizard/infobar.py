# -*- coding: utf-8 -*

import clutter
import easyevent
import logging
from candies2 import StretchText

logger = logging.getLogger('touchwizard')

class InfoBar(clutter.Actor, clutter.Container, easyevent.User):
    __gtype_name__ = 'InfoBar'
    
    def __init__(self):
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        
        self.info_label = StretchText()
        self.info_label.set_text('Hello World!')
        self.info_label.set_parent(self)
        
        self.register_event('info_message')
    
    def evt_info_message(self, event):
        self.info_label.set_text(event.content)
    
    def do_get_preferred_width(self, for_height):
        return self.info_label.get_preferred_width(for_height)
    
    def do_get_preferred_height(self, for_width):
        return self.info_label.get_preferred_height(for_width)
    
    def do_allocate(self, box, flags):
        bar_width = box.x2 - box.x1
        bar_height = box.y2 - box.y1
        
        lbox = clutter.ActorBox(0, 0, bar_width, bar_height)
        self.info_label.allocate(lbox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
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


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        stream=sys.stderr)
    
    stage = clutter.Stage()
    stage.set_title('Infobar test')
    stage.connect('destroy', clutter.main_quit)
    
    def add_bar(y, height):
        rect = clutter.Rectangle()
        rect.set_color(clutter.color_from_string('LightBlue'))
        rect.set_y(y)
        rect.set_size(stage.get_width(), height)
        
        bar = InfoBar()
        bar.props.request_mode = clutter.REQUEST_WIDTH_FOR_HEIGHT
        bar.set_y(y)
        bar.set_size(stage.get_width(), height)
        
        stage.add(rect, bar)
    
    add_bar(0, 25)
    add_bar(50 ,50)
    add_bar(125, 100)
    
    stage.show()
    
    import gobject
    class InfoSender(easyevent.Launcher):
        def send_info(self, text):
            self.launch_event('info_message', text)
    info_sender = InfoSender()
    gobject.timeout_add(3000, info_sender.send_info, 'Goodbye cruel world...')
    gobject.timeout_add(6000, info_sender.send_info, '...')
    gobject.timeout_add(9000, info_sender.send_info, '')
    clutter.main()