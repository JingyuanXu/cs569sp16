import sut
import random
import sys
import time
import math
import argparse
from collections import namedtuple



#Functions

def collectCoverage():
    global coveraged
    for s in sut.currStatements():
        if s not in coveraged:
            coveraged[s] = 0
        coveraged[s] += 1

def randomAction():
    global actCount, bugs, visited
    act = sut.randomEnabled(rgen)
    actCount += 1
    ok = sut.safely(act)
    if not ok:
        bugs += 1
        if argv.FAULTS:
            file = "failure"+str(bugs)+".test"
            fault = sut.test()
            sut.saveTest(fault,file)
            # if argv.COVERAGE:
            #     collectCoverage()
            # sut.restart()
    else:
        if argv.RUNNING:
            if sut.newBranches() != set([]):
                for b in sut.newBranches():
                    print  time.time() - start, len(sut.allBranches()) ,"new branch", b
        if len(sut.newStatements()) != 0:
            visited.append((list(sut.test()), set(sut.currStatements())))
    return ok


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('TIMEOUT', type=int, default=30, help='Time in seconds for testing.')
    parser.add_argument('SEED', type=int, default=1, help='Seed for Python Random.random object used for random number generation in code.')
    parser.add_argument('DEPTH', type=int, default=100, help='Maximum length of a test generated by algorith.')
    parser.add_argument('WIDTH', type=int, default=1, help='Maximum memory/BFS queue/other parameter that is basically a search width.')
    parser.add_argument('FAULTS', type=int, default=0, help='Faults in the SUT.')
    parser.add_argument('COVERAGE', type=int, default=1, help='Final coverage report produced.')
    parser.add_argument('RUNNING', type=int, default=1, help='Running info on branch coverage should be produced.')
    parsed_args = parser.parse_args(sys.argv[1:])
    return (parsed_args, parser)

def make_config(pargs, parser):
	pdict = pargs.__dict__
	key_list = pdict.keys()
	arg_list = [pdict[k] for k in key_list]
	Config = namedtuple('Config', key_list)
	nt_config = Config(*arg_list)
	return nt_config





# TIMEOUT    = int(sys.argv[1])    #
# SEED       = int(sys.argv[2])    #
# DEPTH      = int(sys.argv[3])    #
# WIDTH      = int(sys.argv[4])
# FAULTS     = int(sys.argv[5])    #
# COVERAGE   = int(sys.argv[6])    #
# RUNNING    = int(sys.argv[7])




def main():
	#global variables are defined here
	global sut, rgen, actCount, bugs, coveraged, visited, start, argv
	parsed_args, parser = parse_args()
	argv = make_config(parsed_args, parser)
	start = time.time()
	sut        = sut.sut()
	sut.silenceCoverage()
	rgen       = random.Random()
	rgen.seed(argv.SEED)
	actCount   = 0
	bugs       = 0
	coveraged  = {}
	visited    = []





	print "STARTING PHASE 1"

	while time.time() - start < argv.TIMEOUT * 0.5:
	    sut.restart()

	    for s in xrange(0,argv.DEPTH):
	        randomAction()
	    collectCoverage()

	sortedCov = sorted(coveraged.keys(), key=lambda x: coveraged[x])
	for s in sortedCov:
	    print s, coveraged[s]



	print "STARTING PHASE 2"

	while time.time() - start < argv.TIMEOUT :
	    belowMedian = set([])
	    sort = sorted(coveraged.keys(),key = lambda x : coveraged[x])

	    a = len(sort)/2


	    for s in sort:
	        if coveraged[s] < sort[a]:
	            belowMedian.add(s)
	        else:
	            break
	       	
	    
	    activePool = []
	    for (t,c) in visited:
	        for s in c:
	            if s in belowMedian:
	                activePool.append((t,c))
	                break
	    sut.restart()
	    if len(sut.newStatements()) != 0:
	        print "new statement",sut.newStatements()
	        visited.append((list(sut.test()), set(sut.currStatements())))
	    for s in xrange(0,argv.DEPTH):
	        if not randomAction():
	            break
	    collectCoverage()

	sortedCov = sorted(coveraged.keys(), key=lambda x: coveraged[x])
	for s in sortedCov:
	    print s, coveraged[s]




	if argv.COVERAGE:
	    sut.internalReport()

	print "FAILURES ",bugs, "TIMES"
	print "TOTAL ACTIONS", actCount
	print "TOTAL RUNTIME", time.time()-start

if __name__ == '__main__':
	main()





        

