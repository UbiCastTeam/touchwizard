#!/usr/bin/env python
# -*- coding: utf-8 -*

import clutter
import gobject

class Canvas(clutter.Actor, clutter.Container):
    __gtype_name__ = 'Canvas'
    infobar_height = 23
    iconbar_height = 120
    
    def __init__(self, first_page):
        clutter.Actor.__init__(self)
        self.first_page = first_page
        
        self.infobar = clutter.Rectangle()
        self.infobar.set_color(clutter.color_from_string('LightGray'))
        self.infobar.set_parent(self)
        
        self.iconbar = clutter.Rectangle()
        self.iconbar.set_color(clutter.color_from_string('LightGray'))
        self.iconbar.set_parent(self)
        
        self.available_pages = self.lookup_pages()
        self.current_page = None
    
    def lookup_pages(self):
        import touchwizard
        
        path = touchwizard.page_path
        if path is None:
            if self.first_page is None:
                return tuple()
            import sys
            module = sys.modules[self.first_page.__module__].__file__
            import os
            path = os.path.dirname(os.path.abspath(os.path.expanduser(module)))
        import imp
        for f in os.listdir(path):
            print f
            if f.endswith('.py') and f != os.path.basename(f):
                print 'ok'
                module = imp.load_source(f[:-3], os.path.join(path, f))
                print module
            else: print 'not ok'
    
    def do_get_preferred_width(self, for_height):
        import touchwizard
        width = float(touchwizard.canvas_width)
        return width, width
    
    def do_get_preferred_height(self, for_width):
        import touchwizard
        height = float(touchwizard.canvas_height)
        return height, height
    
    def do_allocate(self, box, flags):
        canvas_width = box.x2 - box.x1
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
    
    def do_foreach(self, func, data=None):
        children = [self.infobar, self.iconbar]
        if self.current_page is not None:
            children.append(self.current_page.panel)
        for child in children:
            func(child, data)
    
    def do_paint(self):
        children = [self.infobar, self.iconbar]
        if self.current_page is not None:
            children.append(self.current_page.panel)
        for child in children:
            child.paint()


def quick_launch(page):
    import touchwizard
    stage = clutter.Stage()
    stage.set_size(touchwizard.canvas_width, touchwizard.canvas_height)
    if page is not None:
        stage.set_title(page.title)
    stage.connect('destroy', clutter.main_quit)
    
    canvas = Canvas(page)
    
    stage.add(canvas)
    stage.show()

    clutter.main()


if __name__ == '__main__':
    quick_launch(None)
