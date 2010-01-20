#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import clutter
    import touchwizard
    import easyevent
    import sys
    import os
    import logging
    
    __path__ = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    touchwizard.icon_path = __path__
    touchwizard.infobar_font = 'Sans 24'

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
        
        bar = touchwizard.InfoBar()
        bar.props.request_mode = clutter.REQUEST_WIDTH_FOR_HEIGHT
        bar.set_y(y)
        bar.set_size(stage.get_width(), height)
        
        stage.add(rect, bar)
    
    #add_bar(0, 25)
    #add_bar(50 ,50)
    add_bar(125, 100)
    
    stage.show()
    
    import gobject
    class InfoSender(easyevent.Launcher):
        def send_info(self, text):
            self.launch_event('info_message', text)
    info_sender = InfoSender()
    gobject.timeout_add(2000, info_sender.send_info, 'Hello world')
    gobject.timeout_add(3000, info_sender.send_info, dict(text='How are you ?', location='bottom-left'))
    gobject.timeout_add(6000, info_sender.send_info, dict(text="I'm fine and you ?", location='top-right', autoclear=True, autoclear_delay=1000))
    gobject.timeout_add(9000, info_sender.send_info, dict(text='Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.', location='bottom-right', style='error'))
    gobject.timeout_add(10000, info_sender.send_info, dict(text='Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'))
    clutter.main()
