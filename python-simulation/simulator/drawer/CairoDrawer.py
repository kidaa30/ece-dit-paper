from simulator.drawer.Drawer import PictureDrawer

import cairo

import math


class CairoDrawer(PictureDrawer):
    def __init__(self, simu, stop):
        super().__init__(simu, stop)

    def custom_init(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        self.ctx = cairo.Context(self.surface)

    def black():
        return (1, 1, 1)

    def grey(self):
        return (0.6, 0.6, 0.6)

    def drawLine(self, x1, y1, x2, y2, width=1, color=black()):
        self.ctx.set_source_rgb(color)
        self.ctx.set_line_width(width)
        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)

    def greyColor(self, color):
        return tuple((c // 2 for c in color))

    def drawRectangle(self, x1, y1, x2, y2, fillColor, outlineColor):
        self.ctx.set_source_rgb(outlineColor)
        width = x2 - y2
        height = y2 - y1
        self.ctx.rectangle(x1, y1, width, height)
        self.ctx.set_source_rgb(fillColor)
        self.ctx.fill()

    def drawCircle(self, xC, yC, rad, color):
        self.ctx.set_source_rgb(color)
        self.ctx.arc(xC, yC, rad, 0, 2 * math.pi)

    def drawArrow(self, x1, y1, x2, y2, color):
        self.drawLine(x1, y1, x2, y2, width=2, color=color)
        r = 2
        self.drawCircle(x2, y2, r, color)
