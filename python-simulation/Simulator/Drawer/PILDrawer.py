from Simulator.Drawer.Drawer import Drawer

from Model import algorithms

from PIL import Image as img
from PIL import ImageFont
from PIL import ImageDraw as draw

import random
import re

class PILDrawer(Drawer):
    def __init__(self, simu, stop):
        super().__init__(simu, stop)
        self.instantWidth = 20
        self.widthMargin = 20
        self.taskHeight = 50
        self.heightMargin = 20
        self.width = stop * self.instantWidth + 2 * self.widthMargin
        self.height = len(simu.system.tasks) * self.taskHeight + 2 * self.heightMargin
        self.colors = ["rgb(" + ",".join([str(random.randint(0, 255)) for i in range(3)]) + ")" for j in range(self.simu.m)]

        self.outImg = img.new("RGB", (self.width, self.height), "white")
        self.fontRoboto = ImageFont.truetype("res/Roboto-Medium.ttf", 9)
        self.outDraw = draw.Draw(self.outImg)

        self.drawGrid(stop)
        self.drawArrivalsAndDeadlines()

    def getTaskNbr(self, task):
        taskNbr = None
        for i, eachTask in enumerate(self.simu.system.tasks):
            if eachTask is task:
                taskNbr = i
                break
        return taskNbr

    def drawGrid(self, stop):
        self.outDraw.line([self.widthMargin, self.height - self.heightMargin, self.widthMargin + self.instantWidth * stop, self.height - self.heightMargin], fill="black")
        # - horizontal lines to separate tasks
        for i, task in enumerate(self.simu.system.tasks):
            self.outDraw.line([self.widthMargin, self.height - self.heightMargin - (i + 1) * self.taskHeight, self.widthMargin + self.instantWidth * stop, self.height - self.heightMargin - (i + 1) * self.taskHeight], fill="black")
        # - vertical lines to separate instants
        for i in range(stop):
            x = self.widthMargin + i * self.instantWidth
            y = self.height - self.heightMargin
            self.outDraw.line([x, self.heightMargin, x, y], fill="gray")
            # timeline markers
            if i % 5 == 0:
                self.outDraw.text((x, y), str(i), font=self.fontRoboto, fill="black")
        # special timeline markers - Omax + k H
        H = self.simu.system.hyperPeriod()
        y = self.height - self.heightMargin
        specialDict = {'omax': self.simu.system.omax(), 'fpdit': algorithms.findFirstDIT(self.simu.system)}
        for specialName, specialTime in list(specialDict.items()):
            i = 0
            while specialTime and specialTime + i * H < stop:
                x = self.widthMargin + (specialTime + i * H) * self.instantWidth
                self.outDraw.line([x, self.heightMargin, x, y], fill="black")
                self.outDraw.text((x, y + 10), specialName + " + " + str(i) + " H", font=self.fontRoboto, fill="black")
                i += 1

    def drawDeadlineMiss(self, t, task):
        taskNbr = self.getTaskNbr(task)
        x = self.widthMargin + t * self.instantWidth
        y1 = self.height - self.heightMargin - (taskNbr + 1) * self.taskHeight
        y2 = self.height - self.heightMargin - taskNbr * self.taskHeight
        self.outDraw.line([x, y1, x, y2], fill="black", width=5)
        self.drawnDeadlineMissCount += 1

    def getDrawnDeadlineMissCount(self):
        return self.drawnDeadlineMissCount

    def drawOneExecutionUnit(self, taskNbr, CPUnbr, t, preemp):
        color = self.colors[CPUnbr]
        if preemp:
            color = greyColor(color)

        x1 = self.widthMargin + t * self.instantWidth
        y1 = self.height - self.heightMargin - (taskNbr + 1) * self.taskHeight
        x2 = self.widthMargin + (t + 1) * self.instantWidth
        y2 = self.height - self.heightMargin - taskNbr * self.taskHeight
        self.outDraw.rectangle([x1, y1, x2, y2], outline="black", fill=color)

    def drawAbort(self, task, t):
        taskNbr = self.getTaskNbr(task)
        assert taskNbr is not None, "drawAbort: task " + str(task) + " was not found in " + str(self.simu.system)
        x1 = self.widthMargin + t * self.instantWidth
        y1 = self.height - self.heightMargin - taskNbr * self.taskHeight - self.taskHeight // 2
        r = 3
        self.outDraw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], outline="black", fill="red")

    def drawInstant(self, t):
        for cpuNbr, cpu in enumerate(self.simu.CPUs):
            if cpu.job:
                taskNbr = self.getTaskNbr(cpu.job.task)
                if cpu in self.simu.preemptedCPUs:
                    self.drawOneExecutionUnit(taskNbr, cpuNbr, t, preemp=True)
                else:
                    self.drawOneExecutionUnit(taskNbr, cpuNbr, t, preemp=False)

    def terminate(self):
        self.drawArrivalsAndDeadlines()

    def drawArrivalsAndDeadlines(self):
        for taskNbr, task in enumerate(self.simu.system.tasks):
            for t in range(task.O, self.simu.stop + 1, task.T):
                x1 = self.widthMargin + t * self.instantWidth
                y1 = self.height - self.heightMargin - taskNbr * self.taskHeight
                # arrivals
                drawArrow(self.outDraw, x1, y1 - (self.taskHeight // 2), x1, y1 - self.taskHeight, "blue")
                # deadlines
                t += task.D
                x2 = self.widthMargin + t * self.instantWidth
                drawArrow(self.outDraw, x2, y1 - (self.taskHeight) // 2, x2, y1, "red")


def greyColor(color):
    colorRe = re.compile('\d+')
    rgb = colorRe.findall(color)
    assert len(rgb) == 3
    rgb = [int(s) for s in rgb]
    rgbGrey = [c // 2 for c in rgb]
    return "rgb(" + ",".join([str(c) for c in rgbGrey]) + ")"


def drawArrow(drawer, x1, y1, x2, y2, color):
    drawer.line((x1, y1, x2, y2), fill=color, width=2)
    r = 2
    drawer.ellipse((x2 - r, y2 - r, x2 + r, y2 + r), fill=color)
