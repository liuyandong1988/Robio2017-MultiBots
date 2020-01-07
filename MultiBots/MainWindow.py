#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import WorldController
import random
from param import *
import wx.gizmos as gizmos
import Graph
import math

REFRESH_INTERVAL = 50


class PaintWindow(wx.Window):

    def __init__(self, parent, myId):
        # setup window
        wx.Window.__init__(self, parent, myId)
        # setup painter
        self.SetBackgroundColour("Black")  # window背景颜色
        self.pen = wx.Pen("??")  # instance 画笔属性
        self.brush = wx.Brush("??")  # 填充色块属性
        self.timeToCount = 0  # 累计秒数
        self.led = gizmos.LEDNumberCtrl(
            self, -1, (25, 5), (248, 50), gizmos.LED_ALIGN_CENTER)
        self.led.SetBackgroundColour("black")
        self.led.SetForegroundColour("red")
        # setup timer
        self.controller = WorldController.Controller()
        self.timer = wx.Timer(self)  # 创建定时器
        self.Bind(wx.EVT_TIMER, self.update, self.timer)  # 绑定处理事件self.update
        self.timer.Start(REFRESH_INTERVAL)  # 间隔REFRESH_INTERVAL=50毫秒刷新

    def updateBuffer(self):
        size = self.GetClientSize()  # 获取client窗口大小
        self.buffer = wx.EmptyBitmap(size.width, size.height)  # 创建缓存设备的上下文
        self.dc = wx.BufferedDC(None, self.buffer)
        self.dc.SetBackground(wx.Brush(self.GetBackgroundColour()))  # 使用上下文
        self.dc.Clear()

        self.drawGround()
        self.drawstartPoints()
        self.drawchargePoints()
        self.drawendPoints()
        self.drawGoods()
        self.drawCarboxes()
        self.drawAgents()
        self.dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)  # wxpython 4.0.4
    #         self.dc = wx.BufferedPaintDC(None, self.buffer) # wxpython 2

    def drawGround(self):
        # draw the warehouse
        self.pen.SetWidth(2)
        self.pen.Colour = "White"
        self.dc.SetPen(self.pen)
        self.dc.DrawLine(
            margin_left, margin_top, margin_left, world_height - margin_bottom)
        self.dc.DrawLine(
            margin_left, margin_top, world_width - margin_right, margin_top)
        self.dc.DrawLine(world_width - margin_right, margin_top,
                         world_width - margin_right, world_height - margin_bottom)
        self.dc.DrawLine(margin_left, world_height - margin_bottom,
                         world_width - margin_right, world_height - margin_bottom)

    def drawGoods(self):
        for g in self.controller.goods:
            self.drawGood(g)

    def drawGood(self, good):
        self.pen.Colour = "red"
        self.pen.SetWidth(2)
        self.dc.SetPen(self.pen)
        if good.status == 0:
            self.dc.SetBrush(wx.Brush("black", wx.SOLID))
        else:
            self.dc.SetBrush(wx.Brush("red", wx.SOLID))
        self.dc.DrawRectangle(good.x, good.y, L, L)

    def drawCarboxes(self):
        for c in self.controller.boxes:
            self.drawbox(c)

    def drawbox(self, box):
        self.pen.Colour = "black"
        self.pen.SetWidth(1)
        self.dc.SetPen(self.pen)
        if box.status == 0:
            self.dc.SetBrush(wx.Brush("black", wx.SOLID))
        else:
            self.dc.SetBrush(wx.Brush("red", wx.SOLID))
        self.dc.DrawRectangle(box.x, box.y, int(L / 3), int(L / 3))

    def drawAgents(self):
        for i in self.controller.agents:
            self.drawAgent(i)

    def drawAgent(self, agent):
        self.brush.SetStyle(wx.SOLID)
        if agent.color == 0:  # idle
            self.brush.SetColour("Green")
        elif agent.color == 1:  # moving to good
            self.brush.SetColour("Blue")
        elif agent.color == 2:  # carrying good
            self.brush.SetColour("Red")
        elif agent.color == 3:  # dead
            self.brush.SetColour("Black")
        elif agent.color == 4:  # charging
            self.brush.SetColour("Orange")
        self.pen.Colour = "Yellow"
        self.pen.SetWidth(1)
        self.dc.SetPen(self.pen)
        self.dc.SetBrush(self.brush)
        self.dc.DrawCircle(agent.x, agent.y, agent.r)
        self.dc.DrawLine(agent.x, agent.y,
                         agent.x + agent.r * agent.angle.cos(),
                         agent.y - agent.r * agent.angle.sin())

        # draw battery
        if agent.batterystatus == 1:
            self.brush.SetColour("Green")
            self.pen.Colour = "Green"

        elif agent.batterystatus == 2:
            self.brush.SetColour("Orange")
            self.pen.Colour = "Orange"

        elif agent.batterystatus == 3:
            self.brush.SetColour("red")
            self.pen.Colour = "red"

        self.pen.SetWidth(1)
        self.dc.SetPen(self.pen)
        self.brush.SetStyle(wx.SOLID)
        self.dc.SetBrush(self.brush)

        if agent.angle.theta == 90 or agent.angle.theta == -90:
            self.dc.DrawRectangle(
                agent.x + 2 * agent.r * agent.batteryangle2.cos(),
                agent.y - 3 * agent.r * agent.batteryangle2.sin(),
                agent.batterypos,  agent.width)
        elif agent.angle.theta == 0 or agent.angle.theta == 180:
            self.dc.DrawRectangle(
                agent.x + 3 * agent.r * agent.batteryangle2.cos(),
                agent.y - 2 * agent.r * agent.batteryangle2.sin(),
                agent.width, agent.batterypos)

            # add battery bar
        self.pen.Colour = "White"
        self.pen.SetWidth(2)
        self.dc.SetPen(self.pen)
        if agent.angle.theta == 90 or agent.angle.theta == -90:
            self.dc.DrawLine(
                agent.x + 2 * agent.r * agent.batteryangle1.cos(),
                agent.y - 3 * agent.r * agent.batteryangle1.sin(),
                agent.x + 2 * agent.r * agent.batteryangle2.cos(),
                agent.y - 3 * agent.r * agent.batteryangle2.sin())

            self.dc.DrawLine(
                agent.x + 2 * agent.r * agent.batteryangle1.cos(),
                agent.y - 2 * agent.r * agent.batteryangle1.sin(),
                agent.x + 2 * agent.r * agent.batteryangle2.cos(),
                agent.y - 2 * agent.r * agent.batteryangle2.sin())

            self.dc.DrawLine(
                agent.x + 2 * agent.r * agent.batteryangle1.cos(),
                agent.y - 3 * agent.r * agent.batteryangle1.sin(),
                agent.x + 2 * agent.r * agent.batteryangle1.cos(),
                agent.y - 2 * agent.r * agent.batteryangle1.sin())

            self.dc.DrawLine(
                agent.x + 2 * agent.r * agent.batteryangle2.cos(),
                agent.y - 3 * agent.r * agent.batteryangle2.sin(),
                agent.x + 2 * agent.r * agent.batteryangle2.cos(),
                agent.y - 2 * agent.r * agent.batteryangle2.sin())
        elif agent.angle.theta == 0 or agent.angle.theta == 180:
            self.dc.DrawLine(
                agent.x + 3 * agent.r * agent.batteryangle1.cos(),
                agent.y - 2 * agent.r * agent.batteryangle1.sin(),
                agent.x + 3 * agent.r * agent.batteryangle2.cos(),
                agent.y - 2 * agent.r * agent.batteryangle2.sin())

            self.dc.DrawLine(
                agent.x + 2 * agent.r * agent.batteryangle1.cos(),
                agent.y - 2 * agent.r * agent.batteryangle1.sin(),
                agent.x + 2 * agent.r * agent.batteryangle2.cos(),
                agent.y - 2 * agent.r * agent.batteryangle2.sin())

            self.dc.DrawLine(
                agent.x + 3 * agent.r * agent.batteryangle1.cos(),
                agent.y - 2 * agent.r * agent.batteryangle1.sin(),
                agent.x + 2 * agent.r * agent.batteryangle1.cos(),
                agent.y - 2 * agent.r * agent.batteryangle1.sin())

            self.dc.DrawLine(
                agent.x + 3 * agent.r * agent.batteryangle2.cos(),
                agent.y - 2 * agent.r * agent.batteryangle2.sin(),
                agent.x + 2 * agent.r * agent.batteryangle2.cos(),
                agent.y - 2 * agent.r * agent.batteryangle2.sin())

    def drawstartPoints(self):
        for i in self.controller.startPoints:
            self.drawstartPoint(i)

    def drawstartPoint(self, startpoint):
        self.pen.Colour = "Blue"
        self.pen.SetWidth(1)
        self.dc.SetPen(self.pen)

        self.brush.SetStyle(wx.SOLID)
        self.brush.SetColour("Black")
        self.dc.SetBrush(self.brush)
        self.dc.DrawCircle(
            startpoint.x, startpoint.y, startpoint.r)

        x1 = startpoint.x + startpoint.r * math.cos(45 * math.pi / 180.0)
        y1 = startpoint.y + startpoint.r * math.sin(45 * math.pi / 180.0)
        x2 = startpoint.x - startpoint.r * math.cos(45 * math.pi / 180.0)
        y2 = startpoint.y - startpoint.r * math.sin(45 * math.pi / 180.0)
        x3 = startpoint.x - startpoint.r * math.cos(45 * math.pi / 180.0)
        y3 = startpoint.y + startpoint.r * math.sin(45 * math.pi / 180.0)
        x4 = startpoint.x + startpoint.r * math.cos(45 * math.pi / 180.0)
        y4 = startpoint.y - startpoint.r * math.sin(45 * math.pi / 180.0)

        self.dc.DrawLine(x1, y1, x2, y2)
        self.dc.DrawLine(x3, y3, x4, y4)

    def drawendPoints(self):
        for i in self.controller.endPoints:
            self.drawendPoint(i)

    def drawendPoint(self, endpoints):
        self.pen.Colour = "Red"
        self.pen.SetWidth(1)
        self.dc.SetPen(self.pen)

        self.brush.SetStyle(wx.SOLID)
        self.brush.SetColour("Black")
        self.dc.SetBrush(self.brush)

        self.dc.DrawCircle(endpoints.x, endpoints.y, endpoints.r)
        self.dc.DrawCircle(endpoints.x, endpoints.y, endpoints.r / 2)

    def drawchargePoints(self):
        for i in self.controller.chargePoints:
            self.drawchargePoint(i)

    def drawchargePoint(self, chargepoint):
        self.pen.Colour = "Green"
        self.pen.SetWidth(1)
        self.dc.SetPen(self.pen)

        self.brush.SetStyle(wx.SOLID)
        self.brush.SetColour("Black")
        self.dc.SetBrush(self.brush)
        self.dc.DrawCircle(
            chargepoint.x, chargepoint.y, chargepoint.r)

        x1 = chargepoint.x + chargepoint.r * math.cos(45 * math.pi / 180.0)
        y1 = chargepoint.y + chargepoint.r * math.sin(45 * math.pi / 180.0)
        x2 = chargepoint.x - chargepoint.r * math.cos(45 * math.pi / 180.0)
        y2 = chargepoint.y - chargepoint.r * math.sin(45 * math.pi / 180.0)
        x3 = chargepoint.x - chargepoint.r * math.cos(45 * math.pi / 180.0)
        y3 = chargepoint.y + chargepoint.r * math.sin(45 * math.pi / 180.0)
        x4 = chargepoint.x + chargepoint.r * math.cos(45 * math.pi / 180.0)
        y4 = chargepoint.y - chargepoint.r * math.sin(45 * math.pi / 180.0)
        self.dc.DrawLine(x1, y1, x3, y3)
        self.dc.DrawLine(x1, y1, x4, y4)
        self.dc.DrawLine(x2, y2, x3, y3)
        self.dc.DrawLine(x2, y2, x4, y4)

    def OnTimer(self):  # 显示时间事件处理函数
        if WorldController.timer_stop == 0:
            self.timeToCount += 1
#         else:
#             # print 'collision waitting time ==>>',
#             # WorldController.collisioncnt
#             raw_input('haha')
        second = self.timeToCount / 20
        st = "%04d" % (second)
        self.led.SetValue(st)

    def update(self, event):
        self.OnTimer()
        self.updateBuffer()
        self.controller.update()  # 定时器绑定的更新事件


class PaintFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(
            self, parent, -1, "Quad", size=(world_width, world_height))
        self.paint = PaintWindow(self, -1)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = PaintFrame(None)
    frame.SetPosition((66, 0))
    frame.Show(True)
    app.MainLoop()
