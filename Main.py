import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

import pgzrun
from pgzhelper import *
from random import *
import math

WIDTH = 1200
HEIGHT = 1000
cx = WIDTH // 2 #x coord of centre of screen
cy = HEIGHT // 2 # y coord of centre of screen
uk = 0.01  #coefficient of friction
max_arr_len = 100
powa = 0.1
class Driver():
    def __init__(self):
        self.players = []
        self.actors = []
        self.status = [0]
        self.launch = False
        self.board = ""
        self.cycle = 0          #Used to cycle through turn
        self.checking_key = False
        self.turns = 0
    
    def setupPlayers(self):
        starting_pos = 300 #yes ik very scuffed will be changed later
        for i in range(1,3): #two players as I don't want to go insane
            p = Player(f"p{i}")
            p.make_team(4,starting_pos) #creates 4 units
            self.players.append(p)
            self.status.append(0)
            starting_pos = WIDTH - starting_pos #insane math
        
        #creates the list of all players actors 
        self.setupActors()
    def setupActors(self):
         #list of all teams
        for i in range(len(self.players[0].units)): #creates a list of actors of the 2nd team
            self.actors.append(self.players[0].units[i])
        
        for i in range(len(self.players[1].units)): #creates a list of actors of the 2nd team
            self.actors.append(self.players[1].units[i])
            
    def setupBoard(self,shrink_rate):
        #setsup the game board
        self.board = Board(800,800,shrink_rate)
    
    def start_launch(self):
        self.launch = True
        for player in self.players:
            for unit in player.units:
                unit.launch_power()
    def play_turn(self):
        
        self.start_launch()
        self.turns += 1
                
    def end_turn(self):
        for player in self.players:
            for unit in player.units:
                if not unit.stopped:
                    return False
        return True
    
    def next_turn(self):
        self.cycle = 0
        self.launch = False
        admin.status = [1, 0, 0]
        for player in self.players:
            player.ready_launch = False
            for unit in player.units:
                unit.line_vect = (0, 0)
                unit.mag_line_vect = 0
                unit.active_arrow = False
                unit.linex = unit.x
                unit.liney = unit.y

    
    def shrink(self):
        self.board.shrink_board()
        self.shrink_playerpos()

    def detect_collision(self):
        """
        actors = [] #should make this a self variable as its required multiple times
       
        #list of all teams
        #second list where values are removed
        for i in range(len(self.players[0].units)): #creates a list of actors of the 2nd team
            actors.append(self.players[0].units[i])
        
        for i in range(len(self.players[1].units)): #creates a list of actors of the 2nd team
            actors.append(self.players[1].units[i])
        """
        colliders = self.actors.copy() #a list of units of both teams
        colliders.pop(0) # removes the first item in the list to prevent collidng with itself
        collactors = [] # list of actors of those units
        
        #creates actors list from the unit list
        for unit in colliders:
            collactors.append(unit.actor)
        
        for units in self.actors:
            #cricle_collidepoints -> cricular hitbox that prevents vibrating and glitching however still overlap
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
    def shrink_playerpos(self):
        #changes player position depending on size of board
        #make this relative to the top left corner of the board class
        #the area of the board (800^2): sqrt(64000*90%) = side length of the board after shrinkage (758.9)
        #800 - the side length  = the coordinate of the top left corner
        
        
        #shifts the units pos relative to the distance from the center
        for player in self.players:
            for unit in player.units:
                unit.x = cx - (cx-unit.x)*self.board.shrink_rate #
                unit.y = cy - (cy-unit.y)*self.board.shrink_rate
                
                #shifts units while not launching
                unit.actor.x = unit.x
                unit.actor.y = unit.y
    
    def units_fall(self):
        #detects when the units fall off and handles them
        #edge of board
        #center = cx,cy
        #Left edge = cx - board.width/2 , right edge = cx + board.width/2
        #top edge = cy + board.width/2 , bottom edge = cy - board.width/2
        for player in self.players:
            for unit in player.units:
                #print(self.board.width)
                if unit.x < (cx-self.board.width/2) or unit.x > (cx+self.board.width/2):
                    print(cx-self.board.width/2,cx+self.board.width/2)
                    player.units.remove(unit)
                    del unit
                elif unit.y > (cy+self.board.width/2) or unit.y < (cy-self.board.width/2):
                    print(cy+self.board.width/2,cy-self.board.width/2)
                    player.units.remove(unit)
                    del unit
      
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
        ypos = 200
        for i in range(units):
            self.units.append(Unit(xpos, ypos, 40, 'cookie',f"{self.team}cookie{i}"))
            ypos += 150
    
    def commit(self):
        '''
        Detects to see if the line vector magnitude is greater than zero and if the player is ready to launch
        '''
        #print(admin.status[int(self.team[1])-1])
        for unit in self.units:
            if unit.mag_line_vect < unit.radius:           #Set a proper boundary in the future
                self.ready_launch = False
                return self.ready_launch
        if keyboard.SPACE and admin.status[int(self.team[1])-1] == 1 and not self.ready_launch:                            #Change to a button in the future - keyboard.SPACE is temporary
            print(self.team)
            self.ready_launch = True
            admin.status[int(self.team[1]) - 1] = 2
            
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
    linex: the x position of the units launch line
    liney: the y position of the units launch line
    line_vect: Stores the vector components of the line relative to the unit's position
    mag_line_vect: Stores the magnitude of the line vector
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
        self.radius = 27
