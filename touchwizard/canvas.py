# -*- coding: utf-8 -*

import clutter
import gobject
import easyevent
import logging
import os
import time

from touchwizard.loading import LoadingWidget

logger = logging.getLogger('touchwizard')


class Canvas(clutter.Actor, clutter.Container, easyevent.User):
    """Wizard main actor which manages the user interface and pages.

    Listen for event:

      - next_page (page_name)
          Request for a new page identified by its name passed as content.
          The current page becomes in top of the page history.

      - previous_page
          Request for displaying back the top of the page history. No content
          expected. If the history is empty, quit the wizard.

      - request_quit
          Request for quitting the wizard. Call prepare_quit callback
          if it exists and there launch the wizard_quit which should
          be handled by the user main script.

    Launch the event:

      - wizard_quit
          Sent after prepare_quit callback to notify the main script that it
          can end the process.
    """

    __gtype_name__ = 'Canvas'
    # infobar_height = 104
    # iconbar_height = 200

    def __init__(self, first_page):
        import touchwizard
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)

        self.session = touchwizard.Session()

        self.background = None
        self.last_page_name = None
        self.last_page_timestamp = None
        self.previous_page_locked = False
        self.previous_page_timeout_id = None

        if touchwizard.canvas_bg:
            if not os.path.exists(touchwizard.canvas_bg):
                logger.error('Canvas background %s not found.', touchwizard.canvas_bg)
            self.background = clutter.Texture(touchwizard.canvas_bg)
            self.background.set_parent(self)

        self.infobar = touchwizard.InfoBar()
        self.infobar.set_parent(self)

        self.iconbar = touchwizard.IconBar()
        self.iconbar.set_parent(self)

        self.loading = LoadingWidget()
        self.loading.set_parent(self)
        self.loading.hide()
        self.loading_padding = 10

        self.home_icon = touchwizard.Icon('shutdown')
        self.home_icon.build()

        self.previous_icon = touchwizard.IconRef(touchwizard.Icon('previous'))
        # self.previous_icon.build()
        easyevent.forward_event('icon_previous_actioned', 'previous_page')

        self.history = list()
        self.first_page = first_page
        self.available_pages = dict()
        self.current_page = None
        self.register_event('next_page', 'previous_page', 'refresh_page', 'clear_history')
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
        for f in os.listdir(path):
            if f.endswith('.py') and f != os.path.basename(origin):
                try:
                    module = imp.load_source(f[:-3], os.path.join(path, f))
                except:
                    import traceback
                    logger.error('Cannot import page %s:\n%s', f[:-3], traceback.format_exc())
                    if not touchwizard.tolerant_to_page_import_error:
                        import sys
                        sys.exit(1)
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
        # print self.available_pages

    def display_page(self, page, icons=None):
        if isinstance(page, type):
            self.current_page = page(self.session)
            if self.current_page.reuse:
                logger.info('Storing reusable page %s in cache.', self.current_page.name)
                self.available_pages[self.current_page.name] = self.current_page
        else:
            self.current_page = page
            logger.info('Reusing already instanciated page %s from cache.', self.current_page.name)
        os.environ["TOUCHWIZARD_CURRENT_PAGE"] = self.current_page.name
        os.environ.pop("TOUCHWIZARD_REQUESTED_PAGE", None)
        if page.need_loading:
            self.loading.hide()
        self._build_iconbar(icons)
        self.current_page.panel.set_parent(self)
        self.current_page.panel.lower_bottom()
        if hasattr(self.current_page.panel, 'prepare') and callable(self.current_page.panel.prepare):
            self.current_page.panel.prepare()
        self.current_page.panel.show()
        self.previous_page_locked = False
        self.last_page_name = page.name

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
        self.home_icon.unregister_all_events()
        if previous_icon is None:
            if self.history:
                last_page, last_icons = self.history[-1]
                previous_icon = last_page.my_icon
                if previous_icon is None:
                    previous_icon = self.previous_icon
            else:
                self.home_icon.register_events()
                previous_icon = self.home_icon
        condition = True
        if isinstance(previous_icon, touchwizard.IconRef):
            if callable(previous_icon.condition):
                condition = previous_icon.condition()
            else:
                condition = previous_icon.condition
            previous_icon = previous_icon.get_icon()
        if condition:
            previous_icon.build()
            self.iconbar.set_previous(previous_icon)

        # Icon "next"
        condition = True
        if next_icon is not None:
            if isinstance(next_icon, touchwizard.IconRef):
                if callable(next_icon.condition):
                    condition = next_icon.condition()
                else:
                    condition = next_icon.condition
                next_icon = next_icon.get_icon()
            if condition:
                next_icon.build()
                self.iconbar.set_next(next_icon)

        # Other icons
        for icon in icons:
            if isinstance(icon, touchwizard.IconRef):
                if callable(icon.condition):
                    condition = icon.condition()
                else:
                    condition = icon.condition
                if not condition:
                    continue
                icon = icon.get_icon()
            icon.build()
            self.iconbar.append(icon)

    def evt_next_page(self, event):
        if self.last_page_name is None or self.last_page_name != event.content:
            gobject.timeout_add(100, self.do_next_page, event, priority=gobject.PRIORITY_HIGH)
            self.unregister_event('next_page')

    def do_next_page(self, event):
        now = time.time()
        name = event.content
        if not self.last_page_timestamp or (now - self.last_page_timestamp) > 0.5:
            logger.info('Page %r requested.', name)
            os.environ["TOUCHWIZARD_REQUESTED_PAGE"] = name
            self.current_page.panel.hide()
            self.current_page.panel.unparent()
            icon_states = self.iconbar.get_icon_states()
            self.history.append((self.current_page, icon_states))
            new_page = self.available_pages[name]
            self.iconbar.clear(keep_back=True)
            if new_page.need_loading:
                self.loading.show()
            gobject.idle_add(self.display_page, new_page)
        else:
            logger.warning('Page %s requested too quickly twice in a row (less than 500ms), not displaying', name)
        self.register_event('next_page')
        self.last_page_timestamp = now

    def evt_previous_page(self, event):
        if not self.previous_page_locked:
            self.previous_page_locked = True
            if self.previous_page_timeout_id is not None:
                gobject.source_remove(self.previous_page_timeout_id)
            self.previous_page_timeout_id = gobject.timeout_add(300, self.do_previous_page, event, priority=gobject.PRIORITY_HIGH)

    def do_previous_page(self, event):
        name = None
        if event.content:
            name = event.content
        for page, icons in self.history[::-1]:
            try:
                previous, icons = self.history.pop()
            except IndexError:
                # logger.error('Previous page requested but history is empty.')
                self.evt_request_quit(event)
                return
            logger.info('Back to %r page.', previous.name)
            os.environ["TOUCHWIZARD_REQUESTED_PAGE"] = previous.name
            self.current_page.panel.hide()
            gobject.idle_add(self.current_page.panel.unparent)
            if previous.need_loading:
                self.loading.show()
            if not self.current_page.reuse:
                gobject.idle_add(self.current_page.panel.destroy)
            if name is None or page.name == name:
                break
            self.current_page = page
        gobject.idle_add(self.display_page, previous, icons)

    def evt_refresh_page(self, event):
        gobject.idle_add(self.do_refresh_page, event)
        self.unregister_event('refresh_page')

    def do_refresh_page(self, event):
        name = self.current_page.name
        logger.info('Page %r refresh requested.', name)
        self.current_page.panel.hide()
        self.current_page.panel.unparent()
        gobject.idle_add(self.current_page.panel.destroy)
        new_page = self.available_pages[name]
        self.iconbar.clear(keep_back=True)
        if new_page.need_loading:
            self.loading.show()
        gobject.idle_add(self.display_page, new_page)
        self.register_event('refresh_page')

    def evt_clear_history(self, event):
        for page, icons in self.history:
            gobject.idle_add(page.panel.destroy)
        self.history = list()

    def evt_request_quit(self, event):
        self.evt_request_quit = self.evt_request_quit_fake
        logger.info('Quit requested.')
        try:
            prepare_quit = getattr(self.current_page, "prepare_quit", None)
            if prepare_quit:
                if not callable(prepare_quit):
                    prepare_quit = getattr(self.current_page.panel, prepare_quit, None)
                if callable(prepare_quit):
                    logger.info('prepare_quit callback found')
                    prepare_quit()
        except Exception, e:
            logger.warning("Failed to call prepare_quit method in page %s: %s", self.current_page, e)
        self.launch_event('wizard_quit')

    def evt_request_quit_fake(self, event):
        logger.error('Quit request rejected.')

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

        infobar_height = round(self.infobar.get_preferred_height(canvas_width)[1])
        infobar_box = clutter.ActorBox()
        infobar_box.x1 = 0
        infobar_box.y1 = 0
        infobar_box.x2 = canvas_width
        infobar_box.y2 = infobar_height
        self.infobar.allocate(infobar_box, flags)

        iconbar_height = round(self.iconbar.get_preferred_height(canvas_width)[1])
        iconbar_box = clutter.ActorBox()
        iconbar_box.x1 = 0
        iconbar_box.y1 = canvas_height - iconbar_height
        iconbar_box.x2 = canvas_width
        iconbar_box.y2 = canvas_height
        self.iconbar.allocate(iconbar_box, flags)

        loading_box = clutter.ActorBox()
        loading_box.x1 = self.loading_padding
        loading_box.y1 = infobar_height + self.loading_padding
        loading_box.x2 = canvas_width - self.loading_padding
        loading_box.y2 = canvas_height - iconbar_height - self.loading_padding
        self.loading.allocate(loading_box, flags)

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
        children = [self.infobar, self.iconbar, self.loading]
        if self.background:
            children.append(self.background)
        if self.current_page:
            children.append(self.current_page.panel)
        for child in children:
            func(child, data)

    def do_paint(self):
        if self.background:
            self.background.paint()
        self.iconbar.paint()
        if self.current_page:
            self.current_page.panel.paint()
        self.infobar.paint()
        self.loading.paint()

    def do_pick(self, color):
        self.do_paint()


