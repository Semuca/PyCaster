import math
import os
from tkinter import *

assetPath = os.getcwd() + "/Assets/" #Sets directory

root = Tk() #Creates window

class Screen: #Manages drawing lines
    def __init__(self, assetPath, root):
        self.anglesPerScan = 1 #How many angles between each ray cast
        self.assetPath = assetPath
        self.canvas = Canvas(root, highlightthickness = 0) #Creates canvas to draw lines on
        self.canvas.image_names = [] #Creates array to store PhotoImage classes to prevent garbage collection
        self.canvas.pack(expand = True, fill = BOTH)
        self.fovAngle = 100 #Field of view
        self.spriteArray = [] #Stores Sprite classes
        self.wallArray = [] #Stores WallSegment classes
        self.windowHeight = 0 #Sets up window dimensions
        self.windowWidth = 0

    def DrawLines(self): #Draws the lines of the room based on the rays cast
        self.canvas.delete("all") #Clears canvas
        _width = (self.windowWidth * (self.anglesPerScan / self.fovAngle)) + 1 #Determines the width for each line based off the windowWidth
        for i in range(len(self.wallArray)):
            _images = []
            for j in self.spriteArray:
                if (i in j.segments and j.distance < self.wallArray[i].distance): #Checks if a sprite is in front of the wall
                    if (len(_images) == 0): #Puts the sprite in the array if there is none already
                        _images.append(j)
                    else:
                        for k in range(len(_images)):
                            if (_images[k].distance < j.distance): #Orders the sprites if there is more than one
                                _images.insert(k, j)
            _tempX = int((((i + 0.5) * self.anglesPerScan) / self.fovAngle) * self.windowWidth) #Calculates column position
            _tempHeight = int(self.windowHeight / (self.wallArray[i].distance + 1)) #Calculates column height
            _referenceImg = PhotoImage(file = self.assetPath + "Textures/" + str(self.wallArray[i].id) + ".png") #Reads the source image of the wall
            self.DrawColumn(_tempHeight, _referenceImg, self.wallArray[i].segment, _tempX, _width) #Draws wall column
            for j in _images:
                _spriteHeight = int(self.windowHeight / (j.distance + 1)) #Calculates sprite height
                _referenceSprite = PhotoImage(file = self.assetPath + "Sprites/" + str(j.id) + ".png") #Reads the source image of the sprite
                self.DrawColumn(_spriteHeight, _referenceSprite, j.segments.index(i) / len(j.segments), _tempX, _width) #Draws an individual column of a sprite

    def DrawColumn(self, height, img, segment, x, width): #Draws a column based on ray data
        _img = PhotoImage(width = int(width), height = height) #Creates PhotoImage based on proportions
        _colours = []
        for i in range(img.height()):
            r, g, b = img.get(int(segment * (img.width() - 1)), i) #Get source image pixel data and put it in hexadecimal format
            _r = format(r, "02X")
            _g = format(g, "02X")
            _b = format(b, "02X")
            _colour = "#" + str(_r) + str(_g) + str(_b)
            for j in range(int((height / img.height()) * (i + 1) - len(_colours))): #Append the colour to an array
                _colours.append(_colour)
        _img.put(_colours, to = (0, 0, int(width), int(((i + 1) / img.height()) * height))) #Put the column in the PhotoImage
        self.canvas.create_image(x, int(self.windowHeight / 2), image = _img) #Put the column on the canvas
        self.canvas.image_names.append(_img) #Store the PhotoImage in array

    def Configuration(self, event): #Redraws lines if the window size changes
        self.windowHeight = event.height
        self.windowWidth = event.width
        self.DrawLines()

class WallSegment: #Stores information about ray collisions with walls
    def __init__(self, distance, colliderID, segment):
        self.distance = distance
        self.id = colliderID
        self.segment = segment

class Sprite: #Stores information about ray collisions with sprites
    def __init__(self, angle, distance, fov, spriteID, x, z):
        self.angle = int(angle + (fov / 2))
        self.distance = distance
        self.id = spriteID
        self.segments = [] #Stores information on the angles its segments lie on
        _segments = int(fov / (distance + 1))
        for i in range(-int(_segments / 2), int(_segments / 2) + _segments):
            self.segments.append(self.angle + i)
        self.x = x
        self.z = z

class Map: #Stores map data
    def __init__(self, path):
        self.colliderIDs = [2, 3] #Sets up ids to be read as colliders
        self.spriteIDs = [4] #Sets up ids to be read as sprites
        _rawData = open(path, "r") #Reads map file
        self.data = []
        for i in _rawData.readlines():
            i = i.replace("\n", "") #Removes '\n', which stands for 'Enter' keyboard presses
            _tempArray = []
            for j in range(len(i)):
                _tempArray.append(int(i[j])) #Appends all characters to a 2D array
            self.data.append(_tempArray)
        for i in range(len(self.data)): #Locates the first spawn point
            for j in range(len(self.data[i])):
                if (self.data[i][j] == 1):
                    self.xSpawn = j
                    self.zSpawn = i
                    break

