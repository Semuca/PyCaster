import math
import os
from tkinter import *

assetPath = os.getcwd() + "/Assets/"

root = Tk()

class Screen:
    def __init__(self, assetPath, root):
        self.anglesPerScan = 1
        self.assetPath = assetPath
        self.canvas = Canvas(root, highlightthickness = 0)
        self.canvas.image_names = []
        self.canvas.pack(expand = True, fill = BOTH)
        self.fovAngle = 100
        self.spriteArray = []
        self.wallArray = []
        self.windowHeight = 0
        self.windowWidth = 0

    def DrawLines(self):
        self.canvas.delete("all")
        _width = (self.windowWidth * (self.anglesPerScan / self.fovAngle)) + 1
        for i in range(len(self.wallArray)):
            _images = []
            for j in self.spriteArray:
                if (i in j.segments and j.distance < self.wallArray[i].distance):
                    if (len(_images) == 0):
                        _images.append(j)
                    else:
                        for k in range(len(_images)):
                            if (_images[k].distance < j.distance):
                                _images.insert(k, j)
            _tempX = int((((i + 0.5) * self.anglesPerScan) / self.fovAngle) * self.windowWidth)
            _tempHeight = int(self.windowHeight / (self.wallArray[i].distance + 1))
            _referenceImg = PhotoImage(file = self.assetPath + "Textures/" + str(self.wallArray[i].id) + ".png")
            self.DrawColumn(_tempHeight, _referenceImg, self.wallArray[i].segment, _tempX, _width)
            for j in _images:
                _spriteHeight = int(self.windowHeight / (j.distance + 1))
                _referenceSprite = PhotoImage(file = self.assetPath + "Sprites/" + str(j.id) + ".png")
                self.DrawColumn(_spriteHeight, _referenceSprite, j.segments.index(i) / len(j.segments), _tempX, _width)

    def DrawColumn(self, height, img, segment, x, width):
        _img = PhotoImage(width = int(width), height = height)
        _colours = []
        for i in range(img.height()):
            r, g, b = img.get(int(segment * (img.width() - 1)), i)
            _r = format(r, "02X")
            _g = format(g, "02X")
            _b = format(b, "02X")
            _colour = "#" + str(_r) + str(_g) + str(_b)
            for j in range(int((height / img.height()) * (i + 1) - len(_colours))):
                _colours.append(_colour)
        _img.put(_colours, to = (0, 0, int(width), int(((i + 1) / img.height()) * height)))
        self.canvas.create_image(x, int(self.windowHeight / 2), image = _img)
        self.canvas.image_names.append(_img)

    def Configuration(self, event):
        self.windowHeight = event.height
        self.windowWidth = event.width
        self.DrawLines()

class WallSegment:
    def __init__(self, distance, colliderID, segment):
        self.distance = distance
        self.id = colliderID
        self.segment = segment

class Sprite:
    def __init__(self, angle, distance, fov, spriteID, x, z):
        self.angle = int(angle + (fov / 2))
        self.distance = distance
        self.id = spriteID
        self.segments = []
        _segments = int(fov / (distance + 1))
        for i in range(-int(_segments / 2), int(_segments / 2) + _segments):
            self.segments.append(self.angle + i)
        self.x = x
        self.z = z

class Map:
    def __init__(self, path):
        self.colliderIDs = [2, 3]
        self.spriteIDs = [4]
        _rawData = open(path, "r")
        self.data = []
        for i in _rawData.readlines():
            i = i.replace("\n", "")
            _tempArray = []
            for j in range(len(i)):
                _tempArray.append(int(i[j]))
            self.data.append(_tempArray)
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                if (self.data[i][j] == 1):
                    self.xSpawn = j
                    self.zSpawn = i
                    break

