#nathans code
import pgzrun
from pgzhelper import *
from random import *

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
    def arrange(self):
        pass #test
        
    def make_team(self, units):
        xpos = 100
        ypos = 100
        for i in range(units):
            self.units.append(Unit(xpos, ypos, 40, 'penguinoes'))
            ypos += 150
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
#         self.radius = radius
#         self.colour = colour
    def move(self,x,y):
        self.x += x
        self.y += y
        self.actor.x = self.x
        self.actor.y = self.y
       # print(self.x, self.y, self.actor.x, self.actor.y)
    
    def update_v(vx,vy):
        self.vx = vx
        self.vy = vy

u1 = Unit(WIDTH/2, HEIGHT/2, 40, 'penguinoes')
p1 = Player("red")
p1.make_team(4)
def draw():
    screen.clear()
    screen.fill((50,100,150))
    for unit in p1.units:
        unit.actor.draw()
        
def update():
    pass
    
    #for unit in p1.units:
        #x = randint(-10,10)
        #y = randint(-10,10)
        #unit.move(x,y)

pgzrun.go()

