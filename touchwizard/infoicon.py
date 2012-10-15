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
    
    def __init__(self, name, label='', status=None, icon_src=None, icon_size=(48, 48), custom_actor=None, clickable=True, on_click_callback=None, tooltips=list(), padding=8):
        self.name = name
        self.label_text = label
        self.icon_src = icon_src
        self.status = None
        self.on_tooltip_display = None
        self.on_click_callback = on_click_callback
        self.images_path = ''
        
        self.tooltip = candies2.VBox(padding=6, pick_enabled=False)
        self.tooltip.connect('button-release-event', self._on_tooltip_click)
        self.tooltip.set_reactive(True)
        self.tooltip_lines = list()
        self.content = IconContent(self.name, self.label_text, icon_size=icon_size, custom_actor=custom_actor, padding=padding)
        self.content.connect('button-release-event', self._on_icon_click)
        candies2.ToolTipManager.__init__(self, tooltip_actor=self.tooltip, content_actor=self.content, h_direction='left', v_direction='bottom', clickable=clickable, long_click=False, tooltip_duration=3000, animation_duration=300, tooltip_x_padding=10, tooltip_y_padding=0)
        easyevent.User.__init__(self)
        
        # Apply skin
        self._apply_skin()
        
        if status is not None:
            self.set_status(status)
        else:
            self.set_status('unknown')
        
        # Add initial tooltips
        for tooltip in tooltips:
            if 'id' in tooltip:
                self.set_tooltip_line(tooltip['id'], tooltip.get('status', None), tooltip.get('text', None), tooltip.get('delete', False))
        
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
        tooltip_bg = candies2.RoundRectangle()
        tooltip_bg.set_inner_color(touchwizard.infobar_params['tooltip_inner_color'])
        tooltip_bg.set_border_color(touchwizard.infobar_params['tooltip_border_color'])
        tooltip_bg.set_border_width(touchwizard.infobar_params['tooltip_border_width'])
        tooltip_bg.set_radius(touchwizard.infobar_params['tooltip_radius'])
        self.tooltip.set_background(tooltip_bg)
        self.tooltip_font_name = touchwizard.infobar_params['tooltip_font_name']
        self.tooltip_font_color = touchwizard.infobar_params['tooltip_font_color']
        self.tooltip_x_padding = touchwizard.infobar_params['tooltip_x_padding']
        self.tooltip_y_padding = touchwizard.infobar_params['tooltip_y_padding']
        
        # Images
        self.images_path = touchwizard.images_path or ''
        #tooltip_texture
        tooltip_texture_src = os.path.join(self.images_path, 'infobar', 'common', 'tooltip_texture.png')
        if os.path.exists(tooltip_texture_src):
            tooltip_texture = clutter.cogl.texture_new_from_file(tooltip_texture_src)
            tooltip_bg.set_texture(tooltip_texture)
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
        if self.status != status:
            self.status = status
            small_status_icon_src = os.path.join(self.images_path, 'infobar', 'common', 'status_%s_small.png' %status)
            if os.path.exists(small_status_icon_src):
                self.content.set_status_icon(small_status_icon_src)
            else:
                logger.error('in infobar icon: Icon file %s does not exist.', small_status_icon_src)
    
    def set_tooltip_line(self, line_id, status=None, text=None, delete=False):
        line = None
        for tooltip_line in self.tooltip_lines:
            if tooltip_line.line_id == line_id:
                line = tooltip_line
                if delete:
                    self.tooltip.remove_element('line_%s' %line_id)
                    self.tooltip_lines.remove(line)
                break
        if line == None:
            if not delete:
                if text == None:
                    text = ''
                line = ToolTipLine(line_id, status, text, images_path=self.images_path)
                line.set_font_name(self.tooltip_font_name)
                line.set_font_color(self.tooltip_font_color)
                self.tooltip.add_element(line, 'line_%s' %line_id, expand=True)
                self.tooltip_lines.append(line)
        else:
            if text is not None:
                line.set_text(text)
            if status is not None:
                line.set_status(status)
    
    def set_on_click_callback(self, callback):
        self.on_click_callback = callback
    
    def _on_icon_click(self, source=None, event=None):
        if self.on_click_callback is not None:
            self.on_click_callback(self.get_tooltip_displayed())
    
    def _on_tooltip_click(self, source=None, event=None):
        self.display_tooltip(False)
    
    def display_tooltip(self, boolean):
        if boolean and len(self.tooltip_lines) > 0:
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

class ToolTipLine(candies2.OptionLine):
    __gtype_name__ = 'ToolTipLine'
    
    def __init__(self, line_id, status, text, images_path):
        candies2.OptionLine.__init__(self, line_id, text, padding=6, rounded=False)
        self.images_path = images_path
        self.line_id = line_id
        self.set_inner_color('#00000000')
        self.set_line_alignment('left')
        self.set_status(status)
    
    def set_status(self, status):
        self.status = status
        if self.status:
            status_icon_src = os.path.join(self.images_path, 'infobar', 'common', 'status_%s.png' %status)
            if os.path.exists(status_icon_src):
                self.set_icon(status_icon_src)
            else:
                logger.error('in infobar icon: Icon file %s does not exist.', status_icon_src)


