#!/usr/bin/env python
# ----------------------------------------------------------------------------
# bugs in a box eating each other mimicking a coalescent sequence
# call with 1 argument the number of bugs in the box
# Peter Beerli (c) 2011
# based on a the noisy.py demo in pyglet.
#
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
# modified by Peter Beerli 2011

'''Bounces balls around a window and plays noises when other ball are met, when balls come near
each other one get swallowed, in analogy to a coalescent process.

This is a simple demonstration of how pyglet efficiently manages many sound
channels without intervention.
'''

import os
import random
import sys
from scipy import *

from pyglet.gl import *
import pyglet
from pyglet.window import key
import time 

BALL_IMAGE = 'tigerbeetle2.png'
BALL_SOUND = 'ball.wav'
MINDISTANCE= 100.0
HUGE = 9999.0
GROW = 100
SHRINK = -100
helper = False
masterscale = 1.0
elapsed = 0.0

if len(sys.argv) > 2:
    BALL_SOUND = sys.argv[2]

sound = pyglet.resource.media(BALL_SOUND, streaming=False)


def rect(r, w, deg=0):				# radian if deg=0; degree if deg=1
    from math import cos, sin, pi
    if deg:
       w = pi * w / 180.0
    return r * cos(w), r * sin(w)

class Population():
    width = 100
    height = 70
    x = 0
    y = 0
    start = False
    
    def __init__(self,window):
        self.width = window.width-200
        self.height = window.height-200
        self.x = 100
        self.y = 100
        start = False

    def draw(self):
        draw_rect(self.x,self.y,self.width,self.height)
        
    def update(self,growvalue):
        self.width = self.width + growvalue
        self.height = self.height +growvalue
        self.x = self.x - growvalue//2
        self.y = self.y - growvalue//2
        

class Ball(pyglet.sprite.Sprite):
    ball_image = pyglet.resource.image(BALL_IMAGE)
    ball_image.anchor_x = ball_image.width/2
    ball_image.anchor_y = ball_image.width/2
    width = ball_image.width
    height = ball_image.height
    
    def __init__(self):
        x0 = population.x + self.width // 2
        y0 = population.y + self.width // 2
        x = x0 + random.random() * (population.width - self.width)
        y = y0 + random.random() * (population.height - self.height)
	d = math.sqrt((x-x0)**2 + (y-y0)**2)
        #x = 1000.0/d * x
	#y = 1000.0/d * y
#	print d
        super(Ball, self).__init__(self.ball_image, x, y, batch=balls_batch)
        self.scale=masterscale
#        self.dx = (random.random() - 0.5) * 1000
#        self.dy = (random.random() - 0.5) * 1000
        self.dx,self.dy = rect(500.0,(random.uniform(-pi,pi)))
#	print self.dx
#	print self.dy 
        self.diff = 0.0
        self.rotation = -math.degrees(math.atan2(random.random()-0.5 , random.random()-0.5))



    def update(self, dt):
        if population.start == True:
            x0 = population.x + self.width // 2
            y0 = population.y + self.width // 2
            if self.x <= x0 or self.x + self.width >= x0 + population.width:
                self.dx *= -1
            if self.y <= y0 or self.y + self.height >= y0 + population.height:
                self.dy *= -1
            oldx = self.x
            oldy = self.y
#            if self.diff<-100. or self.diff > 100.:
#                self.diff = -self.diff
#            self.diff += 0.5
#            self.dx += self.diff
#            self.dy -= self.diff
            
            self.x += self.dx * dt
            self.y += self.dy * dt

            self.x = min(max(self.x, x0), x0 + population.width - self.width)
            self.y = min(max(self.y, y0), y0 + population.height - self.height)
            self.rotation = -math.degrees(math.atan2(oldy-self.y , oldx-self.x))
        return (self.x,self.y)

#window = pyglet.window.Window(800, 600)
window = pyglet.window.Window(fullscreen=True)
population = Population(window)

def displayhelp():
    te  = "H         display/undisplay this help\n"
    te += "Enter     start animation\n"
    te += "R         restart animation\n"
    te += "Escape    quit applciation\n"
    te += "Space     increase box size\n"
    te += "Backspace decrease box size\n"
    te += "S         reduce the size of bugs\n"
    te += "I         increase the size of bugs\n"
    te += "A         add bugs\n"
    te += "D         delete bugs\n"
#    print te
    helplabel.text=te

@window.event
def on_key_press(symbol, modifiers):
    global starttime
    global helper
