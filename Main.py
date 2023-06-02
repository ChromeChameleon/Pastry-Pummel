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
        actors = []
        for i in range(len(self.players[1].units)):
            actors.append(self.players[1].units[i].actor)
      
        for p1units in (self.players[0].units):
            try:
                index = p1units.actor.collidelist_pixel(actors)
                #print(index)
                if index != -1:
                    print(p1units,self.players[1].units[index])
            except:
                pass
            
    
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
    def __repr__(self):
        return f"{self.x},{self.y}"
        
    def move(self,x,y):
        self.x += x
        self.y += y
        self.actor.x = self.x
        self.actor.y = self.y
       # print(self.x, self.y, self.actor.x, self.actor.y)
    
    def update_v(self,vx,vy):
        self.vx = vx
        self.vy = vy
    
  
        

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
    for players in admin.players:
        for unit in players.units:
            if players.team == "p1":
                unit.move(5,0)
            else:
                unit.move(-5,0)
            #unit.move(randint(-10,10),randint(-10,10))
            
    admin.detect_collision()
    
    #for unit in p1.units:
        #x = randint(-10,10)
        #y = randint(-10,10)
        #unit.move(x,y)

pgzrun.go()
