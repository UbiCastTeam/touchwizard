# -*- coding: utf-8 -*

import clutter
import gobject
import easyevent
import types
import logging

logger = logging.getLogger('touchwizard')

class Canvas(clutter.Actor, clutter.Container, easyevent.User):
    """ Wizard main actor which manages the user interface and pages.
    
    Listen for event:
    
      - next_page (page_name)
          Request for a new page identified by its name passed as content.
          The current page becomes in top of the page history.
    
      - previous_page
          Request for displaying back the top of the page history. No content
          expected. If the history is empty, quit the wizard.
    
      - request_quit
          Request for quitting the wizard. Send a prepare_quit event to
          notify other components about the quit request and there launch the
          wizard_quit which should be handled by the user main script.
    
    Launch the event:
    
      - prepare_quit
          Sent when a quit request is received by the canvas to notify the
          other component that the wizard is quitting.
    
      - wizard_quit
          Sent after prepare_quit to notify the main script that it can end
          the process.
    
    """
    __gtype_name__ = 'Canvas'
    infobar_height = 23
    iconbar_height = 120
    
    def __init__(self, first_page):
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        
        self.infobar = clutter.Rectangle()
        self.infobar.set_color(clutter.color_from_string('LightGray'))
        self.infobar.set_parent(self)
        
        self.iconbar = clutter.Rectangle()
        self.iconbar.set_color(clutter.color_from_string('LightGray'))
        self.iconbar.set_parent(self)
        
        self.history = list()
        self.first_page = first_page
        self.available_pages = dict()
        self.current_page = None
        self.register_event('next_page', 'previous_page')
        self.register_event('request_quit')
        gobject.idle_add(self.lookup_pages)
        gobject.idle_add(self.display_page, first_page)
    
    def lookup_pages(self):
        import touchwizard
        
        origin = ''
        path = touchwizard.page_path
        if path is None:
            if self.first_page is None:
                return tuple()
            self.available_pages[self.first_page.name] = self.first_page
            import sys
            origin = sys.modules[self.first_page.__module__].__file__
            import os
            path = os.path.dirname(os.path.abspath(os.path.expanduser(origin)))
        import imp
        pages = list()
        for f in os.listdir(path):
            if f.endswith('.py') and f != os.path.basename(origin):
                module = imp.load_source(f[:-3], os.path.join(path, f))
                for attr_name in dir(module):
                    if attr_name.startswith('__'):
                        continue
                    attribute = getattr(module, attr_name)
                    if isinstance(attribute, type) \
                                  and issubclass(attribute, touchwizard.Page) \
                                  and attribute is not touchwizard.Page:
                        self.available_pages[attribute.name] = attribute
        logger.info('%d pages found.', len(self.available_pages))
        #print self.available_pages
    
    def display_page(self, page):
        if isinstance(page, type):
            self.current_page = page()
        else:
            self.current_page = page
        self.current_page.panel.set_parent(self)
        self.current_page.panel.lower_bottom()
    
    def evt_next_page(self, event):
        name = event.content
        logger.info('Page %r requested.', name)
        self.current_page.panel.unparent()
        self.history.append(self.current_page)
        new_page = self.available_pages[name]
        self.display_page(new_page)
    
    def evt_previous_page(self, event):
        previous = self.history.pop()
        if previous is None:
            self.evt_request_quit(event)
            return
        logger.info('Back to %r page.', previous.name)
        self.current_page.panel.unparent()
        self.current_page.panel.destroy()
        self.display_page(previous)
    
    def evt_request_quit(self, event):
        logger.info('Quit requested.')
        self.launch_event('prepare_quit')
        self.launch_event('wizard_quit')
    
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
        
        clutter.Actor.do_allocate(self, box, flags)
    
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
    
    def do_pick(self, color):
        self.do_paint()


def quick_launch(page):
    import sys
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        stream=sys.stderr)
    
    import touchwizard
    stage = clutter.Stage()
    stage.set_size(touchwizard.canvas_width, touchwizard.canvas_height)
    if page is not None:
        stage.set_title(page.title)
    stage.connect('destroy', clutter.main_quit)
    
    canvas = Canvas(page)
    
    stage.add(canvas)
    stage.show()
    
    class Quitter(easyevent.Listener):
        def __init__(self):
            easyevent.Listener.__init__(self)
            self.register_event('wizard_quit')
        def evt_wizard_quit(self, event):
            logging.info('Clutter quit.')
            clutter.main_quit()
    Quitter()

    clutter.main()


if __name__ == '__main__':
    quick_launch(None)
