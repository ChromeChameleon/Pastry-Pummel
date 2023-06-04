import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '550,150'

import pgzrun
from pgzhelper import *
from random import *
import math

WIDTH = 800
HEIGHT = 800
uk = 0.0008
max_arr_len = 200

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
                #print(units,colliders[index]) #prints the coords of first penguin, and #coords of second penguin
                units.collision_calc(colliders[index]) # passes the second unit collided into the collision calc
            
            #removes items as to prevent collisions with itself
            if len(colliders) != 0:
                colliders.pop(0) 
                collactors.pop(0)
             
#             except: #for testing purposes as to not crash the code for no reason
#                 print('error')

      
class Player():
    """the player itself
    
    Attributes
    -------------
    team: Str that represents which team the player is on
    units: a List that represents every unit that belongs to the player
    """
    
    def __init__(self,team):
        self.team = team #team eg player 1 or 2
        self.units = [] # list of unit objects
        self.ready_launch = False
       
    def make_team(self, units,starting_pos):
        """takes the # of units and their starting positions and creates a team of units"""
        xpos = starting_pos
        ypos = 100
        for i in range(units):
            self.units.append(Unit(xpos, ypos, 40, 'cookie',f"{self.team}cookie{i}"))
            ypos += 150
    
    def launch(self):
        '''
        Detects to see if the line vector magnitude is greater than zero and if the player is ready to launch
        '''
        #print(self.ready_launch)
        for unit in self.units:
            if unit.mag_line_vect < 25:           #Set a proper boundary in the future
                self.ready_launch = False
                return self.ready_launch
        if keyboard.SPACE:                            #Change to a button in the future - keyboard.SPACE is temporary
            self.ready_launch = True

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
        self.actor.x = self.x
        self.actor.y = self.y 
        self.vx = 0
        self.vy = 0
#         self.radius = radius
#         self.colour = colour

        self.linex = x
        self.liney = y
        self.pos_vect = self.x, self.y
        self.line_vect = (0, 0)
        self.mag_line_vect = 0
        self.active_arrow = False
        
    def __repr__(self):
        return self.name
    
    def update_vector(self):
        '''Updates the vector components

        Variables
        ---------
        pos_vect:
            Stores position vector component of penguin
        line_vect:
            Stores the vector component of the line relative to the penguin's position vector
        mag_line_vect:
            Stores the magnitude of the line vector
        '''
        self.pos_vect = (self.x, self.y)
        self.line_vect = (self.linex - self.x), (self.y - self.liney)
        self.mag_line_vect = math.sqrt(self.line_vect[0]**2 + self.line_vect[1]**2)
        #print(self.line_vect)
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
        
        if self.vx != 0: # prevents division by zero error
            self.angle = abs((math.atan(self.vy/self.vx))) #Radians
        else:
            self.angle = math.pi/2 #sets angle to pi/2 (90 deg) when vx = 0
            print('hi')
        #print(self.angle)
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

class Board():
    """the game board
    Board that shrinks every round
    """
    def __init__(self,width,height,shrink_rate):
        self.topx = 0
        self.topy = 0
        self.width = width
        self.height = height
        self.shrink_rate = shrink_rate
        self.board = None
        self.actor = Actor("square",(WIDTH//2,HEIGHT//2))
    def shrink_board(self):
        if self.actor.scale >= 0.1:
            self.actor.scale *= self.shrink_rate
        

#u1 = Unit(WIDTH/2, HEIGHT/2, 40, 'penguinoes')
#p1 = Player("red")
#p1.make_team(4)

admin = Driver()
admin.setupPlayers()

"""TEMP BOARD"""
board = Board(0,0,0.9) #width, height,shrink rate (only last one matters)

#sets velocities of each unit (this is for testing only)
for players in admin.players:
        for unit in players.units:
            if players.team == "p1":
                unit.update_v(2,2)
            else:
                unit.update_v(-2,2)

def on_mouse_down(pos):
    "Turns active_arrow True if mouse is held down and if mouse position is colliding with unit"
    for unit in admin.players[0].units:
        if unit.actor.collidepoint(pos):
            unit.active_arrow = True

def on_mouse_up(pos, button):
    "Turns active_arrow False if mouse is lifted up"
    for unit in admin.players[0].units:
        unit.active_arrow = False
        
def on_mouse_move(pos, rel, buttons):
    "Changes position of line vector if left click + active_arrow is True"
    for unit in admin.players[0].units:
        mouse_vect = (pos[0] - unit.x, unit.y - pos[1])
        mag_mouse_vect = math.sqrt(mouse_vect[0]**2 + mouse_vect[1]**2)
        if mag_mouse_vect > max_arr_len:
            factor = max_arr_len / mag_mouse_vect
        else:
            factor = 1
        if mouse.LEFT in buttons and unit.active_arrow:
            unit.linex = unit.x + ((pos[0] - unit.x) * factor)
            unit.liney = unit.y + ((pos[1] - unit.y) * factor)
            
time = 0
def draw():
    global turns,time

    screen.clear()
    screen.fill((50,100,150))
    
    board.actor.draw()
    if time/60 >= 1:
        board.shrink_board()
        time = 0
    """
    board = Rect((0+(SHRINK_CONSTANT/2)*turns,0+(SHRINK_CONSTANT/2)*turns,
                  WIDTH - SHRINK_CONSTANT*turns,HEIGHT - SHRINK_CONSTANT*turns))#left,top,width,height
            #moves the board left and down by multiplying the shrink constant by the number of turns,
            #it is divided by two to keep it centered. The width and height are then subtracted by the
            #shrink constant multiplied by the turns.
    screen.draw.filled_rect(board,(255,255,255))
    """
    for unit in admin.players[0].units:
        screen.draw.line((unit.actor.x, unit.actor.y), (unit.linex, unit.liney), (50, 50, 50))
    for players in admin.players:
        for unit in players.units:
            unit.actor.draw()
            """
    turns += 1 #for testing
    """
    time += 1

def update():
    
    for players in admin.players:
        players.launch()
        for unit in players.units:
#             if players.team == "p1":
#                 unit.update_v(5,0)
#             else:
#                 unit.update_v(-5,0)
            #unit.move()
            unit.acceleration()
            #unit.move(randint(-10,10),randint(-10,10))

    admin.detect_collision()
    for unit in admin.players[0].units:
        unit.update_vector()
    #for unit in p1.units:
        #x = randint(-10,10)
        #y = randint(-10,10)
        #unit.move(x,y)

pgzrun.go()
