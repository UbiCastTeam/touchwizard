# -*- coding: utf-8 -*-

import clutter
import easyevent
import logging
import os
from icon import IconRef

logger = logging.getLogger('touchwizard')

class IconBar(clutter.Actor, clutter.Container, easyevent.User):
    """
    The icon bar at the bottom of the wizard canvas.
    
    (Should not be used directly.)
    
    Listen for no event.
    
    Launch no event.
    """
    __gtype_name__ = 'IconBar'
    
    def __init__(self):
        import touchwizard
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        
        self.background = clutter.Rectangle()
        self.background.set_color(clutter.color_from_string('LightGray'))
        if touchwizard.iconbar_bg:
            if os.path.exists(touchwizard.iconbar_bg):
                self.background = clutter.Texture(touchwizard.iconbar_bg)
                self.background.set_keep_aspect_ratio(True)
            else:
                logger.error('Iconbar background %s not found.',
                                                        touchwizard.iconbar_bg)
        self.background.set_parent(self)
        
        self._previous = None
        self._icons = list()
        self._next = None
    
    @property
    def _all_icons(self):
        return (self._previous and (self._previous,) or ()) \
               + tuple(self._icons) \
               + (self._next and (self._next,) or ())
    
    def set_previous(self, icon):
        if self._previous is not None:
            self._previous.unparent()
        icon.set_parent(self)
        self._previous = icon
        logger.debug('Adding icon %r as previous.', icon.name)
    
    def set_next(self, icon):
        if self._next is not None:
            self._next.unparent()
        icon.set_parent(self)
        self._next = icon
        logger.debug('Adding icon %r as next.', icon.name)
    
    def append(self, *icons):
        for icon in icons:
            icon.set_parent(self)
            self._icons.append(icon)
            logger.debug('Adding icon %r.', icon.name)
    
    def insert(self, index, icon):
        icon.set_parent(self)
        self._icons.insert(index, icon)
        logger.debug('Inserting icon %r at position %s.', icon.name, index)
    
    def get_icon_states(self):
        icons = list()
        for icon in self._icons:
            ref = IconRef(icon, icon.label_text, icon.is_locked, icon.is_on)
            icons.append(ref)
        return icons
    
    def clear(self):
        for icon in self._all_icons:
            icon.unparent()
            icon.destroy()
        
        self._previous = None
        self._icons = list()
        self._next = None
        logger.debug('Icon bar cleared.')
    
    def __len__(self):
        return len(self._icons)
    
    def do_get_preferred_width(self, for_height):
        min_width = nat_width = 0
        
        for icon in self._all_icons:
            min_icon, nat_icon = icon.get_preferred_width(for_height)
            min_width += min_icon
            nat_width += nat_icon
        
        return min_width, nat_width
    
    def do_get_preferred_height(self, for_width):
        min_height = nat_height = 0
        
        for icon in self._all_icons:
            min_icon, nat_icon = icon.get_preferred_height(-1)
            min_height = max(min_height, min_icon)
            nat_height = max(nat_height, nat_icon)
        
        if isinstance(self.background, clutter.Texture):
            nat_height = self.background.get_preferred_height(for_width)[1]
        return min_height, nat_height
    
    def do_allocate(self, box, flags):
        bar_width = box.x2 - box.x1
        bar_height = box.y2 - box.y1
        
        bbox = clutter.ActorBox(0, 0, bar_width, bar_height)
        self.background.allocate(bbox, flags)
        
        previous_width = 0
        if self._previous is not None:
            previous_width = self._previous.get_preferred_width(bar_height)[1]
            icon_box = clutter.ActorBox(0, 0, previous_width, bar_height)
            self._previous.show()
            self._previous.allocate(icon_box, flags)
        
        next_width = 0
        if self._next is not None:
            next_width = self._next.get_preferred_width(bar_height)[1]
            icon_box = clutter.ActorBox(bar_width - next_width, 0,
                                                         bar_width, bar_height)
            self._next.allocate(icon_box, flags)
        
        if self._icons:
            remaining_width = bar_width - previous_width - next_width
            available_icon_width = remaining_width / len(self._icons)
            
            x = previous_width
            for icon in self._icons:
                icon_box = clutter.ActorBox()
                icon_width = icon.get_preferred_width(bar_height)[1]
                if icon_width < available_icon_width:
                    x_offset = (available_icon_width - icon_width) / 2
                    icon_box.x1 = x + x_offset
                    icon_box.y1 = 0
                    icon_box.x2 = icon_box.x1 + icon_width
                    icon_box.y2 = bar_height
                    x = icon_box.x2 + x_offset
                else:
                    icon_box.x1 = x
                    icon_box.y1 = 0
                    icon_box.x2 = icon_box.x1 + available_icon_width
                    icon_box.y2 = bar_height
                    x = icon_box.x2
                icon.allocate(icon_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        children = (self.background,) + self._all_icons
        for child in children:
            func(child, data)
    
    def do_paint(self):
        children = (self.background,) + self._all_icons
        for child in children:
            child.paint()
    
    def do_pick(self, color):
        self.do_paint()
