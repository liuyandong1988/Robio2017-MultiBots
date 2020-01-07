import math
from Models import angle
from Graph import MyQUEUE, BFS, CPD
from param import *
from distlib._backport.tarfile import TUREAD
import time

start = time.time()
goodscurrentcnt = 0
goodsremain = goodstotal
num_agents_threshold = 0
num_agents_current = num_agents
print 'Start'


class Strategy():

    def __init__(self, boxes, goods, agents, graph_nodes, graph):
        self.boxes = boxes
        self.goods = goods
        self.agents = agents
        self.graph_nodes = graph_nodes
        self.graph = graph

        self.activeAgents = []  # a list of ids of active (not dead) agents
        self.currentOverallPlans = {}  # agent_id overall plans
        self.currentdistance = {}  # agent_id distance
        self.totaldistance = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.path_queues = [MyQUEUE() for i in xrange(num_agents)]

        # every agent gets a good
        for i in self.agents:
            i.goodnum = GOOD_NUM[0]
            GOOD_NUM.pop(0)

        # put agent to corresponding letter position
        for i in self.agents:
            i.color = 0
            self.dummyTeleporterToNode(
                i.agent_id, i.chargingposition, i.angle.theta)

        # agent_id & goal
        for i in self.agents:
            if i.status == 0:
                i.color = 1
                self.setNewPlan(
                    i.agent_id, i.startletter, self.goods[i.goodnum].goodfindletter[0])

    # put the agent to an accurate position
    def dummyTeleporterToNode(self, agent_id, letter, angle):
        self.dummyTeleporter(
            agent_id, (self.graph_nodes[letter].x, self.graph_nodes[letter].y), angle)

    def dummyTeleporter(self, agent_id, toWhere, angle):
        self.agents[agent_id].x, self.agents[agent_id].y = toWhere
        self.agents[agent_id].angle.theta = angle
        # change the dead agent to idle status and anothers do not
        if self.agents[agent_id].status == 3:
            self.agents[agent_id].status = 0

    # set a new plan from start letter to goalletter
    def setNewPlan(self, agent_id, start, goalLetter):
        self.currentOverallPlans[agent_id] = BFS(
            self.graph, start, goalLetter, self.path_queues[agent_id])  # find the path to goal
#         print 'agent_id:%d' % agent_id,
#         print ' >> StartLetter:%s' % start,
#         print ' >> Path:', self.currentOverallPlans[agent_id],
#         print ' >> EndLetter:%s' % goalLetter
        self.currentdistance[agent_id] = CPD(
            self.currentOverallPlans[agent_id])
#         print '>>>>>>currentdistance: %d' % self.currentdistance[agent_id]
        self.totaldistance[agent_id] += self.currentdistance[agent_id]

    # pick up the goods
    def pickupgoods(self, agent_id):
        if self.agents[agent_id].getgood == 0:  # mark get good or not
            # arrived goods waiting for picking up goods
            self.agents[agent_id].waiting += 1
            if self.agents[agent_id].waiting == 10:
                self.agents[agent_id].waiting = 0
                self.agents[agent_id].getgood = 1
                # good is empty
                self.goods[self.agents[agent_id].goodnum].status = 0
                self.agents[agent_id].color = 2
                self.agents[agent_id].nextIntemediateGoal = self.goods[
                    self.agents[agent_id].goodnum].goodfindletter[1]  # goods position to next letter
        else:
            self.travelToNextNode(agent_id)

    # take off goods
    def takeoffgoods(self, agent_id):
        global goodscurrentcnt, num_agents_working, num_agents_current, goodsremain
        bluestatus = 0   # empty agent
        redstatus = 0    # carry goods agent
        if self.agents[agent_id].out == 1:
            self.agents[agent_id].angle.theta = -90.0
            # arrived goods waiting for picking up goods
            self.agents[agent_id].waiting += 1
            if self.agents[agent_id].waiting == 20:
                 # the number of goods in the area and in the carbox

                # count the get good times
                self.boxes[goodscurrentcnt].status = 1
                goodscurrentcnt += 1
                goodsremain = goodstotal - goodscurrentcnt
                # mark reset for next good
                self.agents[agent_id].waiting = 0
                self.agents[agent_id].out = 0
                self.agents[agent_id].goodforwardletter = 0
                self.agents[agent_id].goodbackwardletter = 0
                self.agents[agent_id].getgood = 0
                self.agents[agent_id].waiting = 0
                self.agents[agent_id].currentstatus = 1
                self.agents[agent_id].status = 0
                self.path_queues[agent_id].holder = []

                # charging debug mark
                self.agents[agent_id].debug = 0
                self.agents[agent_id].debug2 = 0

                for r in self.agents:
                    if r.status == 1:
                        if r.needchargemark == 0:
                            bluestatus += 1
                    elif r.status == 2:
                        redstatus += 1

                if num_agents_current > num_agents_threshold:
                    num_agents_current -= 1
                    self.agents[agent_id].color = 0
                    self.agents[agent_id].status = 0
                    self.agents[agent_id].withStepPlan = 0
                    self.agentbackhome(agent_id)
                    print "threshold,goback!"

                # not the last time need set the plan
                else:
                    if (goodsremain - redstatus) > bluestatus:
                        # set next good plan
                        self.agents[agent_id].goodnum = GOOD_NUM[0]
                        GOOD_NUM.pop(0)
                        startletter = self.agents[agent_id].goalletter
                        goalletter = self.goods[
                            self.agents[agent_id].goodnum].goodfindletter[0]
                        self.setNewPlan(agent_id, startletter, goalletter)
                        self.agents[agent_id].status = 1
                    else:
                        num_agents_current -= 1
                        self.agents[agent_id].color = 0
                        self.agents[agent_id].status = 0
                        self.agentbackhome(agent_id)
                        print "finish,goback!"

                self.agents[agent_id].withStepPlan = 0
