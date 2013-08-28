import Scheduler


class ChooseKeepEDF(Scheduler.SchedulerDP):
    def __init__(self, tau):
        super(ChooseKeepEDF, self).__init__(tau)
        self.prioOffset = max([task.alpha for task in tau.tasks])

    def idleCPUsCount(self, simu):
        return len(filter(lambda cpu: cpu.job is None, simu.CPUs))

    def earliestPreempArrival(self, job, simu):
        # return earliest time at which job will be preempted if it is chosen now
        t = simu.t
        jobP = 1.0/(self.prioOffset + job.deadline - job.alpha())
        finishTime = self.finishTime(job, simu)
        # test against priority of next arrival of each task
        candidate = None
        for task in simu.system.tasks:
            if t < task.O:
                nextArrival = task.O
            else:
                nextArrival = (t - task.O) + (task.T - (t - task.O) % task.T) + task.O
            prio = 1.0/(self.prioOffset + nextArrival + task.D)
            if prio >= jobP and nextArrival < finishTime and (candidate is None or nextArrival < candidate):
                candidate = nextArrival
        return candidate

    def priority(self, job, simu):
        # if simu.t == 2 and job.deadline == 9:
        #     pdb.set_trace()
        if self.isJobExecuting(job, simu):
            return 1.0/(self.prioOffset + job.deadline - job.alpha())
        epa = self.earliestPreempArrival(job, simu)
        if epa and epa - simu.t <= job.alpha():  # execution would cost more than idling
            return -1 * float("inf")
        else:
            return 1.0/(self.prioOffset + job.deadline)
