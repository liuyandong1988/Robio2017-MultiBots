#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 eelium <eelium@eez008>
#
# Distributed under terms of the MIT license.

"""
graph construction 
"""

from param import *
graph_nodes = dict()


class node(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y


def generateGraphNodes():
    global graph_nodes
    R1 = 'ABCDEF'
    R2 = 'GHIJKL'
    R3 = 'MNOPQR'
    P1 = 'STUVWY'  # charing position
    for i, p in enumerate(R1):
        graph_nodes[p] = node(
            margin_left + i * 3 * L + L / 2, margin_top + L / 2)
    for i, p in enumerate(R2):
        graph_nodes[p] = node(
            margin_left + i * 3 * L + L / 2, margin_top + 5 * L + L / 2)
    for i, p in enumerate(R3):
        graph_nodes[p] = node(
            margin_left + i * 3 * L + L / 2, margin_top + 10 * L + L / 2)
    for i, p in enumerate(P1):
        graph_nodes[p] = node(75 + 150 * i, 85)
    return graph_nodes


def generateGraph():
    # horizon
    # raw
    R1_ = ['A', 'B', 'C', 'D', 'E', 'F']
    R2_ = ['G', 'H', 'I', 'J', 'K', 'L']
    R3_ = ['M', 'N', 'O', 'P', 'Q', 'R']
    # in-use:
    R1 = R1_
    R2 = R2_
    R3 = R3_[::-1]  # reversed
    # vertical
    C1_ = 'AGM'
    C2_ = 'BHN'
    C3_ = 'CIO'
    C4_ = 'DJP'
    C5_ = 'EKQ'
    C6_ = 'FLR'
    C1 = [k for k in C1_[::-1]]
    C2 = [k for k in C2_]
    C3 = [k for k in C3_[::-1]]
    C4 = [k for k in C4_]
    C5 = [k for k in C5_[::-1]]
    C6 = [k for k in C6_]

    graph = {}

    for ns in [R1, R2, R3, C1, C2, C3, C4, C5, C6]:
        for i, n in enumerate(ns):
            if graph.has_key(n):
                try:
                    graph[n].append(ns[i + 1])
                except IndexError:
                    pass
            else:
                graph[n] = []
                try:
                    graph[n].append(ns[i + 1])
                except IndexError:
                    pass
    # print graph
    # raw_input('prompt')
    return graph


class MyQUEUE:  # just an implementation of a queue

    def __init__(self):
        self.holder = []

    def enqueue(self, val):
        self.holder.append(val)

    def dequeue(self):
        val = None
        try:
            val = self.holder[0]
            if len(self.holder) == 1:
                self.holder = []
            else:
                self.holder = self.holder[1:]
        except:
            pass

        return val

    def IsEmpty(self):
        result = False
        if len(self.holder) == 0:
            result = True
        return result


# path_queue = MyQUEUE() # now we make a queue


def BFS(graph, start, end, q):

    temp_path = [start]
    q.enqueue(temp_path)

    while q.IsEmpty() == False:
        tmp_path = q.dequeue()
        last_node = tmp_path[len(tmp_path) - 1]
        # print tmp_path
        if last_node == end:
            #             print "VALID_PATH : ", tmp_path
            # hopefully the shortest TODO: only return one; or return all for
            # further evaluation
            return tmp_path
        for link_node in graph[last_node]:
            if link_node not in tmp_path:
                #new_path = []
                new_path = tmp_path + [link_node]
                q.enqueue(new_path)


def CPD(path):
    rowcnt = 0
    colcnt = 0
    pathline = []
    for i in range(len(path)):
        if i != (len(path) - 1):
            pathline.append(path[i] + path[i + 1])
#     print pathline
    for pathdis in pathline:
        if pathdis in ROW_LETTER:
            rowcnt += 1
        elif pathdis in COLUMN_LETTER:
            colcnt += 1
        else:
            continue
    currentdistance = rowcnt * 150 + colcnt * 250
#     print rowcnt, colcnt
#     print currentdistance
    return currentdistance
