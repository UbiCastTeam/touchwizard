# -*- coding: utf-8 -*-

import os
import clutter
import gobject
import easyevent
import candies2
import logging

logger = logging.getLogger('touchwizard')


class InfoIcon(candies2.ToolTipManager, easyevent.User):
    """
    Class InfoIcon is used for info bar icons.
    
    Used images files:
        - <touchwizard images path>/infobar/common/tooltip_texture.png
        - <touchwizard images path>/infobar/common/tooltip_pointer.png
        - <touchwizard images path>/infobar/common/status_<status>.png
        - <touchwizard images path>/infobar/common/status_<status>_small.png
        - <touchwizard images path>/infobar/<icon name>.png
    All images files are optionnal.
    """
    __gtype_name__ = 'InfoIcon'
    STATUSES = ['UNKNOWN', 'READY', 'DISABLED', 'INFO', 'ERROR', 'WARNING']
    
    def __init__(self, name, label='', status=None, icon_src=None, clickable=True, tooltip='', icon_height=48, padding=8):
        self.name = name
        self.label_text = label
        self.icon_src = icon_src
        self.status = None
        self.on_tooltip_display = None
        self.images_path = ''
        
        self.tooltip = candies2.OptionLine('tooltip', tooltip, padding=6)
        self.content = IconContent(self.name, self.label_text, icon_height=icon_height, padding=padding)
        candies2.ToolTipManager.__init__(self, tooltip_actor=self.tooltip, content_actor=self.content, h_direction='left', v_direction='bottom', clickable=clickable, long_click=False, tooltip_duration=3000, animation_duration=300, tooltip_x_padding=10, tooltip_y_padding=0)
        easyevent.User.__init__(self)
        
        # Apply skin
        self._apply_skin()
        
        self.set_status(self.STATUSES[0])
        if status is not None:
            self.set_status(status)
        
    """
        self._build_picture()
        
        self.timeline = clutter.Timeline(600)
        alpha = clutter.Alpha(self.timeline, clutter.EASE_OUT_ELASTIC)
        self.animation = clutter.BehaviourScale(1.1, 1.1, 1.0, 1.0, alpha=alpha)
        self.animation.apply(self.picture)
    
    def animate(self):
        self.timeline.start()
    """
    
    def _apply_skin(self):
        import touchwizard
        # Apply skin
        self.content.set_font_name(touchwizard.infobar_params['icon_font_name'])
        self.content.set_font_color(touchwizard.infobar_params['icon_font_color'])
        self.content.set_inner_color(touchwizard.infobar_params['icon_inner_color'])
        self.content.set_border_color(touchwizard.infobar_params['icon_border_color'])
        self.content.set_border_width(touchwizard.infobar_params['icon_border_width'])
        self.content.set_radius(touchwizard.infobar_params['icon_radius'])
        self.tooltip.set_font_name(touchwizard.infobar_params['tooltip_font_name'])
        self.tooltip.set_font_color(touchwizard.infobar_params['tooltip_font_color'])
        self.tooltip.set_inner_color(touchwizard.infobar_params['tooltip_inner_color'])
        self.tooltip.set_border_color(touchwizard.infobar_params['tooltip_border_color'])
        self.tooltip.set_border_width(touchwizard.infobar_params['tooltip_border_width'])
        self.tooltip.set_radius(touchwizard.infobar_params['tooltip_radius'])
        self.tooltip_x_padding = touchwizard.infobar_params['tooltip_x_padding']
        self.tooltip_y_padding = touchwizard.infobar_params['tooltip_y_padding']
        
        # Images
        self.images_path = touchwizard.images_path or ''
        #tooltip_texture
        tooltip_texture_src = os.path.join(self.images_path, 'infobar', 'common', 'tooltip_texture.png')
        if os.path.exists(tooltip_texture_src):
            tooltip_texture = clutter.cogl.texture_new_from_file(tooltip_texture_src)
            self.tooltip.set_texture(tooltip_texture)
        else:
            logger.error('in infobar icon: Image file for tooltip texture (%s) does not exist.', tooltip_texture_src)
        #tooltip_pointer
        tooltip_pointer_src = os.path.join(self.images_path, 'infobar', 'common', 'tooltip_pointer.png')
        if os.path.exists(tooltip_pointer_src):
            self.set_pointer_texture(tooltip_pointer_src)
        else:
            logger.error('in infobar icon: Image file for tooltip pointer (%s) does not exist.', tooltip_pointer_src)
        #icon image
        self.set_src(self.icon_src)
    
    def get_text(self):
        return self.content.get_text()
    
    def set_text(self, text):
        self.content.set_text(text)
    
    def set_tooltip_text(self, text):
        self.tooltip.set_text(text)
    
    def set_src(self, icon_src):
        self.icon_src = icon_src
        if self.icon_src is not None:
            used_src = self.icon_src
        else:
            used_src = os.path.join(self.images_path, 'infobar', '%s.png' %(self.name))
        if os.path.exists(used_src):
            self.content.set_icon(used_src)
        else:
            logger.error('in infobar icon: Icon file %s does not exist.', used_src)
        
    def set_status(self, status):
        new_status = status.upper()
        if self.status != new_status and new_status in self.STATUSES:
            self.status = status
            
            small_status_icon_src = os.path.join(self.images_path, 'infobar', 'common', 'status_%s_small.png' %(new_status.lower()))
            if os.path.exists(small_status_icon_src):
                self.content.set_status_icon(small_status_icon_src)
            else:
                logger.error('in infobar icon: Icon file %s does not exist.', small_status_icon_src)
            
            status_icon_src = os.path.join(self.images_path, 'infobar', 'common', 'status_%s.png' %(new_status.lower()))
            if os.path.exists(status_icon_src):
                self.tooltip.set_icon(status_icon_src)
            else:
                logger.error('in infobar icon: Icon file %s does not exist.', status_icon_src)
    
    def display_tooltip(self, boolean):
        if boolean and len(self.tooltip.get_text()) > 0:
            try:
                self.on_tooltip_display(self, True)
            except:
                pass
            self._show_tooltip()
        else:
            try:
                self.on_tooltip_display(self, False)
            except:
                pass
            self._hide_tooltip()
    
    def do_destroy(self):
        self.unregister_all_events()
        try:
            candies2.ToolTipManager.do_destroy(self)
        except:
            pass


