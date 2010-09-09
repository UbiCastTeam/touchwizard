# -*- coding: utf-8 -*

import os
import sys
import datetime
import traceback
import clutter
import easyevent
import logging
import candies2
import pango
import gobject
from infoicon import InfoIcon

logger = logging.getLogger('touchwizard')

class InfoBar(clutter.Actor, clutter.Container, easyevent.User):
    """
    The icon bar at the top of the wizard canvas.

    (Should only be used via events.)

    Listen for events:

        - infobar_connect(on_press_function)

        - infobar_get_messages()

        - infobar_message(text)
          Display the content to the info bar. Replaces the previous displayed text.

        - infobar_clear()
          Clear the content of the info bar.

        - infobar_add_icon(param)

        - infobar_modify_icon(param)

        - infobar_display_icon_tooltip(param)

        - infobar_remove_icon(param)

    Launch no event.
    
    Used images files:
        - <touchwizard images path>/infobar/common/global_bg.png
        - <touchwizard images path>/infobar/common/text_bg_image_left.png
        - <touchwizard images path>/infobar/common/text_bg_image_middle.png
        - <touchwizard images path>/infobar/common/text_bg_image_right.png
        - <touchwizard images path>/infobar/common/icon_bg_image_left.png
        - <touchwizard images path>/infobar/common/icon_bg_image_middle.png
        - <touchwizard images path>/infobar/common/icon_bg_image_right.png
    All images files are optionnal.
    """
    __gtype_name__ = 'InfoBar'

    def __init__(self):
        import touchwizard
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        self._children = list()
        self.images_path = touchwizard.images_path or ''
        self.padding = 10
        self.spacing = 5
        self.hide_id = None
        self._connection_id = None
        self.current_message_id = 0
        self.types = touchwizard.infobar_params['messages_types']
        self._type = self.types.keys()[0]
        self.messages = dict()
        for key in self.types.keys():
            self.messages.update({key: list()})
        
        # Background images
        self.backgrounds_width = touchwizard.infobar_params['backgrounds_width']
        self.global_bg = clutter.Texture()
        self._set_bg_image(self.global_bg, 'global_bg')
        self._add(self.global_bg)
        self.text_bg_left = clutter.Texture()
        self._set_bg_image(self.text_bg_left, 'text_bg_image_left')
        self._add(self.text_bg_left)
        self.text_bg_middle = clutter.Texture()
        self._set_bg_image(self.text_bg_middle, 'text_bg_image_middle')
        self._add(self.text_bg_middle)
        self.text_bg_right = clutter.Texture()
        self._set_bg_image(self.text_bg_right, 'text_bg_image_right')
        self._add(self.text_bg_right)
        self.icon_bg_left = clutter.Texture()
        self._set_bg_image(self.icon_bg_left, 'icon_bg_image_left')
        self._add(self.icon_bg_left)
        self.icon_bg_middle = clutter.Texture()
        self._set_bg_image(self.icon_bg_middle, 'icon_bg_image_middle')
        self._add(self.icon_bg_middle)
        self.icon_bg_right = clutter.Texture()
        self._set_bg_image(self.icon_bg_right, 'icon_bg_image_right')
        self._add(self.icon_bg_right)
        
        # Label
        self.label = candies2.TextContainer(rounded=False, padding=self.padding)
        self.label.set_font_name(touchwizard.infobar_params['text_font_name'])
        self.label.set_font_color(self.types[self._type].get('color', '#ffffffff'))
        self.label.set_inner_color('#00000000')
        self.label.set_border_color('#00000000')
        self.label.set_border_width(0)
        self.label.set_radius(0)
        self.label.set_line_alignment('center')
        self.label.set_line_wrap(True)
        self._add(self.label)
        
        # Icons
        self.icon_manager = IconManager(padding=self.padding, spacing=self.spacing)
        self._add(self.icon_manager)
        
        # Events
        # text
        self.register_event('infobar_connect')
        self.register_event('infobar_get_messages')
        self.register_event('info_message')
        self.register_event('infobar_message')
        self.register_event('infobar_clear')
        # icon
        self.register_event('infobar_add_icon')
        self.register_event('infobar_modify_icon')
        self.register_event('infobar_display_icon_tooltip')
        self.register_event('infobar_remove_icon')
    
    def _set_bg_image(self, texture, image_name):
        image_src = os.path.join(self.images_path, 'infobar', 'common', '%s.png' %image_name)
        if os.path.exists(image_src):
            texture.set_from_file(image_src)
            texture.show()
        else:
            texture.hide()
            logger.error('in infobar: Image file for background (%s) does not exist.', image_src)
    
    def set_type(self, new_type):
        if new_type != self._type and new_type in self.types:
            self._type = new_type
            self.label.set_font_color(self.types[self._type].get('color', '#ffffffff'))
    
    # text evt
    #-----------------------------------------------------------
    def evt_infobar_connect(self, event):
        if self._connection_id is not None:
            self.label.disconnect(self._connection_id)
        self._connection_id = self.label.connect('button-press-event', event.content)
        self.label.set_reactive(True)
    
    def evt_infobar_get_messages(self, event):
        callback = event.content
        if callback is not None:
            try:
                messages = list()
                for key in self.messages.keys():
                    messages.extend(self.messages[key])
                callback(messages)
            except Exception, e:
                logger.error('Error in info bar get messages callback %s: %s' %(callback, e))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_messages = traceback.format_exception(exc_type, exc_value, exc_traceback)
                for error_message in error_messages:
                    for line in error_message.split('\n'):
                        if line.strip():
                            logger.error(line)
        return False
    
    def evt_info_message(self, event):
        self.evt_infobar_message(event)
    
    def evt_infobar_message(self, event):
        if self.hide_id is not None:
            gobject.source_remove(self.hide_id)
        logger.debug('Info message: %s', event.content)
        if not isinstance(event.content, dict):
            event.content = dict(text=event.content)
        
        new_text = event.content.get('text', '')
        new_type = event.content.get('type', 'info')
        autoclear = event.content.get('autoclear', False)
        autoclear_delay = event.content.get('autoclear_delay', 2000)
        
        self.current_message_id += 1
        if new_type not in self.types:
            new_type = self._type
        self.messages[new_type].append(InfoMessage(self.current_message_id, new_type, datetime.datetime.today(), new_text))
        max_messages = self.types[new_type].get('length', 0)
        if max_messages > 0 and len(self.messages[new_type]) > max_messages:
            self.messages[new_type].remove(self.messages[new_type][0])
        self.label.set_text(new_text)
        self.set_type(new_type)
        if autoclear:
            self.hide_id = gobject.timeout_add(autoclear_delay, self.evt_infobar_clear)
        return False
    
    def evt_infobar_clear(self, event=None):
        self.label.set_text('')
        if self.hide_id is not None:
            gobject.source_remove(self.hide_id)
            self.hide_id = None
        return False
    
    # icon evt
    #-----------------------------------------------------------
    def evt_infobar_add_icon(self, event):
        logger.debug('Info bar add icon with properties: %s', event.content)
        if not isinstance(event.content, dict):
            event.content = dict(name=event.content)
        
        name = event.content.get('name')
        label = event.content.get('label', '')
        status = event.content.get('status', None)
        src = event.content.get('src', None)
        clickable = event.content.get('clickable', False)
        on_click_callback = event.content.get('on_click_callback', None)
        tooltips = event.content.get('tooltips', list())
        callback = event.content.get('callback', None)
        
        icon = self.icon_manager.add_icon(name, label, status, src, clickable, on_click_callback, tooltips)
        if callback is not None:
            try:
                callback(icon)
            except Exception, e:
                logger.error('Error in info bar add icon callback %s: %s' %(callback, e))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_messages = traceback.format_exception(exc_type, exc_value, exc_traceback)
                for error_message in error_messages:
                    for line in error_message.split('\n'):
                        if line.strip():
                            logger.error(line)
        return False
    
    def evt_infobar_modify_icon(self, event):
        logger.debug('Info bar change icon param: %s', event.content)
        
        if not isinstance(event.content, dict):
            if isinstance(event.content, str):
                event.content = dict(name=event.content)
            else:
                event.content = dict(actor=event.content)
        
        self.icon_manager.modify_icon(event.content)
        return False
    
    def evt_infobar_display_icon_tooltip(self, event):
        logger.debug('Info bar display icon tooltip: %s', event.content)
        
        if not isinstance(event.content, dict):
            if isinstance(event.content, str):
                event.content = dict(name=event.content)
            else:
                event.content = dict(actor=event.content)
        
        self.icon_manager.display_icon_tooltip(event.content)
        return False
    
    def evt_infobar_remove_icon(self, event):
        logger.debug('Info bar remove icon: %s', event.content)
        
        if not isinstance(event.content, dict):
            if isinstance(event.content, str):
                event.content = dict(name=event.content)
            else:
                event.content = dict(actor=event.content)
        
        self.icon_manager.remove_icon(event.content)
        return False
    
    # allocation and preferred size
    #-----------------------------------------------------------
    def do_get_preferred_width(self, for_height):
        preferred_width = self.icon_manager.get_preferred_width(for_height)[1]
        return preferred_width, preferred_width
    
    def do_get_preferred_height(self, for_width):
        preferred_height = self.icon_manager.get_preferred_height(for_width)[1]
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        bar_width = box.x2 - box.x1
        bar_height = box.y2 - box.y1
        
        icons_width = self.icon_manager.get_preferred_width(bar_height)[1]
        label_width = bar_width - icons_width
        
        # Background images
        box_bg = clutter.ActorBox()
        box_bg.x1 = 0
        box_bg.x2 = bar_width
        box_bg.y1 = 0
        box_bg.y2 = bar_height
        self.global_bg.allocate(box_bg, flags)
        # text_bg_left
        box_text_left = clutter.ActorBox()
        box_text_left.x1 = 0
        box_text_left.x2 = self.backgrounds_width
        box_text_left.y1 = 0
        box_text_left.y2 = bar_height
        self.text_bg_left.allocate(box_text_left, flags)
        # text_bg_middle
        box_text_middle = clutter.ActorBox()
        box_text_middle.x1 = self.backgrounds_width
        box_text_middle.x2 = label_width - self.backgrounds_width
        box_text_middle.y1 = 0
        box_text_middle.y2 = bar_height
        self.text_bg_middle.allocate(box_text_middle, flags)
        # text_bg_right
        box_text_right = clutter.ActorBox()
        box_text_right.x1 = box_text_middle.x2
        box_text_right.x2 = box_text_middle.x2 + self.backgrounds_width
        box_text_right.y1 = 0
        box_text_right.y2 = bar_height
        self.text_bg_right.allocate(box_text_right, flags)
        
        if icons_width > 0:
            # icon_bg_left
            box_icon_left = clutter.ActorBox()
            box_icon_left.x1 = box_text_right.x2
            box_icon_left.x2 = box_text_right.x2 + self.backgrounds_width
            box_icon_left.y1 = 0
            box_icon_left.y2 = bar_height
            self.icon_bg_left.allocate(box_icon_left, flags)
            # icon_bg_middle
            box_icon_middle = clutter.ActorBox()
            box_icon_middle.x1 = box_icon_left.x2
            box_icon_middle.x2 = bar_width - self.backgrounds_width
            box_icon_middle.y1 = 0
            box_icon_middle.y2 = bar_height
            self.icon_bg_middle.allocate(box_icon_middle, flags)
            # icon_bg_right
            box_icon_right = clutter.ActorBox()
            box_icon_right.x1 = box_icon_middle.x2
            box_icon_right.x2 = bar_width
            box_icon_right.y1 = 0
            box_icon_right.y2 = bar_height
            self.icon_bg_right.allocate(box_icon_right, flags)
        else:
            box_icon_left = clutter.ActorBox(0, 0, 0, 0)
            self.icon_bg_left.allocate(box_icon_left, flags)
            # icon_bg_middle
            box_icon_middle = clutter.ActorBox(0, 0, 0, 0)
            self.icon_bg_middle.allocate(box_icon_middle, flags)
            # icon_bg_right
            box_icon_right = clutter.ActorBox(0, 0, 0, 0)
            self.icon_bg_right.allocate(box_icon_right, flags)
        
        # Label
        box_label = clutter.ActorBox()
        box_label.x1 = 0
        box_label.x2 = label_width
        box_label.y1 = 0
        box_label.y2 = bar_height
        self.label.allocate(box_label, flags)
        
        # Icons
        box_icons = clutter.ActorBox()
        box_icons.x1 = label_width
        box_icons.x2 = bar_width
        box_icons.y1 = 0
        box_icons.y2 = bar_height
        self.icon_manager.allocate(box_icons, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    #-----------------------------------------------------------
    def _add(self, *children):
        for child in children:
            child.set_parent(self)
            self._children.append(child)
    
    def do_foreach(self, func, data=None):
        for child in self._children:
            func(child, data)
        
    def do_paint(self):
        for actor in self._children:
            actor.paint()
    
    def do_pick(self, color):
        for actor in self._children:
            actor.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_children'):
            for child in self._children:
                child.unparent()
                child.destroy()
            self._children = list()

#-----------------------------------------------------------
class InfoMessage():
    def __init__(self, mid=None, mtype=None, mdate=None, mcontent=''):
        self.mid = mid
        self.mtype = mtype
        self.mdate = mdate
        self.mcontent = mcontent

#-----------------------------------------------------------
class IconManager(clutter.Actor, clutter.Container):
    __gtype_name__ = 'IconManager'

    def __init__(self, padding=10, spacing=5):
        import touchwizard
        clutter.Actor.__init__(self)
        self._children = list()
        self.padding = padding
        self.spacing = spacing
        self.icon_height = 48
        self.icon_padding = 8
        self.tooltip_displayed = None
    
    def on_tooltip_display(self, actor, displayed):
        if displayed:
            if self.tooltip_displayed is not None:
                self.tooltip_displayed.display_tooltip(False)
            self.tooltip_displayed = actor
    
    def add_icon(self, name, label='', status=None, icon_src=None, clickable=False, on_click_callback=None, tooltips=list()):
        icon = self.get_icon(dict(name=name))
        if icon is not None:
            return None
        icon = InfoIcon(name, label=label, status=status, icon_src=icon_src, clickable=clickable, on_click_callback=on_click_callback, tooltips=tooltips, icon_height=self.icon_height, padding=self.icon_padding)
        self._add(icon, index=0)
        return icon
    
    def display_icon_tooltip(self, params=dict):
        icon = self.get_icon(params)
        if icon is not None:
            if 'status' in params:
                icon.set_status(params['status'])
            if 'tooltips' in params:
                for tooltip in params['tooltips']:
                    if 'id' in tooltip:
                        icon.set_tooltip_line(tooltip['id'], tooltip.get('status', None), tooltip.get('text', None), tooltip.get('delete', False))
            icon.display_tooltip(True)
        return False
    
    def modify_icon(self, params=dict()):
        icon = self.get_icon(params)
        if icon is not None:
            if 'label' in params:
                icon.set_text(params['label'])
            if 'status' in params:
                icon.set_status(params['status'])
            if 'src' in params:
                icon.set_src(params['src'])
            if 'clickable' in params:
                icon.set_clickable(params['clickable'])
            if 'on_click_callback' in params:
                icon.set_on_click_callback(params['on_click_callback'])
            if 'tooltips' in params:
                for tooltip in params['tooltips']:
                    if 'id' in tooltip:
                        icon.set_tooltip_line(tooltip['id'], tooltip.get('status', None), tooltip.get('text', None), tooltip.get('delete', False))
        return False
    
    def remove_icon(self, params=dict()):
        icon = self.get_icon(params)
        if icon is not None:
            self._remove(icon)
        return False
    
    def get_icon(self, params):
        name = params.get('name', None)
        actor = params.get('actor', None)
        if actor is not None and actor in self._children:
            return actor
        elif actor is None and name is not None:
            for child in self._children:
                if child.name == name:
                    return child
        return None
    
    def _add(self, actor, index=-1):
        if actor in self._children:
            raise Exception("Actor %s is already a children of %s" % (actor, self))
        if index > -1:
            self._children.insert(index, actor)
        else:
            self._children.append(actor)
        actor.on_tooltip_display = self.on_tooltip_display
        actor.set_parent(self)
        self.queue_relayout()
    
    def _remove(self, actor):
        if actor in self._children:
            self._children.remove(actor)
            actor.unparent()
            self.queue_relayout()
        else:
            raise Exception("Actor %s is not a child of %s" % (actor, self))
    
    def do_get_preferred_width(self, for_height):
        if for_height != -1:
            for_height -= 2*self.padding
        preferred_width = 0
        for child in self._children:
            preferred_width += child.get_preferred_width(for_height)[1] + self.spacing
        if preferred_width > 0:
            preferred_width = preferred_width - self.spacing + 2*self.padding
        return preferred_width, preferred_width

    def do_get_preferred_height(self, for_width):
        # return preferred height as a constant in order to have an infobar with a constant height
        preferred_height = 2*self.padding + self.icon_height + 2*self.icon_padding
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        inner_height = main_height - 2*self.padding
        
        x = self.padding
        for child in self._children:
            child_box = clutter.ActorBox()
            child_box.x1 = x
            child_box.x2 = x + child.get_preferred_width(inner_height)[1]
            child_box.y1 = self.padding
            child_box.y2 = main_height - self.padding
            child.allocate(child_box, flags)
            x = child_box.x2 + self.spacing
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        for child in self._children:
            func(child, data)
        
    def do_paint(self):
        for actor in self._children:
            actor.paint()
    
    def do_pick(self, color):
        for actor in self._children:
            actor.paint()
    
    def do_destroy(self):
        self.unparent()
        if hasattr(self, '_children'):
            for child in self._children:
                child.unparent()
                child.destroy()
            self._children = list()
    