# print 'Fetching the number of goods:', goodscurrentcnt, 'good:',
# self.agents[agent_id].goodnum

    # charging
    def agentcharging(self, agent_id):
        self.agents[agent_id].status = 0
        self.agents[agent_id].angle.theta = -90
        self.dummyTeleporterToNode(
            agent_id,     self.agents[agent_id].chargingposition, self.agents[agent_id].angle.theta)
        self.path_queues[agent_id].holder = []

    # finish working and parking
    def agentbackhome(self, agent_id):
        self.agents[agent_id].backhomemark = 1
        self.agents[agent_id].status = 0
        self.path_queues[agent_id].holder = []
        self.setNewPlan(
            agent_id, self.agents[agent_id].goalletter, self.agents[agent_id].startletter)
#         print 'Idle agent_id:', agent_id
#         print 'Path of going home to charge:', self.currentOverallPlans[agent_id]
#         print '-' * 50

    # go to the good position
    def travelTogood(self, agent_id, agentposition):
        distance = math.sqrt(
            (self.agents[agent_id].x - agentposition[0])**2 + (self.agents[agent_id].y - agentposition[1])**2)
        step = (TIME_RATE / FRAME_PER_SECOND) * self.agents[agent_id].speed

        if distance < 5.0:
            # leave the letter forward letter
            self.agents[agent_id].goodforwardletter = 0
            # change agent statues ready to get goods
            self.agents[agent_id].status = 2
            self.agents[agent_id].debug = 1
#             print "agent_id:%d" % agent_id,
#             print" >> Arrived good:%d" % self.agents[agent_id].goodnum
        if step > distance:  # too fast
            self.agents[agent_id].stepToGoal(agentposition, distance)
        else:
            self.agents[agent_id].stepToGoal(agentposition, step)

    # go to the letter position
    def travelToNextNode(self, agent_id):
        if self.agents[agent_id].status != 2 and self.agents[agent_id].backhomemark == 0:
            self.agents[agent_id].status = 1
            # go back to charge and agents blink
            if self.agents[agent_id].backtocharge == 0:
                self.agents[agent_id].color = 1

        if self.agents[agent_id].nextIntemediateGoal == 'x':
            return
        nextgoalletter_x = self.graph_nodes[
            self.agents[agent_id].nextIntemediateGoal].x
        nextgoalletter_y = self.graph_nodes[
            self.agents[agent_id].nextIntemediateGoal].y
        goal = (nextgoalletter_x, nextgoalletter_y)
        step = (TIME_RATE / FRAME_PER_SECOND) * self.agents[agent_id].speed
        distance = math.sqrt(
            (self.agents[agent_id].x - goal[0])**2 + (self.agents[agent_id].y - goal[1])**2)

        if distance < 5.0:
            # agent with goods set the new plan with goods
            if self.agents[agent_id].getgood == 1 and self.agents[agent_id].goodbackwardletter == 0:
                goodbackletter = self.agents[agent_id].nextIntemediateGoal
                outletter = self.agents[agent_id].goalletter
                self.path_queues[agent_id].holder = []
                self.setNewPlan(agent_id, goodbackletter, outletter)
                # arrived the goods backward letter
                self.agents[agent_id].goodbackwardletter = 1
            self.currentOverallPlans[agent_id].pop(0)
            self.agents[agent_id].withStepPlan = 0