class Player:
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

    def Move(self, event):
        if (event.keysym == "Up" or event.keysym == "Down"):
            if (event.keysym == "Down"):
                _speedModifier = 1
            else:
                _speedModifier = -1
            _xPos = self.xPos + math.sin(math.radians(360 - self.rotation)) * _speedModifier * self.speed
            _zPos = self.zPos + math.cos(math.radians(360 - self.rotation)) * _speedModifier * self.speed
            self.xPos, self.xSquare = self.SquareCheck(self.xSquare, _xPos, 1, 0)
            self.zPos, self.zSquare = self.SquareCheck(self.zSquare, _zPos, 0, 1)
        if (event.keysym == "Left"):
            self.rotation = self.rotation - self.rotationSpeed
        elif (event.keysym == "Right"):
            self.rotation = self.rotation + self.rotationSpeed
        if (self.rotation < 0):
            self.rotation = 360 + self.rotation
        elif (self.rotation >= 360):
            self.rotation = self.rotation - 360
        if (event.keysym == "Up" or event.keysym == "Down" or event.keysym == "Left" or event.keysym == "Right"):
            self.Sense()

    def SquareCheck(self, square, pos, modifierX, modifierZ):
        if (square - pos > 0.5):
            return self.SquareChange(square, pos, -modifierX, -modifierZ)
        elif (square - pos < -0.5):
            return self.SquareChange(square, pos, modifierX, modifierZ)
        else:
            return pos, square

    def SquareChange(self, square, pos, modifierX, modifierZ):
        _array = self.map.data[self.zSquare + modifierZ]
        if (_array[self.xSquare + modifierX] in self.map.colliderIDs):
            return square + ((modifierX + modifierZ) / 2), square
        else:
            return pos, square + modifierX + modifierZ

    def Sense(self):
        self.screen.spriteArray = []
        self.screen.wallArray = []
        _xPosInSquare = self.xPos - (self.xSquare - 0.5)
        _zPosInSquare = self.zPos - (self.zSquare - 0.5)
        for i in range(-int(self.screen.fovAngle / (2 * self.screen.anglesPerScan)), int(self.screen.fovAngle / (2 * self.screen.anglesPerScan))):
            _xRaySquare = self.xSquare
            _zRaySquare = self.zSquare
            _rayAngle = self.rotation + (i * self.screen.anglesPerScan)
            if (_rayAngle < 0):
                _rayAngle = _rayAngle + 360
            elif (_rayAngle >= 360):
                _rayAngle = _rayAngle - 360
            _tan = math.tan(math.radians(_rayAngle))
            if (_rayAngle > 0 and _rayAngle < 180):
                _modifierX = 1
            elif (_tan == 0):
                _modifierX = 0
            else:
                _modifierX = -1
            if (_rayAngle > 90 and _rayAngle < 270):
                _modifierZ = 1
            elif (_tan == None):
                _modifierZ = 0
            else:
                _modifierZ = -1
            _xIntX, _xIntZ, _zIntX, _zIntZ = self.FindInitialSquareIntercepts(_rayAngle, _tan, _xPosInSquare, _zPosInSquare)
            _isRaytracing = True
            while _isRaytracing == True:
                if (_zIntX == None or abs(self.xPos - _xIntX) <= abs(self.xPos - _zIntX)):
                    _zRaySquare = _zRaySquare + _modifierZ
                    _isRaytracing, _xIntX, _xIntZ = self.CheckIntercept(i, _xRaySquare, _zRaySquare, _xIntX, _xIntZ, _xRaySquare, _zRaySquare, _xIntX, _xIntZ, _modifierX * abs(_tan), _modifierZ)
                elif (_xIntX == None):
                    _xRaySquare = _xRaySquare + _modifierX
                    _isRaytracing, _zIntZ, _zIntX = self.CheckIntercept(i, _xRaySquare, _zRaySquare, _zIntX, _zIntZ, _zRaySquare, _xRaySquare, _zIntZ, _zIntX, _modifierZ, _modifierX)
                else:
                    _xRaySquare = _xRaySquare + _modifierX
                    _isRaytracing, _zIntZ, _zIntX = self.CheckIntercept(i, _xRaySquare, _zRaySquare, _zIntX, _zIntZ, _zRaySquare, _xRaySquare, _zIntZ, _zIntX, _modifierZ * abs(1 / _tan), _modifierX)
        self.screen.DrawLines()

    def FindInitialSquareIntercepts(self, angle, tanAngle, xPosInSquare, zPosInSquare):
        if (angle > 0 and angle < 180):
            _zIntX = self.xSquare + 0.5
            _zIntZ = self.zPos - ((1 - xPosInSquare) / tanAngle)
        elif (tanAngle == 0):
            _zIntX = None
            _zIntZ = None
        else:
            _zIntX = self.xSquare - 0.5
            _zIntZ = self.zPos + (xPosInSquare / tanAngle)
        if (angle > 90 and angle < 270):
            return self.xPos - (1 - zPosInSquare) * tanAngle, self.zSquare + 0.5, _zIntX, _zIntZ
        elif (tanAngle == None):
            return None, None, _zIntX, _zIntZ
        else:
            return self.xPos + zPosInSquare * tanAngle, self.zSquare - 0.5, _zIntX, _zIntZ

    def CheckIntercept(self, rawAngle, xRaySquare, zRaySquare, intX, intZ, primaryRaySquareAxis, secondaryRaySquareAxis, primaryIntAxis, secondaryIntAxis, primaryModifier, secondaryModifier):
        _tempArray = self.map.data[zRaySquare]
        for j in self.map.colliderIDs:
            if (_tempArray[xRaySquare] == j):
                _distance = math.sqrt((self.xPos - intX)**2 + (self.zPos - intZ)**2)
                self.screen.wallArray.append(WallSegment(_distance * math.cos(math.radians(rawAngle * self.screen.anglesPerScan)), j, 0.5 + primaryIntAxis - primaryRaySquareAxis))
                return False, primaryIntAxis, secondaryIntAxis
        for j in self.map.spriteIDs:
            if (_tempArray[xRaySquare] == j):
                if (self.CheckForRepeatingSprite(xRaySquare, zRaySquare) == True):
                    _distanceX = self.xPos - xRaySquare
                    _distanceZ = self.zPos - zRaySquare
                    _distance = math.sqrt((_distanceX)**2 + (_distanceZ)**2)
                    if (_distanceX < 0 and _distanceZ >= 0):
                        _angle = math.degrees(math.asin(abs(_distanceX) / _distance))
                    elif (_distanceX < 0 and _distanceZ < 0):
                        _angle = 90 + math.degrees(math.asin(abs(_distanceZ) / _distance))
                    elif (_distanceX >= 0 and _distanceZ < 0):
                        _angle = 180 + math.degrees(math.asin(abs(_distanceX) / _distance))
                    else:
                        _angle = 270 + math.degrees(math.asin(abs(_distanceZ) / _distance))
                    self.screen.spriteArray.append(Sprite(_angle - self.rotation, _distance * math.cos(math.radians(rawAngle * self.screen.anglesPerScan)), self.screen.fovAngle, j, xRaySquare, zRaySquare))
                    break
        _primaryIntAxis = primaryIntAxis + primaryModifier
        _secondaryIntAxis = secondaryIntAxis + secondaryModifier
        return True, _primaryIntAxis, _secondaryIntAxis

    def CheckForRepeatingSprite(self, xRaySquare, zRaySquare):
        for i in self.screen.spriteArray:
            if (i.x == xRaySquare and i.z == zRaySquare):
                return False
        return True

currentMap = Map(assetPath + "Map.txt")
screen = Screen(assetPath, root)
player = Player(currentMap, screen)

root.bind("<Up>", player.Move)
root.bind("<Down>", player.Move)
root.bind("<Left>", player.Move)
root.bind("<Right>", player.Move)
root.bind("<Configure>", screen.Configuration)

player.Sense()

root.mainloop()
