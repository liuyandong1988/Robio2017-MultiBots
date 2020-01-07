import math
import random
from param import *


class angle():
    theta = 0.0

    def __init__(self, theta=0.0):
        self.theta = theta

    def increase(self, delta):
        self.theta += delta
        while self.theta > 361:
            self.theta -= 360

    def decrease(self, delta):
        self.theta -= delta
        while self.theta < 0:
            self.theta += 360

    def cos(self):
        return math.cos(self.theta * math.pi / 180.0)

    def sin(self):
        return math.sin(self.theta * math.pi / 180.0)

    def tan(self):
        return math.tan(self.theta * math.pi / 180.0)

    def fromAtan(self, atanValue):
        return angle(math.atan(atanValue) / 180.0 * math.pi)


class point():
    x = 0
    y = 0
    r = 0


class good():  # goods to be operated
    status = 1  # 0: idle  1: operating
    x = 0.0  # top left corner x,y
    y = 0.0
    agentx = 0.0  # agent carry good position
    agenty = 0.0
    goodfindletter = ''


class box():  # goods to be operated
    status = 1  # 0: idle  1: operating
    x = 0.0  # top left corner x,y
    y = 0.0


class agent():  # agent robot to operate

    def __init__(self):
        # 0: idle; 1: moving to good; 2: carrying good to goal, 3: not in task
        # (dead)
        self.status = 0
        self.x = 0.0
        self.y = 0.0
        self.r = 0.2
        self.angle = angle()

        self.speed = agent_speed
        self.agent_id = -1
        # if the robot is moving to an intemediate node, this is true
        self.nextIntemediateGoal = ''
        self.withStepPlan = 0

        self.startletter = ''  # agents start and end position
        self.goalletter = ''
        self.getgood = 0  # mark get good or not
        self.waiting = 0  # pick up or take off goods waiting time
        # good path forwardletter and backwardletter mark
        self.goodforwardletter = 0
        self.goodbackwardletter = 0

        self.out = 0  # agent arrived at goal mark and take off goods mark
        self.goodnum = 0  # agents fetch the number of goods
#         self.getgoodscnts = 0  # agents fetch the times of goods
#         self.takeoff = 0 #
        self.stopmark = 0  # agents collision mark
        self.stoptime = 0
        self.printover = 0

        self.chargingposition = ''  # charging position
        self.consumenergy = 0
        self.currentenergy = 0
        self.fullenergy = 10
        self.backtocharge = 0
        self.needchargemark = 0
        self.currentstatus = 0
        self.firsttime = 0
        self.steptimes = 0
        self.chargemark = 0
        self.blinktimes = 0
        self.fullenergymark = 0
        self.color = 0
        self.chargetimes = 0
        self.chargenergy = 0
        self.backhomemark = 0
        self.readymark = 0
        self.parkingmark = 0
        self.stopwait = 0
        self.chargecnts = 0

        self.starttime = 0
        self.endtime = 0
        self.costtime = 0
        self.startbutton = 0
        self.endbutton = 0
        self.costbutton = 0
        self.endtimemark = 0

        self.debug = 0
        self.debug2 = 0

        self.batteryangle1 = angle()
        self.batteryangle2 = angle()
        self.lastangle = 0
        self.batterystatues = 1
        self.batteryfullpos = 0
        self.batterypos = 0
        self.width = 0

        self.agentcolmark = 0

    def move(self, offset):
        self.x += offset[0]
        self.y += offset[1]
        self.angle.theta = math.atan2(-offset[1], offset[0]) * 180 / math.pi

    def stepToGoal(self, goalCoor, step):  # nocheck on whether arrived
        offset = (0, 0)
        dy = goalCoor[1] - self.y
        dx = goalCoor[0] - self.x
        if dx == 0:
            # print "Easy dY [", self.agent_id, "]"
            if dy > 0:
                offset = (0, step)
            else:
                offset = (0, -step)
        if dy == 0:
            # print "Easy dX [", self.agent_id, "]"
            if dx > 0:
                offset = (step, 0)
            else:
                offset = (-step, 0)
        if (dx != 0) and (dy != 0):
            theta = math.atan2(-dy, dx)
            offset = (step * math.cos(theta), step * math.sin(theta))
        self.move(offset)

    def stop(self):
        self.stopmark = 1