class Player: #Manages movement and raycasting
    def __init__(self, mapClass, screen):
        self.map = mapClass
        self.screen = screen
        self.speed = 0.25
        self.rotationSpeed = 15
        self.rotation = 0
        self.xPos = mapClass.xSpawn
        self.zPos = mapClass.zSpawn
        self.xSquare = mapClass.xSpawn
        self.zSquare = mapClass.zSpawn

    def Move(self, event): #Moves the player's position or rotation
        if (event.keysym == "Up" or event.keysym == "Down"):
            if (event.keysym == "Down"): #Checks if the player is moving forward or back and applies modifier
                _speedModifier = 1
            else:
                _speedModifier = -1
            _xPos = self.xPos + math.sin(math.radians(360 - self.rotation)) * _speedModifier * self.speed #Changes X and Z pos based off rotation
            _zPos = self.zPos + math.cos(math.radians(360 - self.rotation)) * _speedModifier * self.speed
            self.xPos, self.xSquare = self.SquareCheck(self.xSquare, _xPos, 1, 0) #Checks to see if the square is occupied and updates position if it is a collider
            self.zPos, self.zSquare = self.SquareCheck(self.zSquare, _zPos, 0, 1)
        if (event.keysym == "Left"): #Checks if the player is looking left or right and changes rotation
            self.rotation = self.rotation - self.rotationSpeed
        elif (event.keysym == "Right"):
            self.rotation = self.rotation + self.rotationSpeed
        if (self.rotation < 0): #Resets rotation to be between 0 and 360
            self.rotation = 360 + self.rotation
        elif (self.rotation >= 360):
            self.rotation = self.rotation - 360
        self.Sense() #Detects the new position the player is in

    def SquareCheck(self, square, pos, modifierX, modifierZ): #Checks if the player is exiting the square and provides positions accordingly
        if (square - pos > 0.5):
            return self.SquareChange(square, pos, -modifierX, -modifierZ)
        elif (square - pos < -0.5):
            return self.SquareChange(square, pos, modifierX, modifierZ)
        else:
            return pos, square

    def SquareChange(self, square, pos, modifierX, modifierZ): #Checks square to see if it is a collider and returns the new position and the square the player is in
        _array = self.map.data[self.zSquare + modifierZ]
        if (_array[self.xSquare + modifierX] in self.map.colliderIDs):
            return square + ((modifierX + modifierZ) / 2), square
        else:
            return pos, square + modifierX + modifierZ

    def Sense(self): #Shoots raycasts to determine the area around the player
        self.screen.spriteArray = []
        self.screen.wallArray = []
        _xPosInSquare = self.xPos - (self.xSquare - 0.5)
        _zPosInSquare = self.zPos - (self.zSquare - 0.5)
        for i in range(-int(self.screen.fovAngle / (2 * self.screen.anglesPerScan)), int(self.screen.fovAngle / (2 * self.screen.anglesPerScan))): #Shoots rays equal to fov / angles per scan
            _xRaySquare = self.xSquare
            _zRaySquare = self.zSquare
            _rayAngle = self.rotation + (i * self.screen.anglesPerScan) #Calculates ray angle
            if (_rayAngle < 0): #Resets angle to be between 0 and 360
                _rayAngle = _rayAngle + 360
            elif (_rayAngle >= 360):
                _rayAngle = _rayAngle - 360
            _tan = math.tan(math.radians(_rayAngle)) #Calculates the tan of the angle
            if (_rayAngle > 0 and _rayAngle < 180): #Determines the direction on the x-axis the ray travels
                _modifierX = 1
            elif (_tan == 0):
                _modifierX = 0
            else:
                _modifierX = -1
            if (_rayAngle > 90 and _rayAngle < 270): #Determines the direction on the z-axis the ray travels
                _modifierZ = 1
            elif (_tan == None):
                _modifierZ = 0
            else:
                _modifierZ = -1
            _xIntX, _xIntZ, _zIntX, _zIntZ = self.FindInitialSquareIntercepts(_rayAngle, _tan, _xPosInSquare, _zPosInSquare) #Gets first square intercepts of the raycast
            _isRaytracing = True
            while _isRaytracing == True:
                if (_zIntX == None or abs(self.xPos - _xIntX) <= abs(self.xPos - _zIntX)): #Finds next intercept, updates the raySquare, and calls CheckIntercept
                    _zRaySquare = _zRaySquare + _modifierZ
                    _isRaytracing, _xIntX, _xIntZ = self.CheckIntercept(i, _xRaySquare, _zRaySquare, _xIntX, _xIntZ, _xRaySquare, _zRaySquare, _xIntX, _xIntZ, _modifierX * abs(_tan), _modifierZ)
                elif (_xIntX == None):
                    _xRaySquare = _xRaySquare + _modifierX
                    _isRaytracing, _zIntZ, _zIntX = self.CheckIntercept(i, _xRaySquare, _zRaySquare, _zIntX, _zIntZ, _zRaySquare, _xRaySquare, _zIntZ, _zIntX, _modifierZ, _modifierX)
                else:
                    _xRaySquare = _xRaySquare + _modifierX
                    _isRaytracing, _zIntZ, _zIntX = self.CheckIntercept(i, _xRaySquare, _zRaySquare, _zIntX, _zIntZ, _zRaySquare, _xRaySquare, _zIntZ, _zIntX, _modifierZ * abs(1 / _tan), _modifierX)
        self.screen.DrawLines() #Updates the screen

    def FindInitialSquareIntercepts(self, angle, tanAngle, xPosInSquare, zPosInSquare): #Finds first square intercepts of the raycast
        if (angle > 0 and angle < 180): #Calculates first intercept on the z-axis for squares using trigonometry
            _zIntX = self.xSquare + 0.5
            _zIntZ = self.zPos - ((1 - xPosInSquare) / tanAngle)
        elif (tanAngle == 0):
            _zIntX = None
            _zIntZ = None
        else:
            _zIntX = self.xSquare - 0.5
            _zIntZ = self.zPos + (xPosInSquare / tanAngle)
        if (angle > 90 and angle < 270): #Calculates first intercept on the x-axis for squares using trigonometry
            return self.xPos - (1 - zPosInSquare) * tanAngle, self.zSquare + 0.5, _zIntX, _zIntZ
        elif (tanAngle == None):
            return None, None, _zIntX, _zIntZ
        else:
            return self.xPos + zPosInSquare * tanAngle, self.zSquare - 0.5, _zIntX, _zIntZ

    #Checks the axis intercept and registers any sprites or walls
    def CheckIntercept(self, rawAngle, xRaySquare, zRaySquare, intX, intZ, primaryRaySquareAxis, secondaryRaySquareAxis, primaryIntAxis, secondaryIntAxis, primaryModifier, secondaryModifier):
        _tempArray = self.map.data[zRaySquare]
        for j in self.map.colliderIDs: #Checks raySquare for a collider
            if (_tempArray[xRaySquare] == j):
                _distance = math.sqrt((self.xPos - intX)**2 + (self.zPos - intZ)**2) #Finds distance to wall
                self.screen.wallArray.append(WallSegment(_distance * math.cos(math.radians(rawAngle * self.screen.anglesPerScan)), j, 0.5 + primaryIntAxis - primaryRaySquareAxis)) #Appends Wallsegment to list
                return False, primaryIntAxis, secondaryIntAxis
        for j in self.map.spriteIDs: #Checks raySquare for a sprite
            if (_tempArray[xRaySquare] == j):
                if (self.CheckForRepeatingSprite(xRaySquare, zRaySquare) == True): #Checks the sprite hasn't already been recorded
                    _distanceX = self.xPos - xRaySquare #Calculates distance to sprite
                    _distanceZ = self.zPos - zRaySquare
                    _distance = math.sqrt((_distanceX)**2 + (_distanceZ)**2)
                    if (_distanceX < 0 and _distanceZ >= 0): #Calculates angle to sprite
                        _angle = math.degrees(math.asin(abs(_distanceX) / _distance))
                    elif (_distanceX < 0 and _distanceZ < 0):
                        _angle = 90 + math.degrees(math.asin(abs(_distanceZ) / _distance))
                    elif (_distanceX >= 0 and _distanceZ < 0):
                        _angle = 180 + math.degrees(math.asin(abs(_distanceX) / _distance))
                    else:
                        _angle = 270 + math.degrees(math.asin(abs(_distanceZ) / _distance))
                    self.screen.spriteArray.append(Sprite(_angle - self.rotation, _distance * math.cos(math.radians(rawAngle * self.screen.anglesPerScan)), self.screen.fovAngle, j, xRaySquare, zRaySquare)) #Creates sprite class
                    break
        _primaryIntAxis = primaryIntAxis + primaryModifier #Updates raycast intercept
        _secondaryIntAxis = secondaryIntAxis + secondaryModifier
        return True, _primaryIntAxis, _secondaryIntAxis

    def CheckForRepeatingSprite(self, xRaySquare, zRaySquare): #Makes sure the same sprite isn't recorded twice
        for i in self.screen.spriteArray:
            if (i.x == xRaySquare and i.z == zRaySquare):
                return False
        return True

currentMap = Map(assetPath + "Map.txt") #Creates map, screen, and player classes
screen = Screen(assetPath, root)
player = Player(currentMap, screen)

root.bind("<Up>", player.Move) #Binds keys to movement and screen configuration
root.bind("<Down>", player.Move)
root.bind("<Left>", player.Move)
root.bind("<Right>", player.Move)
root.bind("<Configure>", screen.Configuration)

player.Sense() #Performs initial sense check

root.mainloop() #Tkinter mainloop
