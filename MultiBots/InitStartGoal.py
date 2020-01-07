class InitStartGoal():

    def __init__(self, agents):
        self.agents = agents
        self.initstartgoal()

    def initstartgoal(self):

        n = ['A', 'B', 'C', 'D', 'E', 'F']  # start
        m = ['M', 'M', 'M', 'M', 'M', 'M']  # goal
        p = ['S', 'T', 'U', 'V', 'W', 'Y']  # charging position

        for i in self.agents:  # give the agents start and goal letter
            i.startletter = n[0]
            i.goalletter = m[0]
            i.chargingposition = p[0]
            n.pop(0)
            m.pop(0)
            p.pop(0)
