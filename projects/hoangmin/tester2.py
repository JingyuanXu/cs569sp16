import sut
import sys
import random
import time
import math
import os
#implementing outliers of least coverages
# parsing parameters

TIME_BUDGET = int(sys.argv[1])

SEED = int(sys.argv[2])

DEPTH = int(sys.argv[3])

WIDTH = int(sys.argv[4])

FAULT_CHECK = int(sys.argv[5])

COVERAGE_REPORT = int(sys.argv[6])

RUNNING_DETAIL = int(sys.argv[7])


# init objects and parameters
sut=sut.sut()
sut.silenceCoverage()
rand = random.Random()
rand.seed(SEED)

coverageCount = {}

new_state = []
new_statement_by_state = []

selected_state = []
k_selected = []

state_queue = []
state_visited = []

failure_file = "failure"
bug_no = 0;

#define sub-routines
def randomAction():
    global bug_no, time_start, allAction, ii
    action = sut.randomEnabled(rand)
    ok = sut.safely(action)
    elapsed = time.time() - time_start
    if RUNNING_DETAIL:
        if len(sut.newBranches()) > 0:
            print "ACTION:", action[0]
            for b in sut.newBranches():
                print elapsed, len(sut.allBranches()), "New branch", b

    if not ok:  # found a bug
        bug_no += 1
        print "FOUND A BUG! #", bug_no
        print sut.failure()
        # write the bug to file if FAULT_ARGUMENT is enabled
        if (FAULT_CHECK):
            filename = failure_file + str(bug_no) + ".test"
            sut.saveTest(sut.test(), filename )
        print "time: ", time.time() - time_start
    return ok

# begin testing
time_start = time.time()
curDepth = 1
state_queue = [sut.state()]

# Phase 1 : run random test in TIME_BUDGET/4 seconds with depth = DEPTH to find out k statements that we rarely cover

TIME_PHASE1 = TIME_BUDGET / 4
print "PHASE 1..."
while(time.time()< time_start + TIME_PHASE1):
    sut.restart()
    for d in xrange(0,DEPTH):
        ok = randomAction()
        if not ok:
            break
        if(len(sut.newStatements())>0): # we found some new statements. Of course such statement coverages are least, so save its state for later use
            new_state.append(sut.state())
            new_statement_by_state.append(sut.newStatements())
    for s in sut.currStatements():
        if s not in coverageCount:
            coverageCount[s]=0
        coverageCount[s] +=1

# find mean & std to filter outliers
sortedCoverage = sorted(coverageCount.keys(),key=lambda x:coverageCount[x])

threshold =  coverageCount[sortedCoverage[3]]
print "Threshold: " , threshold
# filter to keep only states of threshold-least coverage
for s in sortedCoverage:
    #print coverageCount[s]
    if coverageCount[s]> threshold:
        break
    for k in k_selected:
        if s in new_statement_by_state[k]:
            continue
    for k in xrange(0,len(new_statement_by_state)):
        if s in new_statement_by_state[k]:
            k_selected.append(k)

for k in k_selected:
    selected_state.append(new_state[k])

print bug_no, " BUGS FOUND"

# PHASE 2
#exploit states of k least coverages to explore new statements
print "PHASE 2..."
TIME_PHASE2 = TIME_BUDGET - TIME_PHASE1

all_state =[]
new_statement_by_state = []
i = 0;
time_start = time.time()
time_out = 0
while(time.time()<time_start + TIME_PHASE2 and time_out == 0 ):
    i=0
    for state in selected_state:
        i+=1
        time_state = float(TIME_PHASE2) / (len(selected_state)*(i+1)) # allocate time for each state differently depend on how many time it was covered by phase 1
        time_start2 = time.time()
        while(time.time()<time_start2+time_state):
            sut.restart()
            sut.backtrack(state)
            for d in xrange(0,DEPTH):
                ok = randomAction()
                if not ok:
                    break
                if (len(sut.newStatements()) > 0):  # we found some new statements. Of course such statement coverages are least, so save it for later use
                    print "Found new statement!"
                    d = 0
                    selected_state.remove(state);
                    state = sut.state()
                    selected_state.insert(i-1,state);
                if(time.time()>time_start + TIME_PHASE2):
                    time_out = 1
                    break;
            for s in sut.currStatements():
                if s not in coverageCount:
                    coverageCount[s] = 0
                coverageCount[s] += 1
            if time_out == 1:
                break;
        if(time_out == 1):
            break;
        sortedCoverage = sorted(coverageCount.keys(), key=lambda x: coverageCount[x])

print bug_no, " BUGS FOUND"

if (COVERAGE_REPORT):
    sut.internalReport()



