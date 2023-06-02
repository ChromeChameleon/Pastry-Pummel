import pgzrun
from pgzhelper import *
from random import *

WIDTH = 800
HEIGHT = 800

class Driver():
    def __init__(self):
        self.players = []
    
    def setupPlayers(self):
        starting_pos = 100 #yes ik very scuffed will be changed later
        for i in range(1,3): #two players as I don't want to go insane
            p = Player(f"p{i}")
            p.make_team(4,starting_pos) #creates 4 units
            self.players.append(p)
            starting_pos = WIDTH - starting_pos #insane math
    
class Player():
    """the player itself
    
    Attrtibutes
    -------------
    team: Str that represents which team the player is on
    units: a List that represents every unit that belongs to the player
    """
    
    def __init__(self,team):
        self.team = team #team eg player 1 or 2
        self.units = [] # list of unit objects
        
    def make_team(self, units,starting_pos):
        """takes the # of units and their starting positions and creates a team of units"""
        xpos = starting_pos
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
    x: Int value that represents the x position of the unit
    y: Int value that represents the y position of the unit
    vx: Int value that represents the x speed of the unit
    vy: Int value that represents the y speed of the unit
    mass
    radius
    colour
    '''
    def __init__(self, x, y, mass, actor):
        self.x = x
        self.y = y
        self.mass = mass
        self.actor = Actor(actor)
#         self.actor.x = self.x
#         self.actor.y = self.y (technically unnessary as you have a move method)
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
    
    def update_v(self, vx,vy):
        self.vx = vx
        self.vy = vy
        
    def collision_calc(self, m2):
        '''
        takes in a another unit object which the unit is colliding with and
        calculates their resultant velocities. It then updates the velocity
        attributes of the units.
        
        Parameters
        ----------
        m2: unit object
            the unit that is being collided with
        '''
        m1mass = self.mass
        m2mass = m2.mass
        #x direction
        v1ix = self.vx
        v2ix = m2.vx
        #set m2 frame of reference
        v1ix -= v2ix
        v2ix = 0
        
        v1fx = v1ix*((m1mass-m2mass)/(m1mass+m2mass))
        v2fx = (2*m1mass*v1ix)/(m1mass+m2mass)
        
        #set back to global f.o.r
        v1fx += m2.vx
        v2fx += m2.vx
        
        
        #y direction
        v1iy = self.vy
        v2iy = m2.vy
        #set m2 frame of reference
        v1iy -= v2iy
        v2iy = 0
        
        v1fy = v1iy*((m1mass-m2mass)/(m1mass+m2mass))
        v2fy = (2*m1mass*v1iy)/(m1mass+m2mass)
        
        #set back to global f.o.r
        v1fy += m2.vy
        v2fy += m2.vy
        
        self.update_v(v1fx,v1fy)
        m2.update_v(v2fx,v2fy)

#u1 = Unit(WIDTH/2, HEIGHT/2, 40, 'penguinoes')
#p1 = Player("red")
#p1.make_team(4)
admin = Driver()
admin.setupPlayers()
def draw():
    screen.clear()
    screen.fill((50,100,150))
    for players in admin.players:
        for unit in players.units:
            unit.actor.draw()
            
def update():
    pass
    for players in admin.players:
        for unit in players.units:
            unit.move(randint(-10,10),randint(-10,10))
    #for unit in p1.units:
        #x = randint(-10,10)
        #y = randint(-10,10)
        #unit.move(x,y)

pgzrun.go()