def quick_launch(page, width=None, height=None, overlay=None, main_loop_run_cb=None, main_loop_stop_cb=None):
    if not logging._handlers:
        # Install a default log handler if none set
        import sys
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s  %(name)-12s %(levelname)s %(message)s',
            stream=sys.stderr)

    logger.info('Initializing touchwizard app.')
    import touchwizard
    stage = clutter.Stage()
    if width == None and height == None:
        width = touchwizard.canvas_width
        height = touchwizard.canvas_height
    else:
        touchwizard.canvas_width = width
        touchwizard.canvas_height = height
    stage.set_size(width, height)
    if page is not None:
        stage.set_title(page.title)

    canvas = Canvas(page)
    stage.add(canvas)

    if overlay is not None:
        logger.info('Adding overlay %s', overlay)
        stage.add(overlay)
        overlay.show()

    stage.show()

    main_loop_name = 'External'
    if main_loop_run_cb is None:
        main_loop_run_cb = clutter.main
        main_loop_name = 'Clutter'
    if main_loop_stop_cb is None:
        main_loop_stop_cb = clutter.main_quit

    def quit(*args):
        logger.info('Quitting %s main loop by stage destroy', main_loop_name)
        main_loop_stop_cb()
        import sys
        gobject.timeout_add_seconds(2, sys.exit)

    stage.connect('destroy', quit)

    class Quitter(easyevent.Listener):
        def __init__(self):
            easyevent.Listener.__init__(self)
            self.register_event('wizard_quit')

        def evt_wizard_quit(self, event):
            logging.info('Quitting %s main loop by touchwizard button', main_loop_name)
            main_loop_stop_cb()
            import sys
            gobject.timeout_add_seconds(2, sys.exit)

    Quitter()

    logger.info('Running %s main loop.', main_loop_name)
    main_loop_run_cb()

if __name__ == '__main__':
    quick_launch(None)
