import Scheduler


class PALLF(Scheduler.SchedulerDP):
    def __init__(self, tau):
        super(PALLF, self).__init__(tau)
        self.prioOffset = max([task.alpha for task in tau.tasks]) + 1

    def getLaxity(self, job, simu):
        compLeft = job.task.C - job.computation
        lax = job.deadline - (simu.t + compLeft)
        return max(0, lax)

    def earliestPreempArrival(self, job, simu):
        # return earliest time at which job will be preempted if it is chosen now
        t = simu.t
        lax = self.getLaxity(job, simu)
        jobP = 1.0/(self.prioOffset + lax - job.alpha())
        finishTime = self.finishTime(job, simu)
        # test against priority of next arrival of each task
        candidate = None
        for task in simu.system.tasks:
            if t < task.O:
                nextArrival = task.O
            else:
                nextArrival = (t - task.O) + (task.T - (t - task.O) % task.T) + task.O
            prio = 1.0/(self.prioOffset + task.D - task.C)  # laxity
            if prio >= jobP and nextArrival < finishTime and (candidate is None or nextArrival < candidate):
                candidate = nextArrival
        return candidate

    def priority(self, job, simu):
        lax = self.getLaxity(job, simu)
        if self.isJobExecuting(job, simu):
            return 1.0/(self.prioOffset + lax - job.alpha())
        epa = self.earliestPreempArrival(job, simu)
        if epa and epa - simu.t <= job.alpha():  # execution would cost more than idling
            return -1 * float("inf")
        else:
            return 1.0/(self.prioOffset + lax)
