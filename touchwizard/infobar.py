# -*- coding: utf-8 -*

import clutter
import easyevent
import logging
import candies2
import os

logger = logging.getLogger('touchwizard')

class InfoBar(clutter.Actor, clutter.Container, easyevent.User):
    """
    The icon bar at the top of the wizard canvas.
    
    (Should only be used via events.)
    
    Listen for event:
    
      - info_message (text)
          Display the content to the info bar. Replaces the previous displayed
          text.
    
    Launch no event.
    """
    __gtype_name__ = 'InfoBar'
    
    def __init__(self):
        import touchwizard
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        
        self.background = clutter.Rectangle()
        self.background.set_color(clutter.color_from_string('LightGray'))
        if touchwizard.infobar_bg:
            if os.path.exists(touchwizard.infobar_bg):
                self.background = clutter.Texture(touchwizard.infobar_bg)
                self.background.set_keep_aspect_ratio(True)
            else:
                logger.error('InfoBar background %s not found.',
                                                        touchwizard.infobar_bg)
        self.background.set_parent(self)
        
        self.info_label = candies2.StretchText()
        self.info_label = clutter.Text()
        #self.info_label.set_text('Hello World!')
        self.info_label.set_parent(self)
        
        self.register_event('info_message')
        self.register_event('set_infobar_editable')
        
    def evt_set_infobar_editable(self,event):
        self.info_label.set_editable(True)
        self.info_label.set_cursor_visible(True)
        clutter.Stage().set_key_focus(self.info_label)
   
    def evt_info_message(self, event):
        self.info_label.set_text(event.content)
    
    def do_get_preferred_width(self, for_height):
        return self.info_label.get_preferred_width(for_height)
    
    def do_get_preferred_height(self, for_width):
        min_height, nat_height = \
                           self.info_label.get_preferred_height(for_width - 10)
        if isinstance(self.background, clutter.Texture):
            nat_height = self.background.get_preferred_height(for_width)[1]
        return min_height, nat_height
    
    def do_allocate(self, box, flags):
        bar_width = box.x2 - box.x1
        bar_height = box.y2 - box.y1
        
        bgbox = clutter.ActorBox(0, 0, bar_width, bar_height)
        self.background.allocate(bgbox, flags)
        
        label_height = bar_height
        if '\n' not in self.info_label.get_text():
            label_height = bar_height / 2
        lbox = clutter.ActorBox(5, 0, bar_width - 10, label_height)
        self.info_label.allocate(lbox, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        children = [self.background, self.info_label,]
        for child in children:
            func(child, data)
    
    def do_paint(self):
        children = [self.background, self.info_label,]
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
