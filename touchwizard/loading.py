import candies2
import touchwizard

class LoadingWidget(candies2.TextContainer):
    def __init__(self):
        candies2.TextContainer.__init__(self, touchwizard.loading_message)
        self.set_font_name('48')
        self.set_font_color(touchwizard.font_color)
        self.set_inner_color("#ffffff22")
        self.set_border_color("#ffffff22")