#         self.colour = colour

        self.linex = x
        self.liney = y
        self.line_vect = (0, 0)
        self.mag_line_vect = 0
        self.active_arrow = False
        self.stopped = True
        
    def __repr__(self):
        return self.name
    
    def update_line(self):
        '''
        

        Variables
        ---------
        linex,liney:
            the x and y position of the launch line (gets updated in on_mouse_move())
        line_vect:
            Stores the vector components of the line relative to the unit's position
        mag_line_vect:
            Stores the magnitude of the line vector
        '''
        self.line_vect = (self.linex - self.x), (self.liney - self.y)
        self.mag_line_vect = math.sqrt(self.line_vect[0]**2 + self.line_vect[1]**2)
        
        #angle relative to x axis 
        if self.line_vect[0] != 0: # prevents division by zero error
            self.line_angle = abs((math.atan(self.line_vect[1]/self.line_vect[0]))) #Radians
        else:
            self.line_angle = math.pi/2 #sets angle to pi/2 (90 deg) when vx = 0
        
       
        #print(self.line_vect)
    def launch_power(self):
        #self.visible_mag_line = self.mag_line_vect - self.radius #visible magniutude
        if self.mag_line_vect != 0:
            ratio = self.radius / self.mag_line_vect
            x = self.line_vect[0] * (1-ratio) * powa
            y = self.line_vect[1] * (1-ratio) * powa
            self.update_v(x,y)

    def move(self):
        '''
        moves the units coordinates by its current x and y velocities
        '''
        self.x += self.vx
        self.y += self.vy
        
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
        self.stopped = False
        
        if self.vx != 0: # prevents division by zero error
            self.angle = abs((math.atan(self.vy/self.vx))) #Radians
        else:
            self.angle = math.pi/2 #sets angle to pi/2 (90 deg) when vx = 0
            #print('hi')
        #print(self.angle)
        self.launch_dir = ['',''] #[xdirection, ydirection]
        if self.vx > 0:
            self.launch_dir[0] = '+'
        elif self.vx < 0:
            self.launch_dir[0] = '-'
        if self.vy > 0:
            self.launch_dir[1] = '+'
        elif self.vy < 0:
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
                self.stopped = True
        elif self.vx < 0: #if vx is negative
            if self.launch_dir[0] == '-': # is true if vx should be negative
                self.vx += accx
            else:
                self.vx = 0 # makes it stay at 0 once it reaches it
                self.stopped = True
        if self.vy > 0: #if vy is positive
            if self.launch_dir[1] == '+': # is true if vy should be positive
                self.vy -= accy
            else:
                self.vy = 0 # makes it stay at 0 once it reaches it
                self.stopped = True
        elif self.vy < 0: #if vy is negative
            if self.launch_dir[1] == '-': # is true if vy should be negative
                self.vy += accy
            else:
                self.vy = 0 # makes it stay at 0 once it reaches it
                self.stopped = True
        #print(self.vx,self.vy)

