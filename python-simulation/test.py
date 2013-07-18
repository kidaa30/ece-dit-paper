import pylab

numberOfSystems = "prout"

pylab.figure()
pylab.plot(range(15, 20), [15, 16, 17, 18, 19], "b-", label="DIT ALL")
pylab.ylabel("time (s)")
pylab.xlabel("e")
pylab.title("Computation time for some values of e (" + str(numberOfSystems) + " tasks)")
pylab.legend(loc=0)
#pylab.axis([-1, nbrDecisions, 0, number_of_steps])
pylab.savefig("./plots/001.png")
pylab.show()
