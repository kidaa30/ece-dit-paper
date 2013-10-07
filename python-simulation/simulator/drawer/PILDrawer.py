from simulator.drawer.PictureDrawer import PictureDrawer

from PIL import Image as img
from PIL import ImageFont
from PIL import ImageDraw as draw

import random
import re


class PILDrawer(PictureDrawer):
    def __init__(self, simu, stop):
        super().__init__(simu, stop)

    def custom_init(self):
        self.colors = ["rgb(" + ",".join([str(random.randint(0, 255)) for i in range(3)]) + ")" for j in range(self.simu.m)]
        self.outImg = img.new("RGB", (self.width, self.height), "white")
        self.fontRoboto = ImageFont.truetype("res/Roboto-Medium.ttf", 9)
        self.outDraw = draw.Draw(self.outImg)

    def greyColor(self, color):
        colorRe = re.compile('\d+')
        rgb = colorRe.findall(color)
        assert len(rgb) == 3
        rgb = [int(s) for s in rgb]
        rgbGrey = [c // 2 for c in rgb]
        return "rgb(" + ",".join([str(c) for c in rgbGrey]) + ")"

    def drawArrow(self, x1, y1, x2, y2, color):
        self.drawLine(x1, y1, x2, y2, color=color, width=2)
        r = 2
        self.drawCircle(x2, y2, r, color)

    def black():
        return "black"

    def grey(self):
        return "gray"

    def drawLine(self, x1, y1, x2, y2, width=1, color=black()):
        self.outDraw.line([x1, y1, x2, y2], width=width, fill=color)

    def drawRectangle(self, x1, y1, x2, y2, fillColor, outlineColor):
        self.outDraw.rectangle([x1, y1, x2, y2], outline=outlineColor, fill=fillColor)

    def drawCircle(self, xC, yC, rad, color):
        self.outDraw.ellipse([xC - rad, yC - rad, xC + rad, yC + rad], outline="black", fill=color)
