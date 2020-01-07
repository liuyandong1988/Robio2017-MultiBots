import InitStartGoal
import Strategy


class AgentCharge():

    def __init__(self, agents, graph, goods, graph_nodes, thresholdenergy, consumingrate, chargingrate):
        self.agents = agents
        self.graph = graph
        self.goods = goods
        self.graph_nodes = graph_nodes

        self.thresholdenergy = thresholdenergy
        self.consumingrate = consumingrate
        self.chargingrate = chargingrate

    def eleconsume(self, agent_id):

        self.agents[agent_id].steptimes += 1
#             print r.agent_id, r.steptimes
        self.agents[agent_id].consumenergy = self.consumingrate * \
            self.agents[agent_id].steptimes
        self.agents[agent_id].currentenergy = self.agents[
            agent_id].fullenergy - self.agents[agent_id].consumenergy
#         print '!!!', r.agent_id, '???', r.currentenergy

        if self.agents[agent_id].currentenergy <= self.thresholdenergy:
            #                 print r.agent_id
            if self.agents[agent_id].currentenergy <= 0:
                print "agent_id", agent_id
                raw_input("error")
            elif self.agents[agent_id].status != 0:
                if self.agents[agent_id].backtocharge == 0:
                    if self.agents[agent_id].firsttime == 0:
                        self.agents[agent_id].firsttime = 1
                        # record status takeoff good or go back to charge
                        self.agents[agent_id].currentstatus = self.agents[
                            agent_id].status
                        self.agents[agent_id].needchargemark = 1

                    if self.agents[agent_id].currentstatus == 2:
                        if self.agents[agent_id].steptimes % 20 == 0:
                            self.agents[agent_id].color = 2
                        elif self.agents[agent_id].steptimes % 10 == 0:
                            self.agents[agent_id].color = 4
                else:
                    if self.agents[agent_id].steptimes % 20 == 0:
                        self.agents[agent_id].color = 1
                    elif self.agents[agent_id].steptimes % 10 == 0:
                        self.agents[agent_id].color = 4

    def charging(self, agent_id):
        if self.agents[agent_id].fullenergymark != 1:

            self.agents[agent_id].chargetimes += 1
            self.agents[agent_id].chargenergy = self.chargingrate * 1
            self.agents[
                agent_id].currentenergy += self.agents[agent_id].chargenergy
            if self.agents[agent_id].currentenergy >= self.agents[agent_id].fullenergy:
                self.agents[agent_id].fullenergymark = 1
            else:
                if self.agents[agent_id].chargetimes % 20 == 0:
                    self.agents[agent_id].color = 0
                elif self.agents[agent_id].chargetimes % 10 == 0:
                    self.agents[agent_id].color = 4
