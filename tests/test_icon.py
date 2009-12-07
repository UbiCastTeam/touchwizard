#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import clutter
    import touchwizard
    import easyevent
    import sys
    import logging

    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        stream=sys.stderr)

    stage = clutter.Stage()
    stage.set_size(640, 480)
    stage.connect('destroy', clutter.main_quit)

    green = touchwizard.Icon('green_button')
    green.build()

    blue = touchwizard.Icon('blue_button')
    blue.build()
    blue.set_x(132)

    red = touchwizard.Icon('red_button')
    red.build()
    red.set_x(264)
    
    toggle = touchwizard.Icon('toggle')
    toggle.build()
    toggle.set_x(396)

    easyevent.forward_event(
                         'icon_red_button_actioned', 'lock_icon_blue_button', True)
    easyevent.forward_event(
                      'icon_green_button_actioned', 'lock_icon_blue_button', False)

    stage.add(green, blue, red, toggle)
    stage.show()

    clutter.main()
