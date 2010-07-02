from version import VERSION as __revision__
from canvas import Canvas, quick_launch
from session import Session
from infobar import InfoBar
from iconbar import IconBar
from page import Page
from icon import Icon, IconRef

page_path = None
images_path = 'images'
canvas_bg = None
iconbar_bg = None
scaling_ratio = 1.0
tolerant_to_page_import_error = True

infobar_skin = dict(
    backgrounds_width = 20,
    
    text_font_name = '20',
    text_font_color = '#ffffffff',
    
    icon_font_name = '16',
    icon_font_color = '#ffffffff',
    icon_inner_color = '#888888ff',
    icon_border_color = '#aaaaaaff',
    icon_border_width = 1,
    icon_radius = 5,
    
    tooltip_font_name = '16',
    tooltip_font_color = '#ffffffff',
    tooltip_inner_color = '#00000000',
    tooltip_border_color = '#000000aa',
    tooltip_border_width = 1,
    tooltip_radius = 5,
    tooltip_x_padding = 10,
    tooltip_y_padding = 0,
    tooltip_pointer = None,
)

canvas_width = 1280
canvas_height = 1024

loading_message = 'Loading ...'
font_color = 'Black'
