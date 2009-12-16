# -*- coding: utf-8 -*

import clutter
import gobject
import easyevent
import types
import logging
import os

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
    #infobar_height = 104
    #iconbar_height = 200
    
    def __init__(self, first_page):
        import touchwizard
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        
        self.session = touchwizard.Session()
        
        self.background = None
        if touchwizard.canvas_bg:
            if not os.path.exists(touchwizard.canvas_bg):
                logger.error('Canvas background %s not found.',
                                                         touchwizard.canvas_bg)
            self.background = clutter.Texture(touchwizard.canvas_bg)
            self.background.set_parent(self)
        
        self.infobar = touchwizard.InfoBar()
        self.infobar.set_parent(self)
        
        self.iconbar = touchwizard.IconBar()
        self.iconbar.set_parent(self)
        
        self.home_icon = touchwizard.Icon('shutdown')
        self.home_icon.build()
        easyevent.forward_event('icon_shutdown_actioned', 'request_quit')
        easyevent.forward_event('icon_home_actioned', 'request_quit')
        
        self.previous_icon = touchwizard.Icon('previous')
        self.previous_icon.build()
        easyevent.forward_event('icon_previous_actioned', 'previous_page')
        
        
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
            path = os.path.dirname(os.path.abspath(os.path.expanduser(origin)))
        import imp
        pages = list()
        for f in os.listdir(path):
            if f.endswith('.py') and f != os.path.basename(origin):
                try:
                    module = imp.load_source(f[:-3], os.path.join(path, f))
                except:
                    import traceback
                    logger.error('Cannot import page %s:\n%s',
                                                f[:-3], traceback.format_exc())
                    continue
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
    
    def display_page(self, page, icons=None):
        if isinstance(page, type):
            self.current_page = page()
            if self.current_page.reuse:
                logger.info('Storing reusable page %s in cache.',
                                                        self.current_page.name)
                self.available_pages[self.current_page.name] = \
                                                              self.current_page
        else:
            self.current_page = page
            logger.info('Reusing already instanciated page %s from cache.',
                                                        self.current_page.name)
        self._build_iconbar(icons)
        self.current_page.panel.set_parent(self)
        self.current_page.panel.lower_bottom()
        self.current_page.panel.show()
    
    def _build_iconbar(self, icons):
        import touchwizard
        self.iconbar.clear()
        if icons is not None:
            # cached icons
            previous_icon = icons[0]
            next_icon = icons[-1]
            icons = icons[1:-1]
        else:
            # uninstanciated icons
            icons = self.current_page.icons
            previous_icon = self.current_page.previous
            next_icon = self.current_page.next
        
        # Icon "previous"
        if previous_icon is None:
            if self.history:
                last_page, last_icons = self.history[-1]
                previous_icon = last_page.my_icon
                if previous_icon is None:
                    previous_icon = self.previous_icon
            else:
                previous_icon = self.home_icon
        if isinstance(previous_icon, touchwizard.IconRef):
            previous_icon = previous_icon.get_icon()
        previous_icon.build()
        self.iconbar.set_previous(previous_icon)
        
        # Icon "next"
        if next_icon is not None:
            if isinstance(next_icon, touchwizard.IconRef):
                next_icon = next_icon.get_icon()
            next_icon.build()
            self.iconbar.set_next(next_icon)
        
        # Other icons
        for icon in icons:
            if isinstance(icon, touchwizard.IconRef):
                icon = icon.get_icon()
            icon.build()
            self.iconbar.append(icon)
    
    def evt_next_page(self, event):
        name = event.content
        logger.info('Page %r requested.', name)
        self.current_page.panel.hide()
        self.current_page.panel.unparent()
        icon_states = self.iconbar.get_icon_states()
        self.history.append((self.current_page, icon_states))
        new_page = self.available_pages[name]
        self.display_page(new_page)
    
    def evt_previous_page(self, event):
        try:
            previous, icons = self.history.pop()
        except IndexError:
            #logger.error('Previous page requested but history is empty.')
            self.evt_request_quit(event)
            return
        logger.info('Back to %r page.', previous.name)
        self.current_page.panel.hide()
        self.current_page.panel.unparent()
        if not self.current_page.reuse:
            self.current_page.panel.destroy()
        self.display_page(previous, icons)
    
    def evt_request_quit(self, event):
        logger.info('Quit requested.')
        self.launch_event('prepare_quit')
        self.launch_event('wizard_quit')
    
    def evt_request_session(self, event):
        self.launch_event('dispatch_session', self.session)
    
    def evt_update_session(self, event):
        self.session.update(event)
        self.launch_event('dispatch_session', self.session)
    
    def do_remove(self, actor):
        logger.info.debug('Panel "%s" removed.', actor.__name__)
    
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
        
        infobar_height = self.infobar.get_preferred_height(canvas_width)[1]
        infobar_box = clutter.ActorBox()
        infobar_box.x1 = 0
        infobar_box.y1 = 0
        infobar_box.x2 = canvas_width
        infobar_box.y2 = infobar_height
        self.infobar.allocate(infobar_box, flags)
        
        iconbar_height = self.iconbar.get_preferred_height(canvas_width)[1]
        iconbar_box = clutter.ActorBox()
        iconbar_box.x1 = 0
        iconbar_box.y1 = canvas_height - iconbar_height
        iconbar_box.x2 = canvas_width
        iconbar_box.y2 = canvas_height
        self.iconbar.allocate(iconbar_box, flags)
        
        panel_box = clutter.ActorBox()
        panel_box.x1 = 0
        panel_box.y1 = infobar_height
        panel_box.x2 = canvas_width
        panel_box.y2 = canvas_height - iconbar_height
        if self.background is not None:
            self.background.allocate(panel_box, flags)
        if self.current_page is not None:
            self.current_page.panel.allocate(panel_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        children = [self.infobar, self.iconbar]
        if self.background:
            children.insert(0, self.background)
        if self.current_page is not None:
            children.append(self.current_page.panel)
        for child in children:
            func(child, data)
    
    def do_paint(self):
        children = [self.infobar, self.iconbar]
        if self.background:
            children.insert(0, self.background)
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
