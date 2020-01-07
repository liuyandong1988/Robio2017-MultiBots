import Models
import math
import Strategy
import Graph
from param import *
from InitStartGoal import InitStartGoal
import time
import ChargeThreshold


timer_stop = 0  # mark the timer stop
collisioncnt = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
colltotalcnt = 0
agent_time = []  # record the agent working time
mark = 1
recordthreshold = 0
n = 2


class Controller:

    def __init__(self):
        self.time = 0

        self.cillioned = []  # log the collision agents
        self.deadTargets = []
        self.threshold = 0

        # add goods
        self.goods = [Models.good() for i in xrange(10 * 8)]
        # put goods in warehouse
        indexupleft = 0   # index the goods position  to mark letter
        indexupright = 0
        indexdownleft = 0
        indexdownright = 0

        for group in range(10):
            offset = (0, 0)
            if group % 2 == 0:  # upper row
                offset = (
                    (3 * (group / 2) + 1) * L + margin_left, margin_top + L)
            elif group % 2 == 1:  # lower row
                offset = (
                    (3 * (group / 2) + 1) * L + margin_left, margin_top + 6 * L)
            # print "for good in group ", group, " Offset: ", offset
            for i in range(8):
                if (i % 2 == 0):  # on left
                    self.goods[i + group * 8].status = 0
                    self.goods[i + group * 8].x = offset[0]
                    self.goods[i + group * 8].y = offset[1] + int(i / 2) * L
                    self.goods[
                        i + group * 8].agentx = self.goods[i + group * 8].x - 25
                    self.goods[
                        i + group * 8].agenty = self.goods[i + group * 8].y + 25
                    if group % 2 == 0:
                        self.goods[
                            i + group * 8].goodfindletter = GOOD_FIND_LETTER_UP_LEFT[indexupleft]
                    else:
                        self.goods[
                            i + group * 8].goodfindletter = GOOD_FIND_LETTER_DOWN_LEFT[indexdownleft]

                elif (i % 2 == 1):  # on right
                    self.goods[i + group * 8].status = 0
                    self.goods[i + group * 8].x = offset[0] + L
                    self.goods[i + group * 8].y = offset[1] + int(i / 2) * L
                    self.goods[
                        i + group * 8].agentx = self.goods[i + group * 8].x + 75
                    self.goods[
                        i + group * 8].agenty = self.goods[i + group * 8].y + 25
                    if group % 2 == 0:
                        self.goods[
                            i + group * 8].goodfindletter = GOOD_FIND_LETTER_UP_RIGHT[indexupright]
                    else:
                        self.goods[
                            i + group * 8].goodfindletter = GOOD_FIND_LETTER_DOWN_RIGHT[indexdownright]

            if group % 2 == 0:
                indexupleft += 1
                indexupright += 1
            else:
                indexdownleft += 1
                indexdownright += 1

        # change the good status ocuppied red colour
        for i in xrange(len(GOOD_NUM)):
            self.goods[GOOD_NUM[i]].status = 1

        # add boxes
        self.boxes = [Models.box() for i in xrange(50)]
        offset = (75, 675)
        for i in range(50):
            self.boxes[i].status = 0
            self.boxes[i].x = offset[0] + i * int(L / 4)
            self.boxes[i].y = offset[1]

        agents_theta = 270
        battery_theta = agents_theta - 135
        # add agents
        self.agents = [Models.agent() for i in xrange(num_agents)]
        for r in range(num_agents):
            if r < num_agents / 2:
                self.agents[r].x = world_width / 2 - r * L
            else:
                self.agents[r].x = world_width / 2 + r * L
            self.agents[r].y = L
            self.agents[r].r = L / 4
            self.agents[r].status = 3  # all dead
            self.agents[r].color = 3
            self.agents[r].angle = Models.angle(agents_theta)
            self.agents[r].lastangle = agents_theta
            self.agents[r].agent_id = r

            self.agents[r].batteryangle1 = Models.angle(battery_theta)
            self.agents[r].batteryangle2 = Models.angle(battery_theta - 90)
            self.agents[r].batterystatus = 1

        # genetate graph
        self.graph_nodes = Graph.generateGraphNodes()
        self.graph = Graph.generateGraph()

        self.startPoints = [Models.point() for i in xrange(num_areas)]
        R1 = 'ABCDEF'
        for r in range(num_areas):
            self.startPoints[r].x = Graph.graph_nodes[R1[r]].x
            self.startPoints[r].y = Graph.graph_nodes[R1[r]].y
            self.startPoints[r].r = L / 3

        self.endPoints = [Models.point() for i in xrange(num_areas)]
        R1 = 'MNOPQR'
        for r in range(num_areas):
            self.endPoints[r].x = Graph.graph_nodes[R1[r]].x
            self.endPoints[r].y = Graph.graph_nodes[R1[r]].y
            self.endPoints[r].r = L / 3

        self.chargePoints = [Models.point() for i in xrange(num_areas)]
        R1 = 'STUVWY'
        for r in range(num_areas):
            self.chargePoints[r].x = Graph.graph_nodes[R1[r]].x
            self.chargePoints[r].y = Graph.graph_nodes[R1[r]].y - 5
            self.chargePoints[r].r = L / 3

        # initial agents start and goal position letter
        self.initstartgoal = InitStartGoal(self.agents)

        # set the plan strategy
        self.strategy = Strategy.Strategy(self.boxes,
                                          self.goods, self.agents, self.graph_nodes, self.graph)

        # set agent charge
        self.agentcharge = ChargeThreshold.AgentCharge(
            self.agents, self.graph, self.goods, self.graph_nodes, thresholdenergy=3.5, consumingrate=0.005, chargingrate=0.05)

    # check the collision needs the function
    # collision allow the angle
    def angle_is_close(self, a, b):
        return abs(a - b) < th_close_angle

    # collision distance
    def collisionBetweenAgents(self, a, b):
        if math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2) <= a.r + b.r + 8:
            return True
        return False

    # check the collision among the agents
    def checkCollisionsAndStop(self):
        global collisioncnt
        checked = []
        for i in self.agents:
            for j in self.agents:
                if i == j:
                    continue
                else:
                    checked.append((i, j))  # log
                    if self.collisionBetweenAgents(i, j):
                        angle_i_to_j = math.atan2(-(j.y - i.y),
                                                  j.x - i.x) * 180 / math.pi
                        if self.angle_is_close(angle_i_to_j, i.angle.theta):
                            if (i.agent_id, j.agent_id) not in self.cillioned:
                                self.cillioned.append((i.agent_id, j.agent_id))
                                # collision mark and the backward agent stop
                                # every action
                                i.stop()

                            if i.agentcolmark == 0:
                                collisioncnt[i.agent_id] += 1
                                i.agentcolmark = 1
                                print i.agent_id, 'collision:', collisioncnt

                        elif angle_i_to_j > 133 and angle_i_to_j < 137:
                            if (i.agent_id, j.agent_id) not in self.cillioned:
                                self.cillioned.append((i.agent_id, j.agent_id))
                                i.stop()

                            if i.agentcolmark == 0:
                                collisioncnt[i.agent_id] += 1
                                i.agentcolmark = 1
                                print i.agent_id, 'collision:', collisioncnt

                        else:
                            continue
                    else:
                        # collision finish and run again
                        if len(self. cillioned) != 0:
                            if self. cillioned[0] == (i.agent_id, j.agent_id):
                                i.stopmark = 0
                                self. cillioned.pop(0)
                        continue

    def responsemodel(self):
        Strategy.num_agents_threshold = 10

    # charge control
    def chargeController(self):
        workagentscnt = 0
        for r in self.agents:
            # the number of working agents
            if r.status != 0 and r.needchargemark == 0:
                workagentscnt += 1

        for r in self.agents:
            # consume or charge mark
            if r.chargemark == 1:
                # record end time
                if r.endbutton == 0 and r.endtimemark == 0:
                    r.endtime = time.time()
                    r.costbutton = 1
                    r.endtimemark = 1
