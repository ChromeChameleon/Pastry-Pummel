import pgzrun
from pgzhelper import *
import random
import math

WIDTH = 800
HEIGHT = 800

class Driver():
    def __init__(self):
        self.players = []
    
    def make_team(self):
        pass
        
class Player():
    """the player itself"""
    
    def __init__(self,team):
        self.team = team #team eg player 1 or 2
        self.units = [] # list of unit objects
    
    def make_team(self, units):
        for i in range(units):
            self.units.append(Unit(WIDTH/2, HEIGHT/2, 40, 'penguinoes'))
#             penguinoes = Actor("penguinoes") #to be changed, but its just which picture
#             coords = Unit(100,100) #coords of this actor
#             self.units.append([penguinoes,coords]) 

class Unit():
    '''
    Attributes
    ----------
    x:
    y:
    vx:
    vy:
    mass
    radius
    colour
    '''
    def __init__(self, x, y, mass, actor):
        self.x = x
        self.y = y
        self.mass = mass
        self.actor = Actor(actor)
        self.actor.x = self.x
        self.actor.y = self.y
        self.vx = 0
        self.vy = 0
        self.linex = x
        self.liney = y
        self.pos_vect = self.x, HEIGHT - self.y
        self.pos_angle = math.degrees(math.atan(self.pos_vect[1] / self.pos_vect[0]))
        self.line_vect = (0, 0)
        self.active_arrow = False
        
    def is_clicked():
        print('hi')
    
    def update_pos_vect(self):
        self.pos_vect = (self.x, HEIGHT - self.y)
        self.pos_angle = math.degrees(math.atan(self.pos_vect[1] / self.pos_vect[0]))
        self.line_vect = self.linex - self.x, HEIGHT - self.liney - self.y
        #print(self.line_vect)
        #self.line_vect = 
#         self.radius = radius
#         self.colour = colour
    def move(self, x, y):
        self.x += x
        self.y += y
        self.actor.x = self.x
        self.actor.y = self.y
        #print(self.x, self.y, self.actor.x, self.actor.y)
    
    def update_v(vx,vy):
        self.vx = vx
        self.vy = vy

u1 = Unit(WIDTH/2, HEIGHT/2, 40, 'penguinoes')

def draw():
    screen.clear()
    screen.fill((50,100,150))
    screen.draw.line((u1.x, u1.y), (u1.linex, u1.liney), (50, 50, 50))
    u1.actor.draw()

def update():
    #print(u1.pos_vect, u1.pos_angle)
    u1.update_pos_vect()
    u1.move(1,1)

def on_mouse_down(pos):
    if u1.actor.collidepoint(pos):
        u1.active_arrow = True

def on_mouse_up(pos, button):
    u1.active_arrow = False

def on_mouse_move(pos, rel, buttons):
    if mouse.LEFT in buttons and u1.active_arrow:
        u1.linex = pos[0]
        u1.liney = pos[1]
        #u1.update_pos_vect()
        #print(pos[0], pos[1])

pgzrun.go()
