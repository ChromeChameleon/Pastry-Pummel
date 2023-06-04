import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '550,150'

import pgzrun
from pgzhelper import *
from random import *
import math

WIDTH = 800
HEIGHT = 800
uk = 0.001

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
    
    def detect_collision(self):
        actors = [] #should make this a self variable as its required multiple times
        
        for i in range(len(self.players[1].units)): #creates a list of actors of the 2nd team
            actors.append(self.players[1].units[i].actor)
            #actors.append(self.players[0].units[i].actor) #seems to not work
       
        for p1units in (self.players[0].units):
            index = p1units.actor.collidelist_pixel(actors) #returns the index of the collider #actor
            #print(index)
            if index != -1: # -1 means not colliding 0 - onwards is just index of list
                print(p1units,self.players[1].units[index]) #prints the coords of first penguin, and #coords of second penguin
                p1units.collision_calc(self.players[1].units[index]) # passes the second unit collided into the collision calc
                                                                    # method of the first
#             except: #for testing purposes as to not crash the code for no reason
#                 print('error')

      
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
            self.units.append(Unit(xpos, ypos, 40, 'penguinoes',f"{self.team}penguin{i}"))
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
    angle:
    launch_dir:
    mass
    radius
    colour
    name: Str value to identify the unit 

    '''
    def __init__(self, x, y, mass, actor,name):
        self.name = name
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
    
    def __repr__(self):
        return self.name
    
    def move(self):
        '''
        moves the units coordinates by its current x and y velocities
        '''
        self.x += self.vx
        self.y += self.vy
        self.actor.x = self.x
        self.actor.y = self.y
       # print(self.x, self.y, self.actor.x, self.actor.y)
    
    def update_v(self, vx, vy):
        '''
        sets the x and y velocities of the unit to the given values,
        then finds the launch angle. It then makes a list which stores if the initial
        x and y launch velocities are positive or negative
        
        Parameters
        ----------
        vx: float
            the x velocity to set
        vy: float
            the y velocity to set
        '''
        self.vx = vx
        self.vy = vy
        
        self.angle = abs((math.atan(self.vy/self.vx)))
        print(self.angle)
        self.launch_dir = ['',''] #[xdirection, ydirection]
        if self.vx > 0:
            self.launch_dir[0] = '+'
        elif self.vx < 0:
            self.launch_dir[0] = '-'
        if self.vy > 0:
            self.launch_dir[1] = '+'
        elif self.vy > 0:
            self.launch_dir[1] = '-'
        #print(self.launch_dir)
        
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
#         print(self.vx,self.vy)
#         print(m2.vx,m2.vy)

    def acceleration(self):
        '''
        calculates the magnitude of acceleration and calculates the x and y
        components. It then adds or subtracts the x and y acceleration components
        to bring the x and y velocity components down to 0.
        
        '''
        #fnet = ma, -Ff = ma, -ukFn = ma, -ukFg = ma, -ukmg = ma, -ukg = a
        acc = uk * 9.8
        #print(self.angle)
        accx = acc * math.cos(self.angle) #calculates components
        accy = acc * math.sin(self.angle)
        #print(accx,accy)
        if self.vx > 0: #if vx is positive
            if self.launch_dir[0] == '+': # is true if vx should be positive
                self.vx -= accx
            else:
                self.vx = 0 # makes it stay at 0 once it reaches it
        elif self.vx < 0: #if vx is negative
            if self.launch_dir[0] == '-': # is true if vx should be negative
                self.vx += accx
            else:
                self.vx = 0 # makes it stay at 0 once it reaches it
            
        if self.vy > 0: #if vy is positive
            if self.launch_dir[1] == '+': # is true if vy should be positive
                self.vy -= accy
            else:
                self.vy = 0 # makes it stay at 0 once it reaches it
        elif self.vy < 0: #if vy is negative
            if self.launch_dir[0] == '-': # is true if vy should be negative
                self.vy += accy
            else:
                self.vy = 0 # makes it stay at 0 once it reaches it
        #print(self.vx,self.vy)


#u1 = Unit(WIDTH/2, HEIGHT/2, 40, 'penguinoes')
#p1 = Player("red")
#p1.make_team(4)
admin = Driver()
admin.setupPlayers()

#sets velocities of each unit (this is for testing only)
for players in admin.players:
        for unit in players.units:
            if players.team == "p1":
                unit.update_v(2,2)
            else:
                unit.update_v(-2,2)

def draw():
    screen.clear()
    screen.fill((50,100,150))
    for players in admin.players:
        for unit in players.units:
            unit.actor.draw()
            
def update():
    

    for players in admin.players:
        for unit in players.units:
#             if players.team == "p1":
#                 unit.update_v(5,0)
#             else:
#                 unit.update_v(-5,0)
            unit.move()
            unit.acceleration()
            #unit.move(randint(-10,10),randint(-10,10))

    admin.detect_collision()
    #for unit in p1.units:
        #x = randint(-10,10)
        #y = randint(-10,10)
        #unit.move(x,y)

pgzrun.go()
