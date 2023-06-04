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
    
    def detect_collision(self):
        actors = [] #should make this a self variable as its required multiple times
       
        #list of all teams
        #second list where values are removed
        for i in range(len(self.players[0].units)): #creates a list of actors of the 2nd team
            actors.append(self.players[0].units[i])
        
        for i in range(len(self.players[1].units)): #creates a list of actors of the 2nd team
            actors.append(self.players[1].units[i])
        
        colliders = actors.copy() #a list of units of both teams
        colliders.pop(0) # removes the first item in the list to prevent collidng with itself
        collactors = [] # list of actors of those units
        
        #creates actors list from the unit list
        for unit in colliders:
            collactors.append(unit.actor)
        
        for units in actors: 
            index = units.actor.collidelist_pixel(collactors) #returns the index of the collider #actor
            if index != -1: # -1 means not colliding 0 - onwards is just index of list
                print(units,colliders[index]) #prints the coords of first penguin, and #coords of second penguin
                units.collision_calc(colliders[index]) # passes the second unit collided into the collision calc
            
            #removes items as to rpevent collsions with itself
            if len(colliders) != 0:
                colliders.pop(0) 
                collactors.pop(0)
             
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
        
       # print(self.x, self.y, self.actor.x, self.actor.y)
        #if self.x >= WIDTH or self.x <= 0:
           # self.x = randint(200,600)
        #if self.y >= HEIGHT or self.y <= 0:
            #self.y = randint(200,600)
        
        self.actor.x = self.x
        self.actor.y = self.y
    def update_v(self, vx, vy):
        '''
        sets the x and y velocities of the unit to the given values
        
        Parameters
        ----------
        vx: float
            the x velocity to set
        vy: float
            the y velocity to set
        '''
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
#         print(self.vx,self.vy)
#         print(m2.vx,m2.vy)

admin = Driver()
admin.setupPlayers()

#sets velocities of each unit (this is for testing only)
for players in admin.players:
        for unit in players.units:
            if players.team == "p1":
                unit.update_v(randint(-2,2),randint(-2,2))
            else:
                unit.update_v(randint(-2,2),randint(-2,2))

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
            #unit.move(randint(-10,10),randint(-10,10))

    admin.detect_collision()
    #for unit in p1.units:
        #x = randint(-10,10)
        #y = randint(-10,10)
        #unit.move(x,y)

pgzrun.go()
