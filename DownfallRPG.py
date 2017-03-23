#Downfall RPG
#Made by Cody C Emig (soon to be Aleksandr D Tarkovsky)
#started on 2017.03.21

#Import the libtcodpy files as libtcod for easy reference
import libtcodpy as libtcod
#Set screensize to whatever it needs to be
screenWidth = 80
screenHeight = 50

#Size of the map
mapWidth = 80
mapHeight = 45

#Limits for the dungeon generator
roomMaxSize = 10
roomMinSize = 6
maxRooms = 30

#Limit FPS to GLORIOUS 60 FPS
limitFps = 60

#Creates colors for the DARK versions of walls and the ground
colorDarkWall = libtcod.Color(100, 100, 100)
colorDarkGround = libtcod.Color(50, 50, 50)

class Tile:
	#Defines a tile of the map and it's properties
	def __init__(self, blocked, blockSight=None):
		self.blocked = blocked
		
		#by default, if a tile is blocked, it also blocks sight
		if blockSight is None: blockSight = blocked
		self.blockSight = blockSight

class Rect:
    #a rectangle on the map.  used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
		
	def center(self):
		#points to the center of the room for the creation of tunnels
        centerX = (self.x1 + self.x2) / 2
		centerY = (self.y1 + self.y2) / 2
		return (centerX, centerY)
		
	def intersect(self, other):
		#returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)
		
class Object:
	#This is a generic object; the player, enemy, item, terrain
	#it's always represented by a character on the game screen.
	def __init__(self, x, y, char, color):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		
	def move(self, dx, dy):
		if not map[self.x + dx][self.y + dy].blocked:
			#Move by the given amount
			self.x += dx
			self.y += dy
		
	def draw(self):
		#Set the color and then draw the character that represents this object at
		#it's position
		libtcod.console_set_default_foreground(con, self.color)
		libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
		
	def clear(self):
		#erase the character that represents this object
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
		
def createRoom(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].blockSight = False

def createHTunnel(x1, x2, y):
	#creates a horizontal tunnel
	global map
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].blockSight = False
		
def createVTunnel(y1, y2, x):
	#creates a vertical tunnel
	global map
	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].blockSight = False
		
def makeMap():
	global map, player
	
	#Fills the map with blocked tiles
	map = [[ Tile(True)
		for y in range(mapHeight) ]
			for x in range(mapWidth) ]
			
	#creates an empty array to hold the rooms' data in
	rooms = []
	numRooms = 0
	
	for r in range(maxRooms):
		#Creates a random size for the room to be
		w = libtcod.random_get_int(0, roomMinSize, roomMaxSize)
		h = libtcod.random_get_int(0, roomMinSize, roomMaxSize)
		#Creates a random position for the room to be in without going outside the
		#map
		x = libtcod.random_get_int(0, 0, mapWidth - w - 1)
		y = libtcod.random_get_int(0, 0, mapHeight - h - 1)
		
	#Create a new room with rect dimensions
	newRoom = Rect(x, y, w, h)
	
	#Check to see if other rooms intersect with this room
	failed = False
	for otherRoom in rooms:
		if newRoom.intersect(otherRoom):
			failed = True
			break

	if not failed:
		#No intersections = valid room
		
		#creates the room to the map
		createRoom(newRoom)
		
		#center coordinates of the new room, useful for later
		(newX, newY) = newRoom.center()
		
		if numRooms == 0:
			#this is the first room, where the player is spawned
			player.x = newX
			player.y = newY
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel
 
                #center coordinates of previous room
                (prevX, prevY) = rooms[numRooms-1].center()
 
                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    createHTunnel(prevX, newX, prevY)
                    createVTunnel(prevY, newY, newX)
                else:
                    #first move vertically, then horizontally
                    createVTunnel(prevY, newY, prevX)
                    createHTunnel(prevX, newX, newY)
 
            #finally, append the new room to the list
            rooms.append(newRoom)
            numRooms += 1

def renderAll():
global colorDarkWall, colorLightWall
global colorDarkGround, colorLightGround
 
    #go through all tiles, and set their background color
    for y in range(mapHeight):
        for x in range(mapWidth):
            wall = map[x][y].blockSight
            if wall:
                libtcod.console_set_char_background(con, x, y, colorDarkWall, libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con, x, y, colorDarkGround, libtcod.BKGND_SET)
 
    #draw all objects in the list
    for object in objects:
        object.draw()
 
    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, screenWidth, screenHeight, 0, 0, 0)	

def handle_keys():
	key = libtcod.console_wait_for_keypress(True)
	
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter = Toggle Fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
		
	#Exit game if someone presses escape
	elif key.vk == libtcod.KEY_ESCAPE:
		return True
		
	#movement keys
	#Move up if you press the up arrow
	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		player.move(0, -1)
	#move down if you press the down arrow
	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		player.move(0, 1)
	#Move left if you press left
	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		player.move(-1, 0)
	#Move right if you press right
	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		player.move(1, 0)

# ############################# #
# Initialization and Main Loop  #
# ############################# #

#Sets the font to whatever it needs to be
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
#Creates the window, sizes it, sets the title, and if it's fullscreen or not
libtcod.console_init_root(screenWidth, screenHeight, 'Downfall RPG', False)
#Sets the system FPS to max FPS
libtcod.sys_set_fps(limitFps)
#creates an offscreen console the player can't see
con = libtcod.console_new(screenWidth, screenHeight)

#creates the player, and an NPC as an object
player = Object(screenWidth / 2, screenHeight / 2, '@', libtcod.white)
npc = Object(screenWidth / 2 - 5, screenHeight / 2, '@', libtcod.red)
objects = [npc, player]

#generate map (do not place it on the screen)
makeMap()

#Does shit while the game is running
while not libtcod.console_is_window_closed():
	
	#Draw all objects in the list
	renderAll()
	
	#Updates the game
	libtcod.console_flush()
	
	#erase all objects at old locatios before they move
	for object in objects:
		object.clear()
	
	#handle keys and exit game
	exit = handle_keys()
	if exit:
		break