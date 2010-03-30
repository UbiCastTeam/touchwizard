import sys
import gobject
import clutter
import candies2
import easyevent
import touchwizard
from widgets import EditableButton

class TestPanel(candies2.Box, easyevent.User):
    def __init__(self):
        candies2.Box.__init__(self)
        easyevent.User.__init__(self)
        button = EditableButton('test')
        #button.connect('notify::text', self.on_text_changed)
        self.add_element(button, 'button')
        self.connect('notify::visible', self.on_show)
    
    def on_show(self, panel, event):
        if self.props.visible:
            self.launch_event('info_message', 'WELCOME')
    
    #def on_text_changed(self, button, event):
    #    self.launch_event('info_message', 'HELLO WORLD')

class Page(touchwizard.Page):
    title = 'testPanel'
    name = 'testPanel'
    panel = TestPanel
    icons = (
    )
                
if __name__=='__main__':

    touchwizard.quick_launch(Page)