#
    if symbol == key.H:
       if not(helper):
           helper=True
           displayhelp()
       else:
	   helper=False
	   helplabel.text=""
    elif symbol == key.SPACE:
        population.update(GROW)
    elif symbol == key.BACKSPACE:
        population.update(SHRINK)
    elif symbol == key.S:
	masterscale = balls[0].scale * 0.98
    	for i in balls:
	  i.scale = masterscale
    elif symbol == key.I:
	masterscale = balls[0].scale * 1.02	
    	for i in balls:
	  i.scale = masterscale
    elif symbol == key.A:
        balls.append(Ball())
    elif symbol == key.D:
        if balls:
            del balls[-1]
    elif symbol == key.ENTER:
#        print population.start
        starttime = time.time()
        population.start = not(population.start)
    elif symbol == key.R:
        if timescale:
            del timescale[:]
        if balls:
            del balls[:]
        if len(sys.argv) > 1:
            sample = sys.argv[1]
        else:
            sample = 100
        for i in xrange(0,int(sample)):
            balls.append(Ball())
        label2.text = 'k='+str(sample)
        label3.text = "Time:%6i\nLast:%6i" % (0,0)
	#helplabel.text = ""
        starttime = time.time()
        population.start = False
    elif symbol == key.ESCAPE:
        window.has_exit = True

@window.event
def on_draw():
    window.clear()
    population.draw()
    balls_batch.draw()
    label.draw()
    label2.draw()
    label3.draw()
    helplabel.draw()
    draw_timeintervals()

def update(dt):
    if population.start:
        tim = int(time.time() - starttime)
        label3.text = "Time:%6i\nLast:%6i" % (tim, int(elapsed))	
        c=[]
        for ball in balls:
            c.append(ball.update(dt))
        if(len(c)>1):
            dd=distance(c)
            id=coalesce(balls,dd,MINDISTANCE*balls[0].scale)
            if id>= 0:
                del(balls[id]) 	

def distance(c):
    cc = array(c)
    x = cc[:,0]
    y = cc[:,1]
    d = array(zeros((len(x),len(x)), dtype=float))
    for i in xrange(0,len(x)):
    	for j in xrange(i+1,len(x)):
            d1 = x[i] - x[j]
            d2 = y[i] - y[j]
            td = math.sqrt(d1*d1+d2*d2)
            d[i,j] = td
            d[j,i] = td
	d[i,i] = HUGE
    return d

def coalesce(sample,distance,mindistance):
    global starttime
    global timescale
    global elapsed
    x = argmin(distance, axis=None)
    dims = distance.shape
    idx = unravel_index(x, dims)
    if(distance[idx[0],idx[1]]<mindistance):
        #delete(sample,idx[1],0)
	sound.play()
        label2.text = "k: "+str(len(balls)-1)
        t = time.time()-starttime
	elapsed = int(t)
        label3.text = "Time:%6i\nLast:%6i" % (elapsed, elapsed)
        timescale.append(float(t))
	return idx[1]
    else:
	return -1	

def draw_rect(x, y, width, height):
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def draw_timeintervals():
    global timescale
    xs = window.width // 5
    xe = window.width - xs
    xwidth = xe - xs
    y = window.height - window.height // 15
    s = array(timescale)
    draw_rect(xs,y,xwidth,60)
    if len(s) > 0:
        sss = s[-1]
        ss =  sss * ones(len(s), float)
        timescale_adj = s / ss 
#        print ss,timescale_adj
        for i in timescale_adj:
            draw_rect(xs+i*xwidth, y, 1, 60)
        
pyglet.clock.schedule_interval(update, 1/30.)

balls_batch = pyglet.graphics.Batch()
balls = []
starttime = time.time()
timescale=[]


if len(sys.argv) > 1:
   for i in xrange(0,int(sys.argv[1])):
       balls.append(Ball())
else:
   for i in xrange(0,int(100)):
       balls.append(Ball())
    
label = pyglet.text.Label('Press H for the help menu',
                          font_size=20                     ,
                          x=window.width // 2, y=10, 
                          anchor_x='center')
label2 = pyglet.text.Label("k: "+str(len(balls)),
                           font_size=50,
                           x=window.width - window.width // 10, y=window.height - window.height // 15, 
                           anchor_x='center')
label3 = pyglet.text.Label("Time: "+str(0),
                           font_size=20,multiline=True,width=200,
                           x=window.width // 10, y=window.height - window.height // 20, 
                           anchor_x='center')
helplabel = pyglet.text.Label("",
                           font_size=20,multiline=True,width=800,
                           x=window.width // 10, y=window.height - window.height // 6, 
                           anchor_x='left')

if __name__ == '__main__':
   pyglet.app.run()
