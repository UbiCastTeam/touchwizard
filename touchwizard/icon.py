# -*- coding: utf-8 -*-

import os
import clutter
import gobject
import easyevent
import candies2
import logging
import touchwizard

logger = logging.getLogger('touchwizard')

class IconRef(object):
    """Abtract reference to an Icon instance. Avoid the need to instanciate
    several times the same icon. Allows to change some initial states of
    the referenced icon without changing the icon itself.
    
    Used for abstract page declarations.
    """
    
    def __init__(self, icon, label=None, is_locked=None, is_on=False,
                                                cooldown=None, condition=True):
        self.icon = icon
        self.label = label
        self.is_locked = is_locked
        self.is_on = is_on
        self.cooldown = cooldown
        self.condition = condition
    
    def get_icon(self):
        icon = Icon(self.icon.name, self.icon.label_text)
        if self.label is not None:
            icon.label_text = self.label
        if self.is_locked is not None:
            icon.is_locked = self.is_locked
        if self.is_on is not None:
            icon.is_on = self.is_on
        if self.cooldown is not None:
            icon.cooldown_ms = self.cooldown
        return icon


class Icon(clutter.Actor, clutter.Container, easyevent.User):
    """Represent a icon. Instanciated when defining an abstract page and built
    as a clutter actor at runtime.
    
    (Note: the event types depends on the icon name passed to the constructor.)
    
    Listen for event:
    
      - lock_icon_<name> (is_locked)
          Lock the icon (make it disabled) if the content is True or not set.
          Unlock the icon (make it enabled) it the content is False.

      - set_icon_<name> ({'toset': 'label', 'value': 'New text'})
          Reset some of the icon attributes

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
    default_cooldown = 500
    actioned_event_type_pattern = 'icon_%s_actioned'
    lock_event_type_pattern = 'lock_icon_%s'
    set_event_type_pattern = 'set_icon_%s'
    action_event_type_pattern = 'action_icon_%s'
    
    def __init__(self, name, label=None):
        self.name = name
        if label is None:
            label = name.replace('_', ' ').title()
        self.label_text = label
        self.event_type = self.actioned_event_type_pattern %(name)
        self.cooldown_ms = self.default_cooldown
        self.is_locked = False
        self.is_on = False
        self.picture = None
        self.picture_on = None
        self.picture_off = None
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

        # Remotely set icon parameters
        set_event_type = self.set_event_type_pattern %(self.name)
        #logger.debug('Registering to event type %s.', lock_event_type)
        self.register_event(set_event_type)
        setattr(self, 'evt_' + set_event_type, self.evt_set_icon)

        # Remotely simulate a button click (operation and/or animation)
        action_event_type = self.action_event_type_pattern %(self.name)
        #logger.debug('Registering to event type %s.', action_event_type)
        self.register_event(action_event_type)
        setattr(self, 'evt_' + action_event_type, self.action)
        
        self.label = candies2.StretchText()
        self.label.set_font_name('Sans 16')
        self.label.set_color(touchwizard.font_color)
        self.label.set_parent(self)
        try:
            self.label_text = _(self.label_text)
        except NameError:
            pass

        self._build_picture()

        self.update_text()
       
        self.timeline = clutter.Timeline(600)
        alpha = clutter.Alpha(self.timeline, clutter.EASE_OUT_ELASTIC)
        self.animation = \
                        clutter.BehaviourScale(1.1, 1.1, 1.0, 1.0, alpha=alpha)
        self.animation.apply(self.picture)

    def update_text(self):
        if self.is_toggle():
            if self.is_on:
                self.label.set_text("%s: on" %self.label_text)
            else:
                self.label.set_text("%s: off" %self.label_text)
        else:
            self.label.set_text(self.label_text)

    def is_toggle(self):
        if self.picture_on is not None and self.picture_off is not None:
            return True
        return False

    def _build_picture(self):
        import touchwizard
        images_path = touchwizard.images_path or ''
        picture_path = os.path.join(images_path, 'iconbar', '%s.png' %(self.name))
        
        picture_on = os.path.join(images_path, 'iconbar', '%s_on.png' %(self.name))
        picture_off = os.path.join(images_path, 'iconbar', '%s_off.png' %(self.name))
        if os.path.exists(picture_on):
            self.picture_on = picture_on
        if os.path.exists(picture_off):
            self.picture_off = picture_off
        
        is_on = None
        if os.path.exists(picture_path):
            self.picture = IconPicture(picture_path)
        elif self.is_toggle():
            picture_path = self.picture_off
            is_on = self.is_on is True
            if self.is_on:
                picture_path = self.picture_on
            self.picture = IconPicture(picture_path)
        else:
            logger.error('in icon: Icon file %s does not exist.', picture_path)
            self.picture = candies2.ClassicButton('no icon')
        
        candies2.SimpleClick(self.picture)
        self.picture.set_parent(self)
        self.picture.set_reactive(True)
        self.picture.connect('simple-click-event', lambda src: self.action())
        
        if not isinstance(self.picture, candies2.ClassicButton):
            if self.picture_on is None and self.picture_off is not None:
                self.picture_on = picture_path
                is_on = True
            elif self.picture_off is None and self.picture_on is not None:
                self.picture_off = picture_path
                is_on = False
        
        is_on = is_on is True
        if self.is_on is not None and is_on != self.is_on:
            self.toggle()
        self.is_on = is_on
        
        if self.is_locked:
            self.lock()
    
    def do_get_preferred_width(self, for_height):
        picture_width = self.picture.get_preferred_width(-1)
        picture_height = self.picture.get_preferred_height(picture_width[1])[1]
        label_height = (for_height - picture_height) / 2
        label_width = self.label.get_preferred_width(label_height)
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
        
        picture_width, picture_height = self.picture.get_preferred_size()[2:]
        if isinstance(self.picture, candies2.ClassicButton):
            picture_height = icon_height - 128
        boxes[self.picture].y1 = icon_height - picture_height
        boxes[self.picture].y2 = icon_height
        
        label_height = boxes[self.picture].y1 / 2
        label_width = self.label.get_preferred_width(label_height)[1]
        if label_width > icon_width:
            label_width = icon_width
            label_height = self.label.get_preferred_height(label_width)[1]
        boxes[self.label].y1 = (boxes[self.picture].y1 - label_height) / 2
        boxes[self.label].y2 = boxes[self.label].y1 + label_height
        
        if label_width > picture_width:
            largest = self.label
            largest_width = label_width
            thinest = self.picture
            thinest_width = picture_width
        else:
            thinest = self.label
            thinest_width = label_width
            largest = self.picture
            largest_width = picture_width
        thinest.get_preferred_size()[2]
        boxes[thinest].x1 = (largest_width - thinest_width) / 2
        boxes[largest].x1 = 0
        
        boxes[self.picture].x2 = boxes[self.picture].x1 + picture_width
        boxes[self.label].x2 = boxes[self.label].x1 + label_width
        
        #self.lblback.allocate(boxes[self.label], flags)
        self.label.allocate(boxes[self.label], flags)
        self.picture.allocate(boxes[self.picture], flags)
        #self.back.allocate(clutter.ActorBox(0, 0, icon_width, icon_height), flags)
        clutter.Actor.do_allocate(self, box, flags)
    
    def action(self, event=None):
        what_to_do = self.ACTION_ANIMATE_AND_OPERATE
        new_state = None
        if event is not None and event.content is not None:
            what_to_do = event.content
            if isinstance(event.content, dict):
                what_to_do = event.content['action']
                new_state = event.content['state']
        actions = (self.ACTION_ANIMATE_AND_OPERATE, self.ACTION_ANIMATE_ONLY)
        if self.is_locked:
            actions = (self.ACTION_ANIMATE_ONLY, )
        if what_to_do in actions:
            self.toggle(new_state)
            self.animate()
        actions = (self.ACTION_ANIMATE_AND_OPERATE, self.ACTION_OPERATE_ONLY)
        if what_to_do in actions:
            if not self.is_locked:
                self.lock_for(self.cooldown_ms)
                self.launch_event(self.event_type, self.is_on)
            else:
                if self.cooldown_ms >= 1000:
                    self.launch_event('info_message',
                           'Please wait %d seconds' %(self.cooldown_ms / 1000))
    
    def animate(self):
        self.timeline.start()
    
    def toggle(self, new_state=None):
        if self.is_toggle():
            if new_state is None:
                self.is_on = not self.is_on
                if self.is_on:
                    self.label.set_text("%s: on" %self.label_text)
                else:
                    self.label.set_text("%s: off" %self.label_text)
            else:
                logger.debug('in icon: New state is %s', new_state)
                self.is_on = new_state
            picture_path = self.picture_off
            if self.is_on:
                picture_path = self.picture_on
            logger.debug('in icon: toggle request, %s', picture_path)
            self.picture.set_from_file(picture_path)
    
    def lock(self):
        logger.debug('in icon: locking %s.', self.name)
        self.is_locked = True
        self.picture.set_opacity(80)
        self.picture.set_reactive(False)
        return True

    def lock_for(self, duration):
        self.lock()
        gobject.timeout_add(duration, self.unlock)

    def unlock(self):
        logger.debug('in icon: unlocking %s.', self.name)
        self.is_locked = False
        self.picture.set_reactive(True)
        self.picture.set_opacity(255)
        return False

    def evt_set_icon(self, event):
        if isinstance(event.content, dict):
            toset = event.content.get('toset', 'label')
            value = event.content.get('value', None)
            mode = event.content.get('mode', 'replace')
            if toset == 'label' and value is not None:
                if mode == 'replace':
                    self.label_text = value
                elif mode == 'append':
                    value = str(value)
                    if not hasattr(self, 'base_text'):
                        self.base_text = self.label_text
                    self.label_text = '%s %s' %(self.base_text, value)
                self.update_text()

    def evt_lock_icon(self, event):
        if event.content is not False:
            operation = 'lock'
        else:
            operation = 'unlock'
        logger.debug('in icon: Remote %s request received for %s.',
                                                          operation, self.name)
        call_method = getattr(self, operation)
        call_method()
    
    def do_foreach(self, func, data=None):
        children = (self.label, self.picture)
        #children = (self.back, self.lblback) + children
        for child in children:
            func(child, data)
    
    def do_paint(self):
        children = (self.label, self.picture)
        #children = (self.back, self.lblback) + children
        for child in children:
            child.paint()
    
    def do_pick(self, color):
        self.do_paint()
    
    def do_destroy(self):
        self.unregister_all_events()

class IconPicture(clutter.Texture):
    __gtype_name__ = 'IconPicture'
    
    def do_get_preferred_width(self, for_height):
        import touchwizard
        min, nat = clutter.Texture.do_get_preferred_width(self, for_height)
        return min * touchwizard.scaling_ratio, nat * touchwizard.scaling_ratio
    
    def do_get_preferred_height(self, for_width):
        import touchwizard
        min, nat = clutter.Texture.do_get_preferred_height(self, for_width)
        return min * touchwizard.scaling_ratio, nat * touchwizard.scaling_ratio