class IconContent(candies2.OptionLine):
    __gtype_name__ = 'IconContent'
    
    def __init__(self, name, text, icon_height=48, icon_path=None, padding=8, spacing=8):
        candies2.OptionLine.__init__(self, name, text, icon_height=icon_height, icon_path=icon_path, padding=padding, spacing=spacing, texture=None)
        self.status_icon = clutter.Texture()
        self.status_icon.hide()
        self._add(self.status_icon)
        
    def set_status_icon(self, icon_src=None):
        if icon_src:
            self.status_icon.set_from_file(icon_src)
            self.status_icon.show()
        else:
            self.status_icon.hide()
    
    def do_get_preferred_width(self, for_height):
        if for_height != -1:
            for_height -= 2*self.padding
        if len(self.label.get_text()) > 0:
            preferred_width = self.icon_height + 2*self.padding + self.spacing
            preferred_width += self.label.get_preferred_width(for_height)[1]
        else:
            preferred_width = self.icon_height + 2*self.padding
        return preferred_width, preferred_width
    
    def do_get_preferred_height(self, for_width):
        preferred_height = self.icon_height + 2*self.padding
        return preferred_height, preferred_height
    
    def do_allocate(self, box, flags):
        main_width = box.x2 - box.x1
        main_height = box.y2 - box.y1
        
        # background
        background_box = clutter.ActorBox()
        background_box.x1 = 0
        background_box.y1 = 0
        background_box.x2 = main_width
        background_box.y2 = main_height
        self.background.allocate(background_box, flags)
        
        # icon
        icon_y_padding = int(float(main_height - self.icon_height)/2.0)
        icon_box = clutter.ActorBox()
        icon_box.x1 = self.padding
        icon_box.y1 = icon_y_padding
        icon_box.x2 = self.padding + self.icon_height
        icon_box.y2 = icon_box.y1 + self.icon_height
        self.icon.allocate(icon_box, flags)
        
        # status icon
        self.status_icon.allocate(icon_box, flags)
        
        # label
        label_box = clutter.ActorBox()
        label_box.x1 = icon_box.x2 + self.spacing
        label_box.y1 = self.padding
        label_box.x2 = main_width - self.padding
        label_box.y2 = main_height - self.padding
        self.label.allocate(label_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)


