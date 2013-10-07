class Drawer(object):
    """Abstract drawer class used by a Simulator to display results"""
    def __init__(self, simu, stop):
        """param:
        - Simu is the instance of Simulator which shall be drawn
        - stop is the maximal time which shall be simulated"""
        self.simu = simu
        self.stop = stop
        self.drawnDeadlineMissCount = 0

    def drawInstant(self, t):
        """Draw instant t in the simulation"""
        raise NotImplementedError("Drawer: attempted to call abstract method")

    def drawAbort(self, task, t):
        """Draw an abort of task at time t in the Abort/Restart model"""
        raise NotImplementedError("Drawer: attempted to call abstract method")

    def drawDeadlineMiss(self, t, task):
        """Draw a deadline miss for task at time t"""
        raise NotImplementedError("Drawer: attempted to call abstract method")

    def getDrawnDeadlineMissCount(self):
        """Return the number of deadline misses already processed"""
        raise NotImplementedError("Drawer: attempted to call abstract method")

    def terminate(self):
        """Called at the end of the simulation"""
        raise NotImplementedError("Drawer: attempted to call abstract method")


class EmptyDrawer(Drawer):
    """Will not draw anything. Use it when you don't need a Drawer"""
    def __init__(self, simu, stop):
        super().__init__(simu, stop)
        pass

    def drawInstant(self, t):
        pass

    def drawAbort(self):
        pass

    def drawDeadlineMiss(self, t, task):
        self.drawnDeadlineMissCount += 1

    def getDrawnDeadlineMissCount(self):
        return self.drawnDeadlineMissCount

    def drawArrivalsAndDeadlines(self):
        pass

    def terminate(self):
        pass