class IconContent(candies2.BaseContainer):
    __gtype_name__ = 'IconContent'
    
    def __init__(self, name, text, icon_size=(48, 48), custom_actor=None, icon_path=None, padding=8, spacing=8, texture=None):
        candies2.BaseContainer.__init__(self)
        self._padding = candies2.Padding(padding)
        self._spacing = candies2.Spacing(spacing)
        self.name = name
        
        self.font = '14'
        self.font_color = 'Black'
        self.default_color = 'LightGray'
        self.default_border_color = 'Gray'
        
        # background
        self.background = candies2.RoundRectangle(texture=texture)
        self.background.set_color(self.default_color)
        self.background.set_border_color(self.default_border_color)
        self.background.set_border_width(3)
        self.background.set_radius(10)
        self._add(self.background)
        # icon
        self.icon_size = icon_size
        self.icon_path = icon_path
        self.icon = clutter.Texture()
        if icon_path:
            self.icon.set_from_file(icon_path)
        else:
            self.icon.hide()
        self._add(self.icon)
        # status icon
        self.status_icon = clutter.Texture()
        self.status_icon.hide()
        self._add(self.status_icon)
        # custom_actor
        self.custom_actor = custom_actor
        if custom_actor:
            self._add(custom_actor)
            self.icon.hide()
        # label
        self.label = candies2.TextContainer(text, padding=0, rounded=False)
        self.label.set_font_color(self.font_color)
        self.label.set_font_name(self.font)
        self.label.set_inner_color('#00000000')
        self.label.set_border_color('#00000000')
        self._add(self.label)
    
    def get_text(self):
        return self.label.get_text()
    
    def set_texture(self, texture):
        self.background.set_texture(texture)
    
    def set_line_wrap(self, boolean):
        self.label.set_line_wrap(boolean)
            
    def set_line_alignment(self, alignment):
        self.label.set_line_alignment(alignment)
    
    def set_justify(self, boolean):
        self.label.set_justify(boolean)
    
    def set_text(self, text):
        self.label.set_text(text)
    
    def set_name(self, text):
        self.name = text
    
    def set_hname(self, text):
        self.label.set_text(text)
    
    def has_icon(self):
        if self.icon_path is not None:
            return True
        else:
            return False
    
    def set_icon(self, new_icon_path=None):
        self.icon_path = new_icon_path
        if new_icon_path:
            self.icon.set_from_file(new_icon_path)
            self.icon.show()
        else:
            self.icon.hide()
    
    def set_status_icon(self, icon_src=None):
        if icon_src:
            self.status_icon.set_from_file(icon_src)
            self.status_icon.show()
        else:
            self.status_icon.hide()
    
    def set_font_color(self, color):
        self.label.set_font_color(color)
    
    def set_font_name(self, font_name):
        self.label.set_font_name(font_name)
    
    def set_inner_color(self, color):
        self.background.set_color(color)
    
    def set_border_color(self, color):
        self.background.set_border_color(color)
    
    def set_radius(self, radius):
        self.background.set_radius(radius)
    
    def set_border_width(self, width):
        self.background.set_border_width(width)
    
    def do_get_preferred_width(self, for_height):
        if for_height != -1:
            for_height -= 2*self._padding.y
        if len(self.label.get_text()) > 0:
            preferred_width = self.icon_size[0] + 2*self._padding.x + self._spacing.x
            preferred_width += self.label.get_preferred_width(for_height)[1]
        else:
            preferred_width = self.icon_size[0] + 2*self._padding.x
        return preferred_width, preferred_width
    
    def do_get_preferred_height(self, for_width):
        preferred_height = self.icon_size[1] + 2*self._padding.y
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
        icon_y_padding = int(float(main_height - self.icon_size[1])/2.0)
        icon_box = clutter.ActorBox()
        icon_box.x1 = self._padding.x
        icon_box.y1 = icon_y_padding
        icon_box.x2 = self._padding.x + self.icon_size[0]
        icon_box.y2 = icon_box.y1 + self.icon_size[1]
        if self.custom_actor is not None:
            self.custom_actor.allocate(icon_box, flags)
        else:
            self.icon.allocate(icon_box, flags)
        
        # status icon
        status_icon_width, status_icon_height =  self.status_icon.get_size()
        status_icon_ratio = status_icon_width / status_icon_height
        status_box = clutter.ActorBox()
        status_box.x2 = self._padding.x + self.icon_size[0]
        status_box.y2 = icon_box.y1 + self.icon_size[1]
        status_box.y1 = icon_y_padding
        status_width = (status_box.y2-status_box.y1) * status_icon_ratio
        status_box.x1 = status_box.x2 - status_width
        self.status_icon.allocate(status_box, flags)
        
        # label
        label_box = clutter.ActorBox()
        label_box.x1 = icon_box.x2 + self._spacing.x
        label_box.y1 = self._padding.y
        label_box.x2 = main_width - self._padding.x
        label_box.y2 = main_height - self._padding.y
        self.label.allocate(label_box, flags)
        
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_pick(self, color):
        clutter.Actor.do_pick(self, color)


