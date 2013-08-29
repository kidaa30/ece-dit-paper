class Job(object):
    def __init__(self, task, arrival):
        self.task = task
        self.arrival = arrival
        self.deadline = arrival + task.D
        self.computation = 0
        self.priority = None  # maintained by the Scheduler Class
        self.preempted = False

    def isFinished(self):
        assert 0 <= self.computation <= self.task.C, str(self)
        return self.computation == self.task.C

    def computationLeft(self):
        return self.task.C - self.computation

    def __lt__(self, other):
        return other is not None and (self.priority, id(self.task)) < (other.priority, id(other.task))

    def alpha(self):
        return self.task.alpha

    def __repr__(self):
        return "(" + ", ".join([str(self.task), str(self.arrival), str(self.deadline), str(self.computation)]) + ")"