#                     print 'agent_id:', r.agent_id, 'endtime:', r.endtime

                # begin charging
                self.agentcharge.charging(r.agent_id)
                # full Electricity mark and waitting to fetch goods again
                if r.fullenergymark == 1:
                    # first into mark the readymark and wait the need
                    if r.stopwait == 0:
                        r.stopwait = 1
                        r.color = 0
                        r.status = 0
                        r.backhomemark = 0
                        r.readymark = 1
                        r.steptimes = 0

#                     if Strategy.goodsremain >= Strategy.num_agents_threshold and workagentscnt < Strategy.num_agents_threshold:
#                         r.readymark = 0

                    # have need and fetch again,more than one time
                    if r.readymark == 0:
                        # reset charging mark
                        r.chargecnts += 1
                        r.fullenergymark = 0
                        r.chargemark = 0
                        r.steptimes = 0
                        r.chargetimes = 0
                        r.firsttime = 0
                        r.backtocharge = 0
                        r.needchargemark = 0
                        r.startbutton = 0
                        r.endbutton = 0
                        r.endtimemark = 0
                        # reset the move forward mark
                        r.status = 1
                        r.withStepPlan = 0
                        r.stopwait = 0
                        # path plan again
                        self.strategy.dummyTeleporterToNode(r.agent_id,
                                                            r.startletter, 0)
                        r.goodnum = GOOD_NUM[0]
                        GOOD_NUM.pop(0)

