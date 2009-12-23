# -*- coding: utf-8 -*

import clutter
import easyevent
import logging
import candies2
import pango
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
    locations = ('top-left', 'top-right', 'bottom-left', 'bottom-right')
    styles = dict(normal='Black', reverted='White', error='Red')

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
        self.__stage = None

        self.labels = dict()
        for location in self.locations:
            #label = candies2.StretchText()
            label = clutter.Text()
            if touchwizard.infobar_font:
                label.set_font_name(touchwizard.infobar_font)
            label.set_parent(self)
            self.labels[location] = label

        self.ellipsis = clutter.Text()
        self.ellipsis.set_text('...')
        if touchwizard.infobar_font:
            self.ellipsis.set_font_name(touchwizard.infobar_font)

        self.editable_label = clutter.Text()
        if touchwizard.infobar_font:
                self.editable_label.set_font_name(touchwizard.infobar_font)
        self.editable_label.set_editable(True)
        self.editable_label.set_cursor_visible(True)
        self.editable_label.hide()
        self.editable_label.set_parent(self)

        self.register_event('info_message')
        self.register_event('set_infobar_editable')
        self.register_event('request_infobar_editable')
        self.register_event('clear_infobar')

    @property
    def stage(self):
        if self.__stage is not None:
            return self.__stage
        actor = self
        while actor.get_parent() is not None:
            actor = actor.get_parent()
        self.__stage = actor
        return actor

#---------------------for keyboard--------------------------
    def evt_request_infobar_editable(self, event):
        self.editable_label.show()
        self.launch_event('infobar_editable_reply', self.editable_label)

    def evt_set_infobar_editable(self,event):
        self.editable_label.set_selection(-1,-1)
        prefix = ''
        print '----------infobar-----------------'
        if event.content is False:
            prefix = 'not '
        logger.info('Setting info bar %seditable.', prefix)
        if event.content:
            self.stage.set_key_focus(self.editable_label)
            for label in self.labels.values():
                label.hide()
            self.editable_label.set_text('')
            self.editable_label.show()
        else:
            self.stage.set_key_focus(None)
            for label in self.labels.values():
                label.show()
            self.editable_label.hide()
