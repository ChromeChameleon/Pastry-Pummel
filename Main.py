"""
Authors: Kelvin, Nathan, Tino
Date: 6/19/2023
Description: a Pygamezero project inspired by the ios mobile game "Knockout". A 2-player versus game consisting of realistic
             physics. The goal of the game is to knock the opponents pieces off the board. 
"""

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

import pgzrun
from pgzhelper import *
from random import *
import math

#Read-only Variables
TITLE = "Pastry Pummel"
WIDTH = 1200
HEIGHT = 1000

cx = WIDTH // 2 #x coord of centre of screen
cy = HEIGHT // 2 # y coord of centre of screen
uk = 0.01  #coefficient of friction
max_arr_len = 200 #max length of the line
powa = 0.05 #power multiplier for line vectors
scenes = ["title","tutorial","game"] #possible game screens

class Driver():
    '''
    Handles all game events and overall game manager
    
    Attributes:
    -----------
    actors: List
        Stores a list of unit actors
    players: List
        Stores a list of players in the game
    raccoons: List
        Stores a list of raccoon actors
    status: List
        Stores the game's current turn status (who's turn it is, etc)
    cycle: Int
        Stores an integer that cycles through a turn (related to status)
    turns: Int
        Stores the game's number of turns
    board: String / Object
        Initialized as a string but eventually stores a Board object
    scene: String
        Stores the current screen that the game is displaying
    checking_key: Boolean
        A key in a dictionary the represents the units collided with
    draw_lines: Boolean
        represents whether or not to draw the line vectors
    launch: Boolean
        launch conditional check
    terminate_game: Boolean
        Whether the game is done or not
    '''
    def __init__(self):
        self.actors = []
        self.players = []
        self.raccoons= []
        self.eyes = []
        self.status = [0]
        
        self.cycle = 0
        self.turns = 1

        self.board = ""
        self.scene = 'title' #starting screen
        
        self.checking_key = False
        self.draw_lines = False
        self.launch = False
        self.terminate_game = False

    def setupPlayers(self):
        '''
        Creates the actors and the positions of them
        '''
        starting_pos = 100 
        for i in range(1,3): #two players 
            p = Player(f"p{i}")
            p.make_team(4,starting_pos) #creates 4 units
            self.players.append(p)
            self.status.append(0)
            starting_pos = WIDTH - starting_pos 
        
        #creates the list of all players actors 
        self.setupActors()
        
    def setupActors(self):
        """
        creates a list of all actors of all units
        """
        for i in range(len(self.players[0].units)): #creates a list of actors of the 2nd team
            self.actors.append(self.players[0].units[i])
        
        for i in range(len(self.players[1].units)): #creates a list of actors of the 2nd team
            self.actors.append(self.players[1].units[i])
            
    def setupBoard(self,shrink_rate):
        """
        creates the gameboard
        """
        self.board = Board(800,800,shrink_rate)
    
    def start_launch(self):
        """
        Sets all unit initial velocities and progresses the "turn"
        """
        self.launch = True
        self.draw_lines = False
        for player in self.players:
            for unit in player.units:
                unit.launch_power()
                
    def end_turn(self):
        '''
        Checks if all units are stopped moving
        
        Returns
        ---------
        returns True if all units are stopped
        returns False otherwise
        '''
        for player in self.players:
            for unit in player.units:
                if not unit.stopped:
                    return False
        return True

    def next_turn(self):
        '''
        Resets attributes for next turn
        '''
        self.cycle = 0
        self.launch = False
        self.turns += 1
        admin.status = [1, 0, 0]
        for player in self.players:
            player.ready_launch = False
            for unit in player.units:
                unit.line_vect = (0, 0)
                unit.mag_line_vect = 0
                unit.active_arrow = False
                unit.linex = unit.x
                unit.liney = unit.y
                
        #spawns in eyes from 1 to 10 secs, random amount of times
        for i in range(randint(0,6)):
            clock.schedule(self.create_eyes,randint(1,10))
    def shrink(self):
        """
        Shrinks the playing area, and all units relative to their position on the board
        """
        self.board.shrink_board()
        self.shrink_playerpos()

    def detect_collision(self):
        """
        Detects which units are colliding with which, as well as calculates thier vector components
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
                units.collision_calc(colliders[index]) # passes the second unit collided into the collision calc
            
            #removes items as to prevent collisions with itself
            if len(colliders) != 0:
                colliders.pop(0) 
                collactors.pop(0)   
# 
    def inc_collided_count(self):
        '''
        increases the count of each unit that the unit has recently collided with
        to create a cooldown
        '''
        for unit in self.actors:
            remove = []
            for key in unit.collided: 
                unit.collided[key] += 1
                if unit.collided[key] >= 5: #5 frame cooldown seems to be the best (used to be 9)
                    remove.append(key) #the keys to remove are appended to a list
                                       #and then removed after because you can't do it
                                       #while the dict is being iterated through.
            for item in remove:
                unit.collided.pop(item)
        
    def shrink_playerpos(self):
        """
        Moves the units position relative to the size of the game board
        """
        for player in self.players:
            for unit in player.units:
                unit.x = cx - (cx-unit.x)*self.board.shrink_rate #
                unit.y = cy - (cy-unit.y)*self.board.shrink_rate
                
                #shifts units while not launching
                unit.actor.x = unit.x
                unit.actor.y = unit.y
                
    def create_raccoon(self,x,y,pastry):
        """
        Creates a raccoon at the fallen unit position
        """
        r = Raccoon(x,y) #creates a raccoon
        r.set_images(pastry) #sets the animation set
        self.raccoons.append(r) #appends to list of raccoon objects
         
        
    def create_eyes(self):
        """
        creates a eye object and set a random coord to it
        """
        e = Eyes()
        e.actor.x = choice([randint(0,200),randint(1000,1200)])
        e.actor.y = randint(0,1000)
        self.eyes.append(e)
   
    def units_fall(self):
        """
        Handles when units fall of the edge of the board
        
        Returns
        --------
        returns False when units aren't falling
        returns True otherwise
        """
        #center = cx,cy
        #Left edge = cx - board.width/2 , right edge = cx + board.width/2
        #top edge = cy + board.width/2 , bottom edge = cy - board.width/2
        for player in self.players:
            for unit in player.units:
                
                #Horiztontal border
                if unit.x < (cx-self.board.width/2) or unit.x > (cx+self.board.width/2):

                    if admin.status.count(0) != len(admin.status):
                        
                        #spawn raccoons
                        self.create_raccoon(unit.x,unit.y,unit.pastry)

                        #deletes unit from existence
                        player.units.remove(unit)
                        del unit
                    else:
                        return False
                    
                #Verticle border
                elif unit.y > (cy+self.board.width/2) or unit.y < (cy-self.board.width/2):
                    if admin.status.count(0) != len(admin.status):

                         #spawn raccoons
                        self.create_raccoon(unit.x,unit.y,unit.pastry)

                        #deletes unit from existence
                        player.units.remove(unit)
                        del unit
                    else:
                        return False
        return True
    
    def data_transfer(self):
        '''
        turn, positions, velocities, whos turn it is 
        '''
        data = [self.turns]
        for player in self.players:
            data.append(len(player.units))
            for unit in player.units:
                data.append((unit.x,unit.y))
        
    def game_over(self, player):
        '''
        Check if a player has lost
        '''
        if player.units == []:
            return True
        return False
    
    def reset(self):

        self.scene = "gameover"
        
        #resets the win condition
        self.terminate_game = False
        
        #resets all variables 
        self.players = []
        self.actors = []
        self.launch = False
        self.status = [0]
        self.draw_lines = False
        self.checking_key = False
        self.cycle = 0
        self.turns = 1
        self.setupPlayers()
        self.setupBoard(0.9)
        
        #return to game
        self.scene = "game"
        
class Player():
    """The player class which handles individual team events
    
    Attributes
    -------------
    team: Str
        that represents which team the player is on
    units: List
        that represents every unit that belongs to the player
    ready_launch: boolean
        representing if the player's turn is done
    loser: boolean
        representing whether or not all the players units are gone
    """
    
    def __init__(self,team):
        self.team = team #team eg player 1 or 2
        self.units = [] 
        self.ready_launch = False
        self.loser = False
       
    def make_team(self, units,starting_pos):
        """takes the # of units and their starting positions and creates a team of units"""
        pastries = ["cookie","c_roll","donut","eggtart","penguinoes"]
        xpos = starting_pos
        ypos = 200
        for i in range(units):
            self.units.append(Unit(xpos, ypos, 40, pastries[i],f"{self.team}{pastries[i]}{i}"))
            ypos += 150
    
    def commit(self):
        '''
        Detects to see if the line vector magnitude is greater than zero and if the player is ready to launch
        '''
        for unit in self.units:
            if unit.mag_line_vect < unit.radius:           #Set a proper boundary in the future
                self.ready_launch = False
                return self.ready_launch
        if keyboard.SPACE and admin.status[int(self.team[1])-1] == 1 and not self.ready_launch: #Change to a button in the future - keyboard.SPACE is temporary
            self.ready_launch = True
            admin.status[int(self.team[1]) - 1] = 2
            