#                         print 'Fetching again agent_id:', r.agent_id
#                         print 'Fetching the good number:', r.goodnum
#                         print 'Remain goods:', GOOD_NUM
#                         print '-' * 50

                        self.strategy.setNewPlan(
                            r.agent_id, r.startletter, self.goods[r.goodnum].goodfindletter[0])
#                         if r.agent_id = 4:
#                             print self.strategy.currentOverallPlans
                        r.withStepPlan = 0  # find next letter node

            else:
                # Electricity consuming
                self.agentcharge.eleconsume(r.agent_id)

    # idle status and fetch good again
    def agentsRunagain(self):
        needagents = 0
        haveagents = 0
        workagentscnt = 0
        goodsonagents = 0
        debugmark = 0
        cutagents = 0
        agentsready = {}  # record the ready agent

        # calculate the number of need agent and ready agent
        for r in self.agents:
            agentsready[r.agent_id] = r.readymark
            if r.readymark == 1:
                haveagents += 1

            if r.needchargemark == 1:
                #             if r.needchargemark == 1  and len(GOOD_NUM) !=0:
                if r.status == 2:
                    goodsonagents += 1
                needagents += 1
                cutagents += 1
#                 if r.debug == 1:
#                     workagentscnt += 1
            # the number of working agents
            elif r.status != 0:
                workagentscnt += 1

#             if r.status == 1 and r.debug == 1 and r.needchargemark == 1:
#                 #                 print 'haha'
#                 workagentscnt += 1
#                 r.debug2 = 1
#                 debugmark += 1
#
#             if r.debug2 == 1 and r.status != 1:
#                 #                 print 'hei'
#                 workagentscnt += 1
#                 debugmark += 1

        if haveagents != 0:

            if workagentscnt < Strategy.num_agents_threshold:
                needagents = Strategy.goodsremain - \
                    workagentscnt - goodsonagents
                if needagents >= Strategy.num_agents_threshold - workagentscnt:
                    needagents = Strategy.num_agents_threshold - workagentscnt
            else:
                needagents = 0


#             print Strategy.goodsremain, workagentscnt, needagents, debugmark

        # run the ready agent again  //change the mark of readymark
        if Strategy.goodsremain > workagentscnt:
            if needagents != 0 and haveagents != 0:
                Strategy.num_agents_current = workagentscnt + 1