class Board():
    """the game board
    Board that shrinks every round
    """
    def __init__(self,width,height,shrink_rate):
        self.topx = 0
        self.topy = 0
        self.width = width
        self.area = self.width*2
        self.shrink_rate = shrink_rate
        self.board = None
        self.actor = Actor("square",(WIDTH//2,HEIGHT//2))
    def shrink_board(self):
        #make this relative to the top left corner of the board class
        #the area of the board (800^2): sqrt(64000*90%) = side length of the board after shrinkage (758.9)
        #800 - the side length  = the coordinate of the top left corner
        if self.actor.scale >= 0.1:
            self.actor.scale *= self.shrink_rate
            
            #updates the pos of the top left corner
            self.area *= self.shrink_rate
            self.width = self.area*0.5
            self.topx = 800-(self.area**0.5)
            self.topy = self.topx
            
admin = Driver()
admin.setupPlayers()
admin.setupBoard(0.9)

def on_mouse_down(pos):
    "Turns active_arrow True if mouse is held down and if mouse position is colliding with unit"
   # print(pos) #debugging
    for player in admin.players:
        for unit in player.units:
            if unit.actor.collidepoint(pos):
                unit.active_arrow = True

def on_mouse_up(pos, button):
    "Turns active_arrow False if mouse is lifted up"
    for player in admin.players:
        for unit in player.units:
            unit.active_arrow = False
        
def on_mouse_move(pos, rel, buttons):
    "Changes position of line vector if left click + active_arrow is True"
    for player in admin.players:
        if not player.ready_launch:
            for unit in player.units:
                mag_mouse_vect = math.sqrt((pos[0] - unit.x)**2 + (pos[1] - unit.y)**2)  #Stores magnitude of theoretical line between unit and cursor
                if mag_mouse_vect > max_arr_len:
                    factor = max_arr_len / mag_mouse_vect       #Create a multiplying factor if the line exceeds the maximum length
                else:
                    factor = 1
                if mouse.LEFT in buttons and unit.active_arrow and admin.status[int(player.team[1])-1] == 1:
                    unit.linex = unit.x + ((pos[0] - unit.x) * factor)       #Use similar triangles to develop an equation to readjust the position of the line
                    unit.liney = unit.y + ((pos[1] - unit.y) * factor)
            
#time = 0
def draw():
    global turns#,time
    
    screen.clear()
    screen.fill((50,100,150))
    
    admin.board.actor.draw()
    '''if time/60 >= 1:
        admin.shrink()
        time = 0
        '''
    if admin.status.count(0) == len(admin.status):
        screen.draw.text("Press SPACE to Start!", centerx = WIDTH/2, centery = HEIGHT/2, fontsize = 50)

    #for unit in admin.players[0].units:
    #    screen.draw.line((unit.actor.x, unit.actor.y), (unit.linex, unit.liney), (50, 50, 50))
    for players in admin.players:
        for unit in players.units:
            if admin.status[int(players.team[1])-1] == 1:          #Draw line if player is making their turn
                screen.draw.line((unit.actor.x, unit.actor.y), (unit.linex, unit.liney), (50, 50, 50))
            if unit.mag_line_vect > unit.radius:
                screen.draw.text("Press SPACE to commit turn", centerx = WIDTH/2, centery = HEIGHT - 50)
            
            #highlights players
            if players.team == "p1":
                screen.draw.filled_circle((unit.x,unit.y),27,(255,0,0))
            elif players.team == "p2":
                screen.draw.filled_circle((unit.x,unit.y),27,(0,0,255))
             
            unit.actor.draw()
 
    for i in range(len(admin.status)):
        if admin.status[i] == 1:
            screen.draw.text(f"Player {i+1}'s turn", centerx = WIDTH/2, centery = 30)    
    '''for players in admin.players:
        if not players.ready_launch:
            screen.draw.text(f"Player {players.team[1]}'s turn", (WIDTH/2, 30), color="orange")
      '''      """
    turns += 1 #for testing
    """
    
    if admin.status.count(2) == len(admin.status):
        if admin.end_turn():
            screen.draw.text("Continue Turn", centerx = WIDTH/2, centery = HEIGHT/2)
            if keyboard.r and admin.status.count(2) == len(admin.status):
                admin.shrink()
                admin.next_turn()
                print("next turn")
            
def change_key():
    global checking_key
    checking_key = False

def update():
    #Start Game
    
    #print(admin.launch)
    if keyboard.SPACE and admin.status.count(1) != len(admin.status) and not admin.checking_key:   #Update status on if player is not gone, going, or ready
        admin.status[admin.cycle] = 1
        admin.cycle += 1
        admin.checking_key = True
        clock.schedule_unique(change_key, 1)
    #print(admin.status)
    '''
    if keyboard.g:
        admin.play_turn()
        '''
    #print(admin.status, admin.cycle)
    
    if admin.status.count(2) == len(admin.status) - 1:
        admin.status[-1] = 2
        admin.play_turn()

    
    for players in admin.players:
        players.commit()
        for unit in players.units:
            if admin.launch == True:
                
                unit.move()
                unit.acceleration()

    admin.detect_collision()
    admin.units_fall()
    for player in admin.players:
        for unit in player.units:
            unit.update_line()

    for i in range(len(admin.status), 0, -1):
        if admin.status[i - 1] == 2 and admin.status[i-1] != admin.status[-1]:
            admin.status[i] = 1
            break


pgzrun.go()