class Unit():
    '''The individual pastry class, which handles all events of the pastries

    Attributes
    ----------
    name: Str
        name of the unit , includes the team its on
    pastry: Str
        name of the pastry the unit is using as it image
    x: Int
        value that represents the x position of the unit
    y: Int
        value that represents the y position of the unit
    mass: Int
        values that represents the mass of the unit
    actor: Class
        Stores the Actor class of the unit
    actor.x: Int
        x position of the actor
    actor.y: Int
        y position of the actor
    vx: Int
        value that represents the x speed of the unit
    vy: Int
        value that represents the y speed of the unit
    
    radius: Int
        value that is the radius of the unit (in pixels)
    linex: Int
        the x position of the units launch line
    liney: Int
        the y position of the units launch line
    line_vect: Tuple
        Stores the vector components of the line relative to the unit's position
    mag_line_vect: Int
        Stores the magnitude of the line vector
    active_arrow: Boolean
        Whether if the units arrow is active
    stopped: Boolean
        Whether the unit has stopped all movement
    collided: dictionary
        which stores the units that were recntly collided with (as the key)
        and the amount of frames since that collision as the value
    '''
    def __init__(self, x, y, mass, actor,name):
        self.name = name
        self.pastry = actor
        self.x = x
        self.y = y
        self.mass = mass
        self.actor = Actor(actor)
        self.actor.x = self.x
        self.actor.y = self.y 
        self.vx = 0
        self.vy = 0
        self.radius = 27
        self.linex = x
        self.liney = y
        self.line_vect = (0, 0)
        self.mag_line_vect = 0
        self.active_arrow = False
        self.stopped = True
        self.collided = {}

    def __repr__(self):
        """returns the name when called"""
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
        
    def launch_power(self):
        """
        sets the unitial velocity/power of the units depending on the length of the line vector
        """
        #takes the ratio of radius/magnitude of line vector multiplied by power and the line vector to change the velocities
        if self.mag_line_vect != 0:
            ratio = self.radius / self.mag_line_vect
            x = self.line_vect[0] * (1-ratio) * powa
            y = self.line_vect[1] * (1-ratio) * powa
            self.update_v(x,y)

    def move(self):
        '''
        moves the units and their actors coordinates by its current x and y velocities
        '''
        self.x += self.vx
        self.y += self.vy
        
        self.actor.x = self.x
        self.actor.y = self.y
    def update_v(self, vx, vy):
        '''
        Sets the x and y velocities of the unit to the given values,
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
        self.launch_dir = ['',''] #[xdirection, ydirection]
        if self.vx > 0:
            self.launch_dir[0] = '+'
        elif self.vx < 0:
            self.launch_dir[0] = '-'
        if self.vy > 0:
            self.launch_dir[1] = '+'
        elif self.vy < 0:
            self.launch_dir[1] = '-'
        
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
        if m2 not in self.collided and admin.launch == True: #only collides if it wasn't recently collided with
            self.collided[m2] = 0
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

    def acceleration(self):
        '''
        calculates the magnitude of acceleration and calculates the x and y
        components. It then adds or subtracts the x and y acceleration components
        to bring the x and y velocity components down to 0.
        
        '''
        #fnet = ma, -Ff = ma, -ukFn = ma, -ukFg = ma, -ukmg = ma, -ukg = a
        acc = uk * 9.8
        accx = acc * math.cos(self.angle) #calculates components
        accy = acc * math.sin(self.angle)
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
            if self.launch_dir[1] == '-': # is true if vy should be negative
                self.vy += accy
            else:
                self.vy = 0 # makes it stay at 0 once it reaches it

        if self.vx == 0 and self.vy == 0:
            self.stopped = True

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
        """
        Shrinks the area of the board by the a certain percentage
        """
        #800 - the side length  = the coordinate of the top left corner
        if self.actor.scale >= 0.1:
            #scales down the board by the rate
            self.actor.scale *= self.shrink_rate
            
            #updates the area of the board
            self.area *= self.shrink_rate
            self.width = self.area*0.5
            
            #top left coord
            self.topx = 800-(self.area**0.5)
            self.topy = self.topx
            
class Raccoon():
    """Raccoon object 
    
    Spawns when a unit falls off the edge of the board
    
    Attributes
    ----------
    actor: Class
        a actor object that represents the raccoon
    actor.fps: Int
        value that is the frame rate of the animations
    actor.x: Int
        value that represents the x position of the actor
    actor.y: Int
        value that represents the y position of the actor
    
    """
    
    def __init__(self,x,y):
        self.actor = Actor("000")
        self.actor.fps = 6 #8fps is much smoother
        self.actor.x = x
        self.actor.y = y
    
    def set_images(self,pastry):
        """Changes the animation set depending on which pastry has fallen off"""
        if pastry == "cookie":
            self.actor.images = ['000', '001', '002', 'rc003', 'rc004', 'rc005', 'rc006', '007', '008', '009', '010']
        elif pastry == "c_roll":
            self.actor.images = ['000', '001', '002', 'rcr003', 'rcr004', 'rcr005', 'rcr006', '007', '008', '009', '010']
        elif pastry == "donut":
            self.actor.images = ['000', '001', '002', 'rd003', 'rd004', 'rd005', 'rd006', '007', '008', '009', '010']
        elif pastry == "eggtart":
            self.actor.images = ['000', '001', '002', 'ret003', 'ret004', 'ret005', 'ret006', '007', '008', '009', '010']
    
    def consume(self):
        """Cycles through the animation sets to animate the raccoon"""
        self.actor.animate()
        

class Eyes():
    """
    Eyes that periodically appear on the screen
    
    Attributes
    -----------
    actor: Class
        Actor object used for visuals
    actor.images: List
        all animations frames
    actor.fps: Int
        Framerate of the animation
        
    """

    def __init__(self):
        self.actor = Actor('e014')
        self.actor.images = ['e000', 'e001', 'e002', 'e003', 'e004', 'e005', 'e006', 'e007', 'e008', 'e009', 'e010', 'e011', 'e012', 'e013', 'e014','e015','e016']
        self.actor.fps = 8
        
    def spawn_eyes(self):
        """animates the actors"""
        self.actor.animate()
            
        
def on_mouse_down(pos):
    "Turns active_arrow True if mouse is held down and if mouse position is colliding with unit"

    #closes tutorial popup
    if admin.scene == "tutorial":
        admin.scene = "title"
        
    #open tutorial popup
    if admin.scene == "title" and (425 < pos[0] < 725) and (720 < pos[1] < 820):
        admin.scene = "tutorial"
        
    #runs only when in game
    if admin.scene == "game":
        for player in admin.players:
            for unit in player.units:
                if unit.actor.collidepoint(pos):
                    unit.active_arrow = True
    
        if rect_q.collidepoint(pos):
            preset(1, [[500, 250], [350, 400], [350, HEIGHT - 400], [500, HEIGHT - 250]])
        if rect_w.collidepoint(pos):
            preset(1, [[400, 250], [400, 400], [400, HEIGHT - 400], [400, HEIGHT - 250]])
        if rect_e.collidepoint(pos):
            preset(1, [[350, 250], [500, 400], [500, HEIGHT - 400], [350, HEIGHT - 250]])
        if rect_p.collidepoint(pos):
            preset(2, [[700, 250], [850, 400], [850, HEIGHT - 400], [700, HEIGHT - 250]])
        if rect_o.collidepoint(pos):
            preset(2, [[800, 250], [800, 400], [800, HEIGHT - 400], [800, HEIGHT - 250]])
        if rect_i.collidepoint(pos):
            preset(2, [[850, 250], [700, 400], [700, HEIGHT - 400], [850, HEIGHT - 250]])
    

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
                if admin.status.count(0) != len(admin.status):
                    mag_mouse_vect = math.sqrt((pos[0] - unit.x)**2 + (pos[1] - unit.y)**2)  #Stores magnitude of theoretical line between unit and cursor
                    if mag_mouse_vect > max_arr_len:
                        factor = max_arr_len / mag_mouse_vect       #Create a multiplying factor if the line exceeds the maximum length
                    else:
                        factor = 1
                    if mouse.LEFT in buttons and unit.active_arrow and admin.status[int(player.team[1])-1] == 1:
                        unit.linex = unit.x + ((pos[0] - unit.x) * factor)       #Use similar triangles to develop an equation to readjust the position of the line
                        unit.liney = unit.y + ((pos[1] - unit.y) * factor)
                elif unit.active_arrow:                    #NOTE: unit.active_arrow now also represents a bool that determines if a unit is being dragged
                    unit.actor.x = pos[0]
                    unit.x = unit.actor.x
                    unit.actor.y = pos[1]
                    unit.y = unit.actor.y
                    unit.linex = unit.actor.x
                    unit.liney = unit.actor.y
#various rectangles

#pre game screen
rect_q = Rect((200, 800), (100, 100))
rect_w = Rect((300, 800), (100, 100))
rect_e = Rect((400, 800), (100, 100))
rect_p = Rect((WIDTH - 200 - 100, 800), (100, 100))
rect_o = Rect((WIDTH - 300 - 100, 800), (100, 100))
rect_i = Rect((WIDTH - 400 - 100, 800), (100, 100))

#title screen
rect_tutorial = Rect((425,720), (300,100))

def draw():
    screen.clear()
    """TITLE SCREEN"""
    if admin.scene == "title":
        screen.blit("title",(0,0))       
        screen.draw.filled_rect(rect_tutorial,("RED"))
        screen.draw.text("How To Play",(450,750),color = "white",fontsize = 60)
    """TUTORIAL SCREEN"""   
    if admin.scene == "tutorial":
        screen.blit("title",(0,0))   
        screen.blit("tutorial_popup",(200,300))
        
    """GAME SCREEN"""
    if admin.scene == "game":
        screen.fill((29, 29, 31)) #grey ish was (50,100,150)

    #Draws the game board
        admin.board.actor.draw()
        
        #informative text for Positioning units
        if admin.status.count(0) == len(admin.status):
            screen.draw.text("Position Your Characters!", centerx = WIDTH/2, centery = HEIGHT/2, fontsize = 50, color = (64, 0, 255))
            screen.draw.text("Press SPACE To Start Once Positioned", centerx = WIDTH/2, centery = HEIGHT/1.5, fontsize = 40, color = (64, 0, 255))
            
            #Player 1
            screen.draw.filled_rect(rect_q, (150, 50, 25))
            screen.blit("c_line", (200, 800))
            screen.draw.filled_rect(rect_w, (200, 100, 50))
            screen.blit("straight_line", (300, 800))
            screen.draw.filled_rect(rect_e, (250, 150, 75))
            screen.blit("d_line", (400, 800))
            
            #Player 2
            screen.draw.filled_rect(rect_p, (25, 50, 150))
            screen.blit("d_line", (WIDTH - 200 - 100, 800))
            screen.draw.filled_rect(rect_o, (50, 100, 200))
            screen.blit("straight_line", (WIDTH - 300 - 100, 800))
            screen.draw.filled_rect(rect_i, (75, 150, 250))
            screen.blit("c_line", (WIDTH - 400 - 100, 800))

        #updates vector line visual, as well as unit highlight indicators
        for players in admin.players:
            
            for unit in players.units:
                #Draw line if player is making their turn
                if admin.status[int(players.team[1])-1] == 1 or admin.draw_lines:
                    
                    """Draws an arrowhead on the tip of the line"""
                    a = Actor("arrow")
                    a.x = unit.linex #arrow heads pos
                    a.y = unit.liney
                    dx = (unit.linex - unit.actor.x) #change in x position from center of unit to tip of line
                    dy = (unit.liney - unit.actor.y) #change in y position
                    
                    if dx != 0:
                        a.angle = -1* math.degrees(math.atan(dy/dx)) #right side of unit  
                        if dx < 0:
                            a.angle += 180 #left side of unit
                    elif dx == 0:
                        if dy > 0:
                            a.angle = -90 #down
                        elif dy < 0:
                            a.angle = 90 #top
             
                    #vector line
                    screen.draw.line((unit.actor.x, unit.actor.y), (unit.linex, unit.liney), (50, 50, 50))
                    
                    #arrow
                    a.draw()
     
                if unit.mag_line_vect > unit.radius:

                    screen.draw.text("Press SPACE to commit turn once ready", centerx = WIDTH/2, centery = HEIGHT - 50)
                
                #highlights players
                if players.team == "p1":
                    screen.draw.filled_circle((unit.x,unit.y),27,(255,0,0))
                elif players.team == "p2":
                    screen.draw.filled_circle((unit.x,unit.y),27,(0,0,255))

                unit.actor.draw()

        #Informative text that represents the current players turn
        for i in range(len(admin.status)):
            if admin.status[i] == 1:
                if i+1 == 1:
                    screen.draw.text("@Player 2, Look Away!", centerx = WIDTH/2, centery = 80)
                    screen.draw.text(f"Player {i+1}'s turn", centerx = WIDTH/2, centery = 40,fontsize = 80, color = (255, 0, 0))    
                else:
                    screen.draw.text(f"Player {i+1}'s turn", centerx = WIDTH/2, centery = 40,fontsize = 80, color = (0, 0, 255))    

        if admin.status.count(2) == len(admin.status):           #Check if all indexes are 2 (aka if they're mid launching)
            if admin.end_turn() and not admin.terminate_game and not admin.draw_lines:
                screen.draw.text("Click R to continue", centerx = WIDTH/2, centery = HEIGHT/2, color = (64, 0, 255))
                
                #Progresses to next turn
                if keyboard.r and admin.status.count(2) == len(admin.status):
                    admin.shrink()
                    admin.next_turn()
                    admin.data_transfer()

        #turn indicator text            
        screen.draw.text(f"TURN {admin.turns}", centerx = 100, centery = 40,fontsize = 50)
        
        #replaying the game stuff
        if admin.terminate_game:
            screen.draw.text("PRESS R TO PLAY AGAIN", centerx = WIDTH/2, centery = HEIGHT/2+150, color = (255, 255, 255), fontsize = 50)
            if keyboard.r:
                admin.reset()
        
        #decides who is the winner
        for i in range(len(admin.players)):
            if admin.players[0].loser and admin.players[1].loser:
                screen.draw.text("Everybody Loses :), The Raccoons Win", centerx = WIDTH/2, centery = HEIGHT/2, fontsize = 50, color = (255,255,255))
                admin.terminate_game = True
                
            elif admin.players[0].loser:
                screen.draw.text("Player 2 Wins!", centerx = WIDTH/2, centery = HEIGHT/2, fontsize = 50, color = (64, 0, 255))
                admin.terminate_game = True
                
            elif admin.players[1].loser:
                screen.draw.text("Player 1 Wins!", centerx = WIDTH/2, centery = HEIGHT/2, fontsize = 50, color = (255, 0, 64))
                admin.terminate_game = True
                
        #draws all the raccoons who eat the fallen pieces
        for raccoon in admin.raccoons:
            if raccoon.actor.image != "010" or admin.terminate_game:
                raccoon.actor.draw()
                raccoon.consume()
            
        #draws all the eyes 
        for eye in admin.eyes:
            eye.actor.draw()
            eye.spawn_eyes()
            
            #removes after animation is done
            if eye.actor.image == "e016":
                admin.eyes.remove(eye)
        
        
                
def change_key():
    '''
    Called through a clock.schedule to prevent multiple registrations of a key
    '''
    global checking_key
    checking_key = False

def update_status():
    '''
    Called in update and runs through all the conditions required to update admin.status
    '''
    if keyboard.SPACE and admin.status.count(1) != len(admin.status) and not admin.checking_key and admin.units_fall():

        #Update status on if player is not gone, going, or ready
        admin.status[admin.cycle] = 1
        admin.cycle += 1
        admin.checking_key = True
        clock.schedule_unique(change_key, 1)
    
    if admin.status.count(2) == len(admin.status) - 1:
        admin.status[-1] = 2
        admin.draw_lines = True
        clock.schedule_unique(admin.start_launch, 2)   #Delay launch by 2 seconds

    for i in range(len(admin.status), 0, -1):
        if admin.status[i - 1] == 2 and admin.status[i-1] != admin.status[-1]:           #If an index is 2, change the next index to 1 (aka passing the turn)
            admin.status[i] = 1
            break

def preset(p, mylist):
    '''
    Creates new set positions for a player's starting position
    '''
    i = 0
    for unit in admin.players[p - 1].units:
        unit.actor.x = mylist[i][0]
        unit.actor.y = mylist[i][1]
        unit.x = unit.actor.x
        unit.y = unit.actor.y
        unit.linex = unit.actor.x
        unit.liney = unit.actor.y
        i += 1

def update():
    #Start Game
    
    """TITLE SCENE"""
    if admin.scene == "title":
        if keyboard.SPACE:
            admin.scene = "game"
    
    """TUTORIAL"""
    #in on_mouse_down
        
    """GAME SCENE"""
    if admin.scene == "game":
       
        """updates units depending on player interaction"""
        for player in admin.players:
            player.commit()
            player.loser = admin.game_over(player)
            for unit in player.units:
                unit.update_line()
                if admin.launch:
                    unit.move()
                    unit.acceleration()          
        admin.detect_collision()
        admin.inc_collided_count()
        if admin.status.count(0) != len(admin.status):
            admin.units_fall()
        update_status()

'''represent the keyboard buttons that dont work and shouldnt be here
        if keyboard.q:
            preset(1, [[350, 250], [500, 400], [500, HEIGHT - 400], [350, HEIGHT - 250]])
        if keyboard.w:
            preset(1, [[500, 250], [350, 400], [350, HEIGHT - 400], [500, HEIGHT - 250]])
        if keyboard.e:
            preset(1, [[400, 250], [400, 400], [400, HEIGHT - 400], [400, HEIGHT - 250]])
        
        if keyboard.p:
            preset(2, [[850, 250], [700, 400], [700, HEIGHT - 400], [850, HEIGHT - 250]])
        if keyboard.o:
            preset(2, [[700, 250], [850, 400], [850, HEIGHT - 400], [700, HEIGHT - 250]])
        if keyboard.i:
            preset(2, [[800, 250], [800, 400], [800, HEIGHT - 400], [800, HEIGHT - 250]])
'''

def main():
    """Initializes the game objects"""
    global admin
    admin = Driver()
    admin.setupPlayers()
    admin.setupBoard(0.9)
    pgzrun.go()

main()

