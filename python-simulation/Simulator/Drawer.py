import Image as img
import ImageDraw as draw
import random


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
		self.outDraw = draw.Draw(self.outImg)

		self.outDraw.line([self.widthMargin, self.height - self.heightMargin, self.widthMargin + self.instantWidth * stop, self.height - self.heightMargin], fill="black", width=3)
		# grid
		# - horizontal lines to separate tasks
		for i, task in enumerate(simu.system.tasks):
			self.outDraw.line([self.widthMargin, self.height - self.heightMargin - (i + 1) * self.taskHeight, self.widthMargin + self.instantWidth * stop, self.height - self.heightMargin - (i + 1) * self.taskHeight], fill=128)
		# - vertical lines to separate instants
		for i in range(stop):
			self.outDraw.line([self.widthMargin + i * self.instantWidth, self.heightMargin, self.widthMargin + i * self.instantWidth, self.height - self.heightMargin], fill=64)

	def drawOneExecutionUnit(self, taskNbr, CPUnbr, t, preemp):
		if preemp:
			outlineColor = "red"
		else:
			outlineColor = "gray"
		x1 = self.widthMargin + t * self.instantWidth
		y1 = self.height - self.heightMargin - (taskNbr + 1) * self.taskHeight
		x2 = self.widthMargin + (t + 1) * self.instantWidth
		y2 = self.height - self.heightMargin - taskNbr * self.taskHeight
		self.outDraw.rectangle([x1, y1, x2, y2], outline=outlineColor, fill=self.colors[CPUnbr])

	def drawInstant(self, t):
		for i, task in enumerate(self.simu.system.tasks):
			for j, cpu in enumerate(self.simu.CPUs):
				if cpu.job and cpu.job.task is task:
					if cpu in self.simu.preemptedCPUs:
						self.drawOneExecutionUnit(i, j, t, preemp=True)
					else:
						self.drawOneExecutionUnit(i, j, t, preemp=False)
