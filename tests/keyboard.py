#!/usr/bin/env python
# -*- coding: utf-8 -*

import touchwizard
import easyevent
import clutter
import gobject
import candies2
import common

class KeyboardPanel(candies2.Keyboard, easyevent.User):
    
    def __init__(self):
        candies2.Keyboard.__init__(self, 'fr_maj', 'Sans 20')
        easyevent.User.__init__(self)
        self.connect('notify::visible', self.on_show)
        self.connect('keyboard', self.on_keyboard_input)
        self.text=''
        self.register_event('icon_langues_actioned')
        self.register_event('icon_next_actioned')
        self.register_event('icon_delete_title_actioned')
        self.register_event('icon_left_actioned')
        self.register_event('icon_right_actioned')
        self.register_event('info_bar_cursor_position')
        self.cursor_position = 0
                
        self.session = dict()
        self.register_event('session_reply')
        self.launch_event('request_session')
    
    def evt_info_bar_cursor_position(self,event):
        self.cursor_position=event.content
    
    def evt_session_reply(self, event):
        self.unregister_event('session_reply')
        self.session = event.content
    
    def evt_icon_previous_actioned(self,event):
        self.launch_event('info_message', '')
        self.unregister_event('icon_previous_actioned')
        self.launch_event('set_infobar_editable',False)
     
    def evt_icon_left_actioned(self,event):
        self.launch_event('info_bar_get_cursor_position')
        self.launch_event('info_bar_left')
    
    def evt_icon_right_actioned(self,event): 
        self.launch_event('info_bar_get_cursor_position')
        self.launch_event('info_bar_right')
        
    def evt_icon_delete_title_actioned(self,event):
        self.text=''
        self.launch_event('info_message', self.text)
        if self.map_name=='fr_min':
            self.load_profile('fr_maj')
        elif self.map_name=='en_min':
            self.load_profile('en_maj')
        
    def evt_icon_next_actioned(self,event):
        self.unregister_event('icon_previous_actioned')
        self.launch_event('info_message', '')
        self.launch_event('keyboard_done', self.text)
        gobject.timeout_add(200, self.launch_event, 'previous_page')
        self.launch_event('set_infobar_editable',False)
    
    def evt_icon_langues_actioned(self,event):
        if self.map_name =='fr_maj':    
            self.load_profile('en_maj')
        elif self.map_name =='fr_min':
            self.load_profile('en_min')
        elif self.map_name =='en_maj':
            self.load_profile('fr_maj')
        elif self.map_name =='en_min':
            self.load_profile('fr_min')
        elif self.map_name =='caract_fr':
            self.load_profile('caract_en')
        elif self.map_name =='caract_en':
            self.load_profile('caract_fr')
    
    def on_show(self, panel, event):
        if self.props.visible:
            self.launch_event('set_infobar_editable',True)
            self.text = self.session.pop('initial_keyboard_text', '')
            if len(self.text)>1:
                if self.map_name == 'fr_maj':
                    self.load_profile('fr_min')
                elif self.map_name == 'en_maj':
                    self.load_profile('en_min')
                elif self.map_name=='caract_fr':
                    self.load_profile('fr_min')
                elif self.map_name=='caract_en':
                    self.load_profile('en_min')
            else:
                if self.map_name == 'fr_min':
                    self.load_profile('fr_maj')
                elif self.map_name == 'en_min':
                    self.load_profile('en_maj')
                elif self.map_name=='caract_fr':
                    self.load_profile('fr_maj')
                elif self.map_name=='caract_en':
                    self.load_profile('en_maj')
            self.register_event('icon_previous_actioned') 
            self.launch_event('info_message', self.text)
    
    def on_keyboard_input(self,source,key):
        if key == 'suppr':
            self.text=self.text[:-1]
        elif key == 'enter':
            self.launch_event('keyboard_output',self.text)
            self.text=' '
        else :
            if len(self.text)>=1:
                if self.text[-1]=='.' and key == ' ':
                    if self.map_name == 'fr_min':
                        self.load_profile('fr_maj')
                    elif self.map_name == 'en_min':
                        self.load_profile('en_maj')
            if len(self.text)>=2:
                if self.text[-2]+self.text[-1]=='. ':
                    if self.map_name == 'fr_maj':
                        self.load_profile('fr_min')
                    elif self.map_name == 'en_maj':
                        self.load_profile('en_min')
            self.launch_event('info_bar_get_cursor_position')
            if self.cursor_position == -1 :
                self.text=self.text + key
            else :
                text_before_cursor=self.text[:self.cursor_position]
                text_after_cursor=self.text[self.cursor_position:len(self.text)]
                text_before_cursor+=key
                self.text=text_before_cursor+text_after_cursor
                self.launch_event('info_bar_right')
        if len(self.text)==1:
            if self.map_name == 'fr_maj':
                self.load_profile('fr_min')
            elif self.map_name == 'en_maj':
                self.load_profile('en_min')
        if len(self.text)==0:
            if self.map_name == 'fr_min':
                self.load_profile('fr_maj')
            elif self.map_name == 'en_min':
                self.load_profile('en_maj')
        self.launch_event('info_message', self.text)

class Page(touchwizard.Page):
    reuse = True
    title = 'Keyboard'
    name = 'keyboard'
    panel = KeyboardPanel
    #print KeyboardPanel.map_name
    icons = (
        touchwizard.Icon('langues', _('English/Français')),
        touchwizard.Icon('left',_('left')),
        touchwizard.Icon('right',_('right')),
        touchwizard.Icon('delete_title',_('delete text')),
        touchwizard.Icon('next', _('OK'))
            )

if __name__ == '__main__':
    touchwizard.quick_launch(Page)
