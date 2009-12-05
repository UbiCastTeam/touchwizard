# -*- coding: utf-8 -*-

import os
import clutter
import gobject
import easyevent
import candies2
import logging

logger = logging.getLogger('icon')

class IconRef(object):
    
    def __init__(self, icon, label=None, is_locked=None):
        self.icon = icon
        self.label = label
        self.is_locked = is_locked
    
    def get_icon(self):
        icon = Icon(self.icon.name, self.icon.label)
        if self.label is not None:
            icon.label = self.label
        if self.is_locked is not None:
            icon.is_locked = self.is_locked
        return icon


class Icon(clutter.Actor, clutter.Container, easyevent.User):
    """Represent a icon. Instanciated when defining an abstract page and built
    as a clutter actor at runtime.
    
    (Note: the event types depends on the icon name passed to the constructor.)
    
    Listen for event:
    
      - lock_icon_<name> (is_locked)
          Lock the icon (make it disabled) if the content is True or not set.
          Unlock the icon (make it enabled) it the content is False.
    
      - action_icon_<name> (what_to_do)
          Simulates an icon push. Depending on the content value, either it
          discretely runs the operation that an icon push do (if content set to
          Icon.ACTION_OPERATE_ONLY), or it only animates as when pushed but
          does not anything else (if content set to Icon.ACTION_ANIMATE_ONLY),
          or it does both actions as a real icon push (if content not set or
          set to Icon.ACTION_ANIMATE_AND_OPERATE).
    
    Launch the event:
    
      - icon_<name>_actioned
          Sent when the icon is pushed. Note that this event is also sent after
          receiving an action_icon_<name> event type with a content set to
          Icon.ACTION_OPERATE_ONLY or Icon.ACTION_ANIMATE_AND_OPERATE.
    """
    ACTION_ANIMATE_AND_OPERATE, ACTION_ANIMATE_ONLY, ACTION_OPERATE_ONLY = \
                                                                       range(3)
    __gtype_name__ = 'Icon'
    default_cooldown = 100
    actioned_event_type_pattern = 'icon_%s_actioned'
    lock_event_type_pattern = 'lock_icon_%s'
    action_event_type_pattern = 'action_icon_%s'
    
    def __init__(self, name, label=None):
        self.name = name
        if label is None:
            label = name.replace('_', ' ').title()
        self.label_text = label
        self.event_type = self.actioned_event_type_pattern %(name)
        self.cooldown_ms = self.default_cooldown
        self.is_locked = False
        self.__is_built = False
    
    def build(self):
        if self.__is_built:
            return
        self.__is_built = True
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        
        # Remotely (un)lock icon
        lock_event_type = self.lock_event_type_pattern %(self.name)
        #logger.debug('Registering to event type %s.', lock_event_type)
        self.register_event(lock_event_type)
        setattr(self, 'evt_' + lock_event_type, self.evt_lock_icon)
        
        # Remotely simulate a button click (operation and/or animation)
        action_event_type = self.action_event_type_pattern %(self.name)
        #logger.debug('Registering to event type %s.', action_event_type)
        self.register_event(action_event_type)
        setattr(self, 'evt_' + action_event_type, self.action)
        
        import touchwizard
        picture_path = \
               os.path.join(touchwizard.icon_path or '', "%s.png" %(self.name))
        if not os.path.exists(picture_path):
            self.picture = candies2.ClassicButton('no icon')
        else:
            self.picture = clutter.Texture(picture_path)
            self.picture.set_keep_aspect_ratio(True)
        candies2.SimpleClick(self.picture)
        self.picture.set_parent(self)
        self.picture.set_reactive(True)
        self.picture.connect('simple-click-event',
                                                     lambda src: self.action())
        
        self.timeline = clutter.Timeline(600)
        alpha = clutter.Alpha(self.timeline, clutter.EASE_OUT_ELASTIC)
        self.animation = \
                        clutter.BehaviourScale(1.1, 1.1, 1.0, 1.0, alpha=alpha)
        self.animation.apply(self.picture)
        
        self.label = clutter.Text()
        self.label.set_parent(self)
        self.label.set_text(self.label_text)
    
    def do_get_preferred_width(self, for_height):
        label_width = self.label.get_preferred_width(-1)
        picture_width = self.picture.get_preferred_width(-1)
        icon_width = (
            max(label_width[0], picture_width[0]),
            max(label_width[1], picture_width[1])
        )
        return icon_width
    
    def do_get_preferred_height(self, for_width):
        label_height = self.label.get_preferred_height(for_width)
        picture_height = self.picture.get_preferred_height(for_width)
        icon_height = (
            label_height[0] + picture_height[0],
            label_height[1] + picture_height[1]
        )
        return icon_height
    
    def do_allocate(self, box, flags):
        icon_width = box.x2 - box.x1
        icon_height = box.y2 - box.y1
        
        boxes = {
            self.label: clutter.ActorBox(),
            self.picture: clutter.ActorBox()
        }
        label_width = self.label.get_preferred_size()[2]
        label_height = self.label.get_preferred_size()[3]
        picture_width = self.picture.get_preferred_size()[2]
        picture_height = self.picture.get_preferred_size()[3]
        if isinstance(self.picture, candies2.ClassicButton):
            picture_height = icon_height - label_height
        
        if label_width > picture_width:
            largest = self.label
            thinest = self.picture
        else:
            thinest = self.label
            largest = self.picture
        largest_width = largest.get_preferred_size()[2]
        thinest_width = thinest.get_preferred_size()[2]
        boxes[thinest].x1 = (largest_width - thinest_width) / 2
        boxes[largest].x1 = 0
        
        boxes[self.label].x2 = boxes[self.label].x1 + label_width
        boxes[self.label].y1 = 0
        boxes[self.label].y2 = label_height
        
        boxes[self.picture].x2 = boxes[self.picture].x1 + picture_width
        boxes[self.picture].y1 = boxes[self.label].y2
        boxes[self.picture].y2 = boxes[self.picture].y1 + picture_height
        
        b = boxes[self.label]
        b = boxes[self.picture]
        
        self.label.allocate(boxes[self.label], flags)
        self.picture.allocate(boxes[self.picture], flags)
        clutter.Actor.do_allocate(self, box, flags)
    
    def action(self, event=None):
        what_to_do = self.ACTION_ANIMATE_AND_OPERATE
        if event is not None and event.content is not None:
            what_to_do = event.content
        if what_to_do in (self.ACTION_ANIMATE_AND_OPERATE, self.ACTION_OPERATE_ONLY):
            if not self.is_locked:
                self.lock_for(self.cooldown_ms)
                self.launch_event(self.event_type)
            else:
                self.launch_event('info',
                               'Please wait %d seconds' %(self.cooldown_ms / 1000))
        if what_to_do in (self.ACTION_ANIMATE_AND_OPERATE, self.ACTION_ANIMATE_ONLY):
            self.animate()
    
    def animate(self):
        self.timeline.start()
    
    def lock(self):
        logger.debug('Locking %s.', self.name)
        self.is_locked = True
        self.picture.set_opacity(80)
        return True

    def lock_for(self, duration):
        self.lock()
        gobject.timeout_add(duration, self.unlock)

    def unlock(self):
        logger.debug('Unlocking %s.', self.name)
        self.is_locked = False
        self.picture.set_opacity(255)
        return False

    def evt_lock_icon(self, event):
        if event.content is not False:
            operation = 'lock'
        else:
            operation = 'unlock'
        logger.debug('Remote %s request received for %s.',
                                                          operation, self.name)
        call_method = getattr(self, operation)
        call_method()
    
    def do_foreach(self, func, data=None):
        children = (self.label, self.picture)
        for child in children:
            func(child, data)
    
    def do_paint(self):
        children = (self.label, self.picture)
        for child in children:
            child.paint()
    
    def do_pick(self, color):
        self.do_paint()
