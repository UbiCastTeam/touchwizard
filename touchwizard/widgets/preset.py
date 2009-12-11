#!/ur/bin/env python
# -*- coding: utf-8 -*-

''' 
preset class
author : flavie
date : dec 4 2009
version : none
'''
import sys
import operator
import gobject
import clutter
import candies2
import easyevent

class Preset(clutter.Actor, clutter.Container, easyevent.User):
    '''
    Preset class
    '''
    __gtype_name__ = 'Preset'
    
    def __init__(self,label,img,name):
        clutter.Actor.__init__(self)
        easyevent.User.__init__(self)
        self.name=name
        self.preset_image = img
        self.preset_image.set_parent(self)
        self.register = clutter.Texture('/images/save.png') 
        self.register.set_parent(self)
        self.register.set_reactive(True)
        self.register.connect('button-press-event', self.on_button_register_press)
        self.preset_name = candies2.ClassicButton(label)
        self.preset_name.set_parent(self)
        self.preset_name.set_reactive(True)
        self.preset_name.connect('button-press-event', self.on_preset_name_press) 
        self.preset_name.connect('button-release-event',self.on_preset_name_release)          
        self.register_event('preset_image')
        self.border=clutter.Rectangle()
    
    def on_button_register_press(self, source, event) :
        self.launch_event('save_preset',self.name)
    
    def evt_preset_image(self, event):
        pass
    
    def on_preset_name_press(self, source, event) :
        self.preset_name.rect.set_color('Gray')
                
    def on_preset_name_release(self, source, event):
        self.preset_name.rect.set_color('LightGray')
                       
    def do_allocate(self, box, flags):
        box_width = box.x2 - box.x1
        box_height = box.y2 - box.y1
        
        label_box=clutter.ActorBox()
        label_box.x1=0
        label_box.y1=0
        label_box.x2=box_width
        label_box.y2=box_height/8
        self.preset_name.allocate(label_box,flags)
        
        preset_image_box=clutter.ActorBox()
        preset_image_box.x1=0
        preset_image_box.y1=3*box_height/12
        preset_image_box.x2=3*box_width/4
        preset_image_box.y2=box_height
        self.preset_image.allocate(preset_image_box,flags)
        
        register_box=clutter.ActorBox()
        register_box.x1=13*box_width/16
        register_box.y1=box_height/2
        register_box.x2=box_width
        register_box.y2=3*box_height/4
        self.register.allocate(register_box,flags)
        clutter.Actor.do_allocate(self, box, flags)
    
    def do_foreach(self, func, data=None):
        children = (self.preset_name,self.preset_image,self.register)
        for child in children :
            func(child, data)
    
    def do_paint(self):
        children = (self.preset_name,self.preset_image,self.register)
        for child in children :
            child.paint()

    def do_pick(self, color):
        children = (self.preset_name,self.preset_image,self.register)
        for child in children :
            child.paint()

if __name__ == '__main__':

    stage = clutter.Stage()
    stage.connect('destroy',clutter.main_quit)
    
    label_preset_name1= "ceci n\'est pas un nom de preset"
    image1 = clutter.Texture( 'preset1.jpg') 
    preset_box1 = Preset(label_preset_name1,image1,'preset1')
    preset_box1.set_size(240,180)
    preset_box1.set_position(20,50)
    stage.add(preset_box1)

    label_preset_name2= "preset 2"
    image2 = clutter.Texture( 'preset2.jpg') 
    preset_box2 = Preset(label_preset_name2,image2,'preset2')
    preset_box2.set_size(160,120)
    preset_box2.set_position(230,50)
    stage.add(preset_box2)

    stage.show()
    
    clutter.main() 