#-----------------------------------------------------------

    def evt_info_message(self, event):
        logger.debug('Info message: %s', event.content)
        if self.editable_label.props.visible:
            return
        if not isinstance(event.content, dict):
            event.content = dict(text=event.content)

        new_text = event.content.get('text')
        style = event.content.get('style')
        location = event.content.get('location', self.locations[0])

        if style is None:
            if location.startswith('bottom'):
                style = 'reverted'
            else:
                style = 'normal'

        label = self.labels[location]
        label.set_color(self.styles[style])
        if new_text is not None:
            label.set_text(new_text)

    def evt_clear_infobar(self, event):
        for label in self.labels:
            self.labels[label].set_text('')
    
    def do_get_preferred_width(self, for_height):
        tl_min, tl_nat = \
                        self.labels['top-left'].get_preferred_width(for_height)
        tr_min, tr_nat = \
                       self.labels['top-right'].get_preferred_width(for_height)
        bl_min, bl_nat = \
                     self.labels['bottom-left'].get_preferred_width(for_height)
        br_min, br_nat = \
                    self.labels['bottom-right'].get_preferred_width(for_height)
        min = max(tl_min + tr_min, bl_min, br_min)
        nat = max(tl_nat + tr_nat, bl_nat, br_nat)
        if isinstance(self.background, clutter.Texture):
            nat = self.background.get_preferred_width(for_height)[1]
        return min, nat

    def do_get_preferred_height(self, for_width):
        tl_min, tl_nat = \
                        self.labels['top-left'].get_preferred_height(for_width)
        tr_min, tr_nat = \
                       self.labels['top-right'].get_preferred_height(for_width)
        bl_min, bl_nat = \
                     self.labels['bottom-left'].get_preferred_height(for_width)
        br_min, br_nat = \
                    self.labels['bottom-right'].get_preferred_height(for_width)
        min = max(tl_min + bl_min, tr_min, br_min)
        nat = max(tl_nat + bl_nat, tr_nat, br_nat)
        if isinstance(self.background, clutter.Texture):
            nat = self.background.get_preferred_height(for_width)[1]
        return min, nat

    def do_allocate(self, box, flags):
        bar_width = box.x2 - box.x1
        bar_height = box.y2 - box.y1

        bgbox = clutter.ActorBox(0, 0, bar_width, bar_height)
        self.background.allocate(bgbox, flags)

        available_height = bar_height / 2
        ellipsis_width = self.ellipsis.get_preferred_width(-1)[1]

        label = self.labels['top-left']
        label_width, label_height = label.get_preferred_size()[2:]
        if label_width > bar_width - ellipsis_width - 10:
            label.set_ellipsize(pango.ELLIPSIZE_END)
            label_width = (bar_width - 10) / 2
        else:
            label.set_ellipsize(pango.ELLIPSIZE_NONE)
        tlbox = clutter.ActorBox()
        tlbox.x1 = 5
        tlbox.y1 = (available_height - label_height) / 2
        tlbox.x2 = tlbox.x1 + label_width
        tlbox.y2 = tlbox.y1 + label_height
        label.allocate(tlbox, flags)

        label = self.labels['top-right']
        label_width, label_height = label.get_preferred_size()[2:]
        if label_width > bar_width - tlbox.x2 - 5:
            label.set_ellipsize(pango.ELLIPSIZE_END)
            label_width = bar_width - tlbox.x2 - 5
        else:
            label.set_ellipsize(pango.ELLIPSIZE_NONE)
        trbox = clutter.ActorBox()
        trbox.x2 = bar_width - 5
        trbox.x1 = trbox.x2 - label_width
        trbox.y1 = (available_height - label_height) / 2
        trbox.y2 = trbox.y1 + label_height
        label.allocate(trbox, flags)

        label = self.labels['bottom-left']
        label_width, label_height = label.get_preferred_size()[2:]
        if label_width > bar_width - ellipsis_width - 10:
            label.set_ellipsize(pango.ELLIPSIZE_END)
            label_width = (bar_width - 10) / 2
        else:
            label.set_ellipsize(pango.ELLIPSIZE_NONE)
        blbox = clutter.ActorBox()
        blbox.x1 = 5
        blbox.y1 = available_height + (available_height - label_height) / 2
        blbox.x2 = blbox.x1 + label_width
        blbox.y2 = blbox.y1 + label_height
        label.allocate(blbox, flags)

        label = self.labels['bottom-right']
        label_width, label_height = label.get_preferred_size()[2:]
        if label_width > bar_width - blbox.x2 - 5:
            label.set_ellipsize(pango.ELLIPSIZE_END)
            label_width = bar_width - blbox.x2 - 5
        else:
            label.set_ellipsize(pango.ELLIPSIZE_NONE)
        brbox = clutter.ActorBox()
        brbox.x2 = bar_width - 5
        brbox.x1 = brbox.x2 - label_width
        brbox.y1 = available_height + (available_height - label_height) / 2
        brbox.y2 = brbox.y1 + label_height
        label.allocate(brbox, flags)

        ebox = clutter.ActorBox(5, 0, bar_width - 5, bar_height)
        self.editable_label.allocate(ebox, flags)

        clutter.Actor.do_allocate(self, box, flags)

    def do_foreach(self, func, data=None):
        children = (self.background, self.editable_label) \
                                                  + tuple(self.labels.values())
        for child in children:
            func(child, data)

    def do_paint(self):
        children = (self.background, self.editable_label) \
                                                  + tuple(self.labels.values())
        for child in children:
            child.paint()

    #def do_pick(self, color):
    #    self.do_paint()