# print 'want:', needagents, 'have:', haveagents, 'num_agents_current',
# Strategy.num_agents_current, agentsready

                if needagents <= haveagents:
                    for r in self.agents:
                        if agentsready[r.agent_id] == 1:
                            r.readymark = 0
                            needagents -= 1
                        if needagents == 0:
                            break
                else:
                    for r in self.agents:
                        if agentsready[r.agent_id] == 1:
                            r.readymark = 0
                    haveagents = 0

    # control timer
    def TimerController(self):
        global mark, timer_stop, agent_time, collisioncnt, colltotalcnt
        chargetotalcnts = 0
        totaltime = 0
        cnts = 0
        for r in self.agents:
            if r.costbutton == 1 and r.chargemark == 1:
                r.costtime += r.endtime - r.starttime
#                 print 'agent_id:', r.agent_id, 'costtime:', r.costtime
                r.costbutton = 0

        if Strategy.goodsremain == 0:
            for r in self.agents:
                if r.chargemark == 1:
                    cnts += 1
                chargetotalcnts += r.chargecnts

            if cnts == 6 and mark == 1:
                mark = 0
                timer_stop = 1
#                 for r in self.agents:
#                     agent_time.append(r.costtime)
#                 for k, v in enumerate(agent_time):
#                     totaltime += v
#                     print 'agent_id:', k, 'costtime:', v
                taskcosttime = time.time() - Strategy.start
#                 avg_agent_num = totaltime / float(taskcosttime)
#                 print agent_time
                print 'Task cost time:', taskcosttime
# print 'Average number of the working status agents', avg_agent_num
                print 'collision:', collisioncnt
                for i, val in collisioncnt.items():
                    colltotalcnt += val
                print 'Total collision counts:', colltotalcnt
                print 'Total charge counts:', chargetotalcnts

    def findangle(self):
        for i in self.agents:
            if i.lastangle != i.angle.theta:
                i.lastangle = i.angle.theta - 135
                i.batteryangle1 = Models.angle(i.lastangle)
                i.batteryangle2 = Models.angle(i.lastangle - 90)
            else:
                pass

            if i.angle.theta == 90 or i.angle.theta == -90:
                i.batteryfullpos = i.x + 2 * i.r * i.batteryangle1.cos(
                ) - (i.x + 2 * i.r * i.batteryangle2.cos())
                i.width = i.y + 3 * i.r * i.batteryangle2.cos() - \
                    (i.y + 2 * i.r * i.batteryangle2.cos())

            elif i.angle.theta == 0 or i.angle.theta == 180:
                i.batteryfullpos = i.y - 2 * i.r * \
                    i.batteryangle1.sin() - \
                    (i.y - 2 * i.r * i.batteryangle2.sin())
                i.width = i.x + 2 * i.r * i.batteryangle1.cos() - \
                    (i.x + 3 * i.r * i.batteryangle1.cos())

    def batteryshow(self):
        for r in self.agents:
            if r.currentenergy >= 0.8 * r.fullenergy:
                r.batterypos = r.batteryfullpos
                r.batterystatus = 1  # green
            elif r.currentenergy >= 0.6 * r.fullenergy:
                r.batterypos = r.batteryfullpos * 0.8
                r.batterystatus = 1  # green
            elif r.currentenergy >= 0.4 * r.fullenergy:
                r.batterypos = r.batteryfullpos * 0.6
                r.batterystatus = 2  # orange
            elif r.currentenergy >= 0.2 * r.fullenergy:
                r.batterypos = r.batteryfullpos * 0.4
                r.batterystatus = 2  # orange
            else:
                r.batterypos = r.batteryfullpos * 0.2
                r.batterystatus = 3  # red

    def update(self):
        # agents fetch goods
        self.strategy.computeStartToGood()
        # TODO avoid collision among agents
        self.checkCollisionsAndStop()
        # count the number of agents
        self.responsemodel()
        # calculate the energy consume
        self.chargeController()
        # idle status and fetch good again
        self.agentsRunagain()
        # start and stop timer
        self.TimerController()
        # battery bar angle
        self.findangle()
        # show the battery
        self.batteryshow()
