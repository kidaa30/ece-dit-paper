import Image as img
import ImageFont
import ImageDraw as draw

import random
import re

class Drawer(object):
	def __init__(self, simu, stop):
		self.simu = simu
		self.instantWidth = 20
		self.widthMargin = 20
		self.taskHeight = 50
		self.heightMargin = 20
		self.width = stop * self.instantWidth + 2 * self.widthMargin
		self.height = len(simu.system.tasks) * self.taskHeight + 2 * self.heightMargin
		self.colors = ["rgb(" + ",".join([str(random.randint(0, 255)) for i in range(3)]) + ")" for j in range(self.simu.m)] + ["black"]  # black: preemption

		self.outImg = img.new("RGB", (self.width, self.height), "white")
		self.fontRoboto = ImageFont.truetype("Simulator/Roboto-Thin.ttf", 9)
		self.outDraw = draw.Draw(self.outImg)

		self.outDraw.line([self.widthMargin, self.height - self.heightMargin, self.widthMargin + self.instantWidth * stop, self.height - self.heightMargin], fill="black")
		# grid
		# - horizontal lines to separate tasks
		for i, task in enumerate(simu.system.tasks):
			self.outDraw.line([self.widthMargin, self.height - self.heightMargin - (i + 1) * self.taskHeight, self.widthMargin + self.instantWidth * stop, self.height - self.heightMargin - (i + 1) * self.taskHeight], fill=128)
		# - vertical lines to separate instants
		for i in range(stop):
			x = self.widthMargin + i * self.instantWidth
			y = self.height - self.heightMargin
			self.outDraw.line([x, self.heightMargin, x, y], fill=64)
			if i % 5 == 0:
				self.outDraw.text((x, y), str(i), font=self.fontRoboto, fill="black")

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
		taskNbr = None
		for i, eachTask in enumerate(self.simu.system.tasks):
			if eachTask is task:
				taskNbr = i
		assert taskNbr is not None, "drawAbort: task " + str(task) + " was not found in " + str(self.simu.system)
		x1 = self.widthMargin + t * self.instantWidth
		y1 = self.height - self.heightMargin - taskNbr * self.taskHeight - self.taskHeight/2
		r = 3
		self.outDraw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], outline="black", fill="red")

	def drawInstant(self, t):
		for cpuNbr, cpu in enumerate(self.simu.CPUs):
			if cpu.job:
				taskNbr = None
				for i, task in enumerate(self.simu.system.tasks):
					if cpu.job.task is task:
						taskNbr = i
				if cpu in self.simu.preemptedCPUs:
					self.drawOneExecutionUnit(taskNbr, cpuNbr, t, preemp=True)
				else:
					self.drawOneExecutionUnit(taskNbr, cpuNbr, t, preemp=False)

	def drawArrivalsAndDeadlines(self):
		for taskNbr, task in enumerate(self.simu.system.tasks):
			for t in range(task.O, self.simu.stop + 1, task.T):
				x1 = self.widthMargin + t * self.instantWidth
				y1 = self.height - self.heightMargin - taskNbr * self.taskHeight
				# arrivals
				drawArrow(self.outDraw, x1, y1 - (self.taskHeight / 2), x1, y1 - self.taskHeight, "blue")
				# deadlines
				t += task.D
				x2 = self.widthMargin + t * self.instantWidth
				drawArrow(self.outDraw, x2, y1 - (self.taskHeight)/2, x2, y1 , "red")


def greyColor(color):
	colorRe = re.compile('\d+')
	rgb = colorRe.findall(color)
	assert len(rgb) == 3
	rgb = map(lambda s: int(s), rgb)
	rgb = [c/2 for c in rgb]
	return "rgb(" + ",".join([str(c) for c in rgb]) + ")"


def drawArrow(drawer, x1, y1, x2, y2, color):
	drawer.line((x1, y1, x2, y2), fill=color, width=2)
	r = 2
	drawer.ellipse((x2 - r, y2 - r, x2 + r, y2 + r), fill=color)
