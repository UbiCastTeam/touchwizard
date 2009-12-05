#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import clutter
    import touchwizard
    from touchwizard.iconbar import IconBar
    from touchwizard.icon import Icon
    import easyevent
    import sys
    import os
    import logging
    
    __path__ = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    touchwizard.icon_path = __path__

    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        stream=sys.stderr)

    stage = clutter.Stage()
    stage.set_size(1024, 768)
    stage.connect('destroy', clutter.main_quit)

    iconbar = IconBar()
    stage.add(iconbar)
    
    green = Icon('green_button')
    green.build()
    iconbar.set_previous(green)

    nb_blue_buttons = 6
    for i in range(nb_blue_buttons):
        blue = Icon('blue_button')
        blue.build()
        iconbar.append(blue)
    
    red = Icon('red_button')
    red.build()
    iconbar.set_next(red)

    iconbar.set_size(stage.get_width(), iconbar.get_preferred_height(stage.get_width())[1])
    iconbar.set_position(0, stage.get_height() - iconbar.get_height())
    
    stage.show()

    clutter.main()
