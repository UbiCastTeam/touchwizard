# -*- coding: utf-8 -*

import clutter
import easyevent
import logging

logger = logging.getLogger('touchwizard')

class InfoBar(clutter.Actor, clutter.Container, easyevent.User):
    __gtype_name__ = 'InfoBar'
    minimal_fontsize = 5
    
    def __init__(self):
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        
        self.info_label = clutter.Text()
        self.info_label.set_text('Hello World!')
        self.info_label.set_parent(self)
        
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
        if for_width > self.get_preferred_width(-1)[0]:
            pass  #TODO
        return min_height, nat_height
    
    def do_allocate(self, box, flags):
        bar_width = box.x2 - box.x1
        bar_height = box.y2 - box.y1
        fontsize = self.minimal_fontsize
        
        lbl = clutter.Text()
        text = self.info_label.get_text()
        if text.strip():
            lbl.set_text(text)
            while True:
                fontsize += 1
                lbl.set_font_name('Sans %s' %(fontsize))
                if (self.props.request_mode == clutter.REQUEST_HEIGHT_FOR_WIDTH
                                                and lbl.get_width() > bar_width) \
                   or (self.props.request_mode == clutter.REQUEST_WIDTH_FOR_HEIGHT
                                                and lbl.get_height() > bar_height):
                    fontsize -= 1
                    break
        print 'fontsize:', fontsize
        self.info_label.set_font_name('Sans %s' %(fontsize))
        self.info_label.allocate_preferred_size(flags)
        
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
    gobject.timeout_add(2000, info_sender.send_info, 'Goodbye cruel world...')
    gobject.timeout_add(4000, info_sender.send_info, '...')
    gobject.timeout_add(6000, info_sender.send_info, '')
    clutter.main()