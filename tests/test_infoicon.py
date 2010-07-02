#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import clutter
    import touchwizard
    import easyevent
    import sys
    import logging
    from touchwizard.infoicon import InfoIcon

    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        stream=sys.stderr)

    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    red = InfoIcon('red_button', 'text')
    red.set_x(350)
    
    green = InfoIcon('green_button', 'text2 alignment\nmulti')
    green.set_x(50)
    green.set_y(300)

    blue = InfoIcon('blue_button')
    blue.set_x(50)

    #easyevent.forward_event('icon_red_button_actioned', 'lock_icon_blue_button', True)
    #easyevent.forward_event('icon_green_button_actioned', 'lock_icon_blue_button', False)

    stage.add(blue, red, green)
    stage.show()

    clutter.main()
