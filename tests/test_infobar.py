#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import clutter
    import touchwizard
    import easyevent
    import sys
    import os
    import logging
    import gobject
    from touchwizard.infoicon import InfoIcon
    
    __path__ = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    touchwizard.images_path = os.path.join(__path__, 'images')
    touchwizard.infobar_font = 'Sans 24'

    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        stream=sys.stderr)
    
    stage = clutter.Stage()
    stage.set_title('Infobar test')
    stage.set_size(900, 400)
    stage.connect('destroy', clutter.main_quit)
    
    
    def add_bar(y, height):
        rect = clutter.Rectangle()
        rect.set_color(clutter.color_from_string('LightBlue'))
        rect.set_y(y)
        rect.set_size(stage.get_width(), height)
        
        bar = touchwizard.InfoBar()
        #bar.props.request_mode = clutter.REQUEST_WIDTH_FOR_HEIGHT
        bar.set_y(y)
        bar.set_size(stage.get_width(), height)
        
        # icons
        red = InfoIcon('red_button', 'text')
        gobject.timeout_add(100, actor_loop, red)
        green = InfoIcon('green_button', 'text2 alignment\nmulti')
        blue = InfoIcon('blue_button')
        
        bar.icon_manager.add(red, green, blue)
        
        stage.add(rect, bar)
    
    def actor_loop(actor, count=0):
        count += 1
        if count > 3:
            count = 0
        if count == 0:
            actor.content.set_inner_color('#226688ff')
        elif count == 1:
            actor.content.set_inner_color('#000000ff')
        elif count == 2:
            actor.content.set_inner_color('#445566ff')
        elif count == 3:
            actor.content.set_inner_color('#8899eeff')
        gobject.timeout_add(100, actor_loop, actor, count)
        return False
            
    
    #add_bar(0, 25)
    #add_bar(50 ,50)
    add_bar(125, 100)
    
    stage.show()
    
    class InfoSender(easyevent.Launcher):
        def send_info(self, text):
            self.launch_event('infobar_message', text)
    info_sender = InfoSender()
    gobject.timeout_add(2000, info_sender.send_info, 'Hello world')
    gobject.timeout_add(3000, info_sender.send_info, dict(text='How are you ?'))
    gobject.timeout_add(6000, info_sender.send_info, dict(text="I'm fine and you ?", autoclear=True, autoclear_delay=1000))
    gobject.timeout_add(9000, info_sender.send_info, dict(text='Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.', type='error'))
    gobject.timeout_add(10000, info_sender.send_info, dict(text='Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'))
    clutter.main()