# print agent_id, " >> ARRIVED INTEMEDIATE ",
# self.agents[agent_id].nextIntemediateGoal
            self.dummyTeleporterToNode(
                agent_id, self.agents[agent_id].nextIntemediateGoal, self.agents[agent_id].angle.theta)  # hard reset to position
            return
        if step > distance:  # too fast
            self.agents[agent_id].stepToGoal(goal, distance)
        else:
            self.agents[agent_id].stepToGoal(goal, step)

    # get the next letter on the path
    def getNextPlannedNode(self, agent_id):
        if not self.currentOverallPlans.has_key(agent_id):
            #             print "no plan for agent ", agent_id
            return 'x'
        elif self.currentOverallPlans[agent_id] == []:  # all plans are don
            return 'x'
        else:  # with valid plan (normal case)
            plan = self.currentOverallPlans[agent_id][0]
#             print agent_id, " > going to ", plan
            return plan

    # run plan to fetch goods
    def computeStartToGood(self):
        global goodscurrentcnt
        for r in self.agents:
            # record time
            if r.startbutton == 0:
                r.starttime = time.time()
#                 print 'agent_id:', r.agent_id, 'starttime:', r.starttime
                r.startbutton = 1

            # agent collision mark
            if r.stopmark == 0 and r.chargemark == 0:
                r.agentcolmark = 0
                plan = ''
                if r.status == 3:  # agent dead statues
                    continue
                # move agent from good forward letter to good
                elif r.status == 1 and r.goodforwardletter == 1:

                    self.travelTogood(r.agent_id, (self.goods[r.goodnum].agentx, self.goods[
                                      r.goodnum].agenty))  # from forward letter to goods
                # arrived at goods
                elif r.status == 2 and r.goodbackwardletter == 0:
                    self.pickupgoods(r.agent_id)  # pick up goods
                # arrived at goal
                elif r.status == 2 and r.out == 1:
                    #                         if r.waiting == 0:
                    #                             print "agent_id:%d" % r.agent_id,
                    # print " >> Arrived goal:%s" % r.goalletter
                    self.takeoffgoods(r.agent_id)  # take off goods
                # run among the letters
                else:
                    self.activeAgents.append(r.agent_id)
                    # get the next node of  a seq of letter on the path
                    plan = self.getNextPlannedNode(r.agent_id)
                    # need to charge
                    if r.needchargemark == 1 and r.backtocharge == 0 and r.backhomemark == 0:
                        # without good
                        if r.currentstatus == 1 and r.debug == 0:
                            # print "Needs to charge!"
                            # have goods to fetch
                            if goodscurrentcnt != goodstotal:
                                GOOD_NUM.insert(0, r.goodnum)
#                                     print GOOD_NUM
                                # planning the charging path
                                self.path_queues[
                                    r.agent_id].holder = []
                                self.setNewPlan(
                                    r.agent_id, plan, r.startletter)
                                # mark go back to charge
                                r.backtocharge = 1

                    if r.withStepPlan:
                        self.travelToNextNode(r.agent_id)
                    else:

                        if (plan == 'x'):
                            # finish work and parking
                            if r.backtocharge == 1 or r.backhomemark == 1:
                                r.chargemark = 1
                                r.needchargemark = 0
                                self.agentcharging(r.agent_id)
                            else:
                                r.withStepPlan = 0
                                if r.goodforwardletter == 0 and r.getgood == 0 and r.out == 0:
                                    # arrived at good forward letter final
                                    r.goodforwardletter = 1
                                else:

                                    # arrived at out take off goods
                                    r.out = 1
    #                         print "Continue ", r.agent_id, " to ", plan
                        r.nextIntemediateGoal = plan
                        r.withStepPlan = 1
