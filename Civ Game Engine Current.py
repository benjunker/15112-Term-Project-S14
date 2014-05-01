#Benjamin Junker
#Andrew ID: bjunker

#Note: This game is intended to run in 1280x720 resolution.
#Note: Failure to do say may result in subpar gameplay

from Tkinter import *
import random
import math
from fractions import Fraction
import time

class Animation(object): #From Kosbie email;expanded sligtly from stock code
	def mousePressed(self, event): pass
	def keyPressed(self, event): pass
	def timerFired(self): pass
	def init(self): pass
	def redrawAll(self): pass
	def mouseReleased(self,event): pass #added mouseReleased
	def mouseMotion(self,event): pass #added
	
	#removed many of the comments
	def run(self,rows=10,cols=20,width=1280,height=720):#new args
		root = Tk(className=" Civilization ")
		self.canvasWidth,self.canvasHeight = width,height
		self.rows,self.cols = rows,cols
		self.canvas = Canvas(root, width=width, height=height)
		self.canvas.configure(bd = 0, highlightthickness = 0) #added
		self.canvas.pack()
		def redrawAllWrapper():
			self.canvas.delete(ALL)
			self.redrawAll()
		def mousePressedWrapper(event):
			self.mousePressed(event)
			#redrawAllWrapper()
		def mouseReleasedWrapper(event): #NEW
			self.mouseReleased(event)
			#redrawAllWrapper()
		def keyPressedWrapper(event):
			self.keyPressed(event)
			#redrawAllWrapper()
		def mouseMotionWrapper(event): #NEW
			self.mouseMotion(event)
			#redrawAllWrapper()
		self.canvas.bind("<Motion>", mouseMotionWrapper)
		root.bind("<Button-1>", mousePressedWrapper)
		root.bind("<Key>", keyPressedWrapper)
		root.bind("<B1-ButtonRelease>",mouseReleasedWrapper)
		self.timerFiredDelay = 15 # milliseconds
		def timerFiredWrapper():
			self.timerFired()
			redrawAllWrapper()
			self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
		self.init()
		timerFiredWrapper()
		root.mainloop()

class Interactable(object): #--> eg - Warriors, Settler, Cities, etc
	interSet = set()

	#interDict = {}

	def __init__(self):
		Interactable.interSet.add(self)
		xPos,yPos = self.xPos,self.yPos
		#try: Interactable.interDict[(xPos,yPos)].add(self)
		#except: Interactable.interDict[(xPos,yPos)] = set([self])

class Unit(Interactable): #generic unit class
	unitDict = {}

	unitSet = set()

	effectiveDict = {"very ineffective" : 2,
					 "ineffective"      : 2.5,
					 "neutral"          : 3,
					 "effective"        : 3.5,
					 "very effective"   : 4}
					 #quantifies effectiveness

	normalDict = {0 : "very ineffective",
				  1 : "very ineffective",
				  2 : "ineffective",
				  3 : "ineffective",
				  4 : "neutral",
				  5 : "neutral",
				  6 : "effective",
				  7 : "effective",
				  8 : "very effective",
				  9 : "very effective"}
				  #probability mass function of efectiveness for a normal unit

	eliteDict = {0 : "very ineffective",
				 1 : "ineffective",
				 2 : "ineffective",
				 3 : "neutral",
				 4 : "neutral",
				 5 : "effective",
				 6 : "effective",
				 7 : "effective",
				 8 : "very effective",
				 9 : "very effective"}
				 #probability mass function of effectiveness for an elite unit

	masterDict = {0 : "ineffective",
				  1 : "ineffective",
				  2 : "neutral",
				  3 : "neutral",
				  4 : "neutral",
				  5 : "effective",
				  6 : "effective",
				  7 : "very effective",
				  8 : "very effective",
				  9 : "very effective"}
				  #probability mass function of effectiveness for a master unit

	rankDict = {"normal" : normalDict,
				"elite"  : eliteDict,
				"master" : masterDict}
				#dictionary referring the ranking to the correct effectiveness

	reverseEffectiveDict = {1 : "very ineffective",
							2 : "ineffective",
							3 : "neutral",
							4 : "effective",
							5 : "very effective"}
							#dictionary that qualifies an efectiveness number

	def __init__(self,team,moves,xPos,yPos,sight,
		state="neutral",selected=False): #initializes units
		Unit.unitSet.add(self)
		try: Unit.unitDict[(xPos,yPos)].add(self)
		except: Unit.unitDict[(xPos,yPos)] = set([self])
		#self.atk = atk #attacking power
		#self.df = df #defending ability
		#self.type = typee #purpose of unit (ie-attack,build,settle,etc)
		self.team = team #which player/team controls the unit
		#self.mode = mode #mode of attack (if at all) (ie - ground,range,etc)
		self.moves = moves #number of moves per turn
		self.xPos = xPos #current x position --> an index?
		self.yPos = yPos # current y position --> and index?
		self.sight = sight #amount of tiles away, that a unit can "see"
		#self.health = health #health remaining
		self.state = state #game state (ie-neutral,fortitified,etc)
		self.defaultMoves = moves #num of moves per turn --> to reset
		self.selected = selected
		self.battled = False
		super(Unit,self).__init__()

	def move(self,indexA,indexB,moveDict):
		if (indexA,indexB) not in moveDict: return
		else:
			if (indexA,indexB) in City.cityDict:
				if not City.cityDict[(indexA,indexB)]:
					Unit.unitDict[(self.xPos,self.yPos)].remove(self)
					self.xPos,self.yPos = indexA,indexB
					try: Unit.unitDict[(self.xPos,self.yPos)].add(self)
					except: Unit.unitDict[(self.xPos,self.yPos)] = set([self])
					if len(Unit.unitDict[(self.xPos,self.yPos)])>1: assert(
						False)
					self.moves -= moveDict[(self.xPos,self.yPos)]
			else:
				Unit.unitDict[(self.xPos,self.yPos)].remove(self)
				self.xPos,self.yPos = indexA,indexB
				try: Unit.unitDict[(self.xPos,self.yPos)].add(self)
				except: Unit.unitDict[(self.xPos,self.yPos)] = set([self])
				if len(Unit.unitDict[(self.xPos,self.yPos)])>1: assert(
					False)
				self.moves -= moveDict[(self.xPos,self.yPos)]

	def reset(self):
		#to reset moves each turn
		self.moves = self.defaultMoves
		self.battled = False

	def battleSuccess(self): pass
	def battle(self): pass
	def attack(self): pass
	def retaliate(self): pass

class Marine(Unit):
	def  __init__(self,team,moves,xPos,yPos,capactiy,sight=2):
		super(Marine,self).__init__(team,moves,xPos,yPos,sight)
		self.capactiy = capactiy
		self.loaded = False
		self.atCapacity = False
		self.unitSet = set()
		self.currentCapacity = 0

	def load(self,other):
		if not(isinstance(other,Military) or isinstance(other,Support)):
			print "Tried to load a non-unit!"
			return
		if not self.atCapacity:
			if other.moves>0:
				other.moves = 0
				Unit.unitSet.remove(other)
				Unit.unitDict[(other.xPos,other.yPos)].remove(other)
				other.xPos,other.yPos = None,None
				self.unitSet.add(other)
				self.currentCapacity = len(self.unitSet)
				self.capacityTest()

	def capacityTest(self):
		if self.currentCapacity > 0: self.loaded = True
		else: self.loaded = False
		if self.currentCapacity == self.capacity: self.atCapacity = True
		else: self.atCapacity = False

	def unload(self):
		posAdj = [(+1,-1),(+2,+0),(+1,+1),(-1,+1),(-2,+0),(-1,-1)]
		n=1
		basePos = (self.xPos,self.yPos)
		relPosAdj = [(basePos[0]+adj[0],basePos[1]+adj[1]) for adj in posAdj]
		cont = False
		for pos in relPosAdj:
			if pos[0] >= 0 and pos[1] >= 0:
				if Tile.terrainDict[pos] == "land":
					cont = True
		if cont:
			while self.loaded and n<5:
			#	newPosAdj = []
			#	for adj in posAdj:
			#		addend = []
			#		for element in adj:
			#			addend.append(n*element)
			#		addend = tuple(addend)
			#		newPosAdj.append(addend)
				#posPlace = []
				boundingBox = self.findBoundingBoxAttackTiles(self.xPos,
					self.yPos,n)
				newPosAdj = self.findDiamondAttackTilesGivenSet(self.xPos,
					self.yPos,n,boundingBox)
				#for adj in newPosAdj:
				#	addend = (basePos[0]+adj[0],basePos[1]+adj[1])
				#	if addend[0]>=0 and addend[1]>=0:
				#		posPlace.append(addend)
				#print posPlace
				#count = -1
				for place in newPosAdj:
					if len(self.unitSet) <= 0: continue
					#count += 1
					#print " "*count + str(place) + "1"
					if place in Tile.terrainDict:
					#	print " "*count + str(place) + "2"
						if Tile.terrainDict[place] == "land":
					#		print " "*count + str(place) + "3"
							if len(self.unitSet)> 0:
								if place not in City.cityDict:
									if place not in Unit.unitDict:
						#			print " "*count + str(place) + "4"
										unitList = list(self.unitSet)
										unit = unitList.pop()
										unit.xPos = place[0]
										unit.yPos = place[1]
										Unit.unitSet.add(unit)
										try: Unit.unitDict[(unit.xPos,unit.yPos)].add(unit)
										except: Unit.unitDict[(unit.xPos,
											unit.yPos)] = set([unit])
									elif place in Unit.unitDict:
										if not Unit.unitDict[place]:
											unitList = list(self.unitSet)
											unit = unitList.pop()
											unit.xPos = place[0]
											unit.yPos = place[1]
											Unit.unitSet.add(unit)
											try: Unit.unitDict[(unit.xPos,unit.yPos)].add(unit)
											except: Unit.unitDict[(unit.xPos,
												unit.yPos)] = set([unit])
									#unit.reset(x)
									try: self.unitSet = set(unitList)
									except: pass
								elif not City.cityDict[place]:
									if place not in Unit.unitDict:
						#			print " "*count + str(place) + "4"
										unitList = list(self.unitSet)
										unit = unitList.pop()
										unit.xPos = place[0]
										unit.yPos = place[1]
										Unit.unitSet.add(unit)
										try: Unit.unitDict[(unit.xPos,unit.yPos)].add(unit)
										except: Unit.unitDict[(unit.xPos,
											unit.yPos)] = set([unit])
									elif place in Unit.unitDict:
										if not Unit.unitDict[place]:
											unitList = list(self.unitSet)
											unit = unitList.pop()
											unit.xPos = place[0]
											unit.yPos = place[1]
											Unit.unitSet.add(unit)
											try: Unit.unitDict[(unit.xPos,unit.yPos)].add(unit)
											except: Unit.unitDict[(unit.xPos,
												unit.yPos)] = set([unit])
									#unit.reset(x)
									try: self.unitSet = set(unitList)
									except: pass
				n += 1
		self.currentCapacity = len(self.unitSet)
		self.capacityTest()

	def findBoundingBoxAttackTiles(self,indexA,indexB,n):
		boundingBoxSet = set()
		for xPos in xrange(max(indexA-2*n,0),indexA+2*n+1):
			for yPos in xrange(max(indexB-n,0),indexB+n+1):
				if xPos%2 == yPos%2:
					boundingBoxSet.add((xPos,yPos))
		return boundingBoxSet

	def findDiamondAttackTilesGivenSet(self,indexA,indexB,n,boundingBoxSet):
		legalMoveSet = set()
		for move in boundingBoxSet:
			(moveX,moveY) = move
			deltaX = abs(moveX-indexA)
			deltaY = abs(moveY-indexB)
			deltaTotal = (deltaX+deltaY)/2
			deltaMax = n
			if deltaMax>=deltaTotal:
				legalMoveSet.add(move)
		return legalMoveSet

class Ship(Marine):
	moves = 4
	capacity = 3

	def __init__(self,team,xPos,yPos):
		moves,capacity = Ship.moves,Ship.capacity
		super(Ship,self).__init__(team,moves,xPos,yPos,capacity)

class Military(Unit):
	#for military (attacking) units
	#three types (maybe only two) Land, Range, and (maybe) Air
	def __init__(self,atk,df,team,moves,xPos,yPos,sight,health,rank="normal"):
		super(Military,self).__init__(team,moves,xPos,yPos,sight)
		self.atk = atk
		self.df = df
		self.health = health
		self.rank = rank #current ability/prowess (normal, elite, or master)
		self.exp = 0 #current amount of experience

	def battleSuccess(self):#determines effectiveness in battle
		luck = random.randint(0,9)#for pmf
		success = Unit.rankDict[self.rank][luck]#gets qualified success
		successNumber = Unit.effectiveDict[success] #quantifies success
		return successNumber

	def battle(self,other,moveDict): #battle enginge, for military units
		if isinstance(other,Military):
			selfSuccess = self.battleSuccess()
			otherSuccess = other.battleSuccess()
			damageDealt = self.attack(other,selfSuccess,otherSuccess)
			damageRetaliated = other.retaliate(self,otherSuccess,selfSuccess)
			self.checkLife()
			other.checkLife()
			self.battled = True
			self.moves = 0
			return (damageDealt,damageRetaliated,self.health,other.health,
				self.battled)
		elif isinstance(other,Support):
			other.lose(self)
			self.battled = True
			self.moves = 0
			return 0,0,None,None,self.battled
		#health is temporarily displayed in console window
		#with the attacker's health first

	def checkLife(self): #health is temporarily displayed in console window
		if self.health <= 0:
			Unit.unitDict[(self.xPos,self.yPos)].remove(self)
			Unit.unitSet.remove(self)

	def attack(self,other,selfSuccess,otherSuccess): #dealing damage
		otherBefore = other.health
		damage = 3*selfSuccess*self.atk-otherSuccess*other.df
		other.health = other.health - int(damage) if damage>0 else other.health
		otherAfter = other.health
		self.damage = damage if damage>0 else 0
		return damage if damage>0 else 0
		#health is temporarily displayed in the console window
		#attacker's health first

	def retaliate(self,other,selfSuccess,otherSuccess): #retaliating after atk
		otherBefore = other.health
		damage = (3*selfSuccess*self.atk-otherSuccess*other.df)/2
		other.health = other.health - int(damage) if damage>0 else other.health
		otherAfter = other.health
		self.damage = damage if damage>0 else 0
		return damage if damage>0 else 0
		#health is temporarily displayed in the console window
		#attacker's health first

class Land(Military):
	def battle(self,other,moveDict):
		if (other.xPos,other.yPos) in moveDict:
			if moveDict[(other.xPos,other.yPos)] == 1:
				return super(Land,self).battle(other,moveDict)
			else: return None,None,None,None,False
		else: return None,None,None,None,False

	def retaliate(self,other,selfSuccess,otherSuccess):
		if isinstance(other,Land):
			return super(Land,self).retaliate(other,selfSuccess,otherSuccess)
		else:
			self.damage = 0
			return 0

class Warrior(Land):
	atk = df = moves = sight = 2 #arbitrary

	def __init__(self,team=None,xPos=None,yPos=None,health=10):
		atk,df,moves,sight = Warrior.atk,Warrior.df,Warrior.moves,Warrior.sight
		super(Warrior,self).__init__(atk,df,team,moves,xPos,yPos,sight,health)

	#def __str__(self):
		#print "atk: " + str(self.atk)
		#print "df: " + str(self.df)
		#print "moves: " + str(self.moves)
		#print "sight: " + str(self.sight)
		#print "health: " + str(self.health)
		#print "rank: " + str(self.rank)
		#print "exp: " + str(self.exp)
		#print type(self)
		#print "Land: " +  str(isinstance(self,Land))
		#print "Military: " + str(isinstance(self,Military))
		#print "Unit: " + str(isinstance(self,Unit))
		#return ""

class Swordsman(Land):
	atk = df = 3
	sight = moves = 2

	def __init__(self,team=None,xPos=None,yPos=None,health=100):
		atk,df,sight,moves = (Swordsman.atk,Swordsman.df,Swordsman.sight,
			Swordsman.moves)
		super(Swordsman,self).__init__(atk,df,team,moves,xPos,yPos,sight,
			health)

class Range(Military):
	def __init__(self,atk,df,team,moves,xPos,yPos,sight,health,ranged=2):
		self.range = ranged
		super(Range,self).__init__(atk,df,team,moves,xPos,yPos,sight,health)

	def findBoundingBoxAttackTiles(self,indexA,indexB,n):
		boundingBoxSet = set()
		for xPos in xrange(max(indexA-2*n,0),indexA+2*n+1):
			for yPos in xrange(max(indexB-n,0),indexB+n+1):
				if xPos%2 == yPos%2:
					boundingBoxSet.add((xPos,yPos))
		return boundingBoxSet

	def findDiamondAttackTilesGivenSet(self,indexA,indexB,n,boundingBoxSet):
		legalMoveSet = set()
		for move in boundingBoxSet:
			(moveX,moveY) = move
			deltaX = abs(moveX-indexA)
			deltaY = abs(moveY-indexB)
			deltaTotal = (deltaX+deltaY)/2
			deltaMax = n
			if deltaMax>=deltaTotal:
				legalMoveSet.add(move)
		return legalMoveSet
		#rectangle plus diamond makes hexagon

	def battle(self,other,moveDict): #fix so ranged attacks work
		indexA,indexB,n = self.xPos,self.yPos,self.range
		self.attackSet = self.findDiamondAttackTilesGivenSet(indexA,indexB,
			n,self.findBoundingBoxAttackTiles(indexA,indexB,n))
		if (other.xPos,other.yPos) in self.attackSet:
			print "!"
			return super(Range,self).battle(other,moveDict)
		else:
			return None,None,None,None,False

class Archer(Range):
	atk = df = moves = sight = 2 #arbitrary

	def __init__(self,team=None,xPos=None,yPos=None,health=100,ranged=None):
		atk,df,moves,sight=Archer.atk,Archer.df,Archer.moves,Archer.sight
		if not ranged:
			super(Archer,self).__init__(atk,df,team,moves,xPos,yPos,sight,
				health)
		else:
			super(Archer,self).__init__(atk,df,team,moves,xPos,yPos,sight,
				health,ranged)

class Support(Unit):
	def lose(self,other): #always lose battles to military
		assert isinstance(other,Military)
		if self.state == "neutral":
			self.team = other.team

class Settler(Support):
	moves = sight = 2 #arbitrary

	def  __init__(self,team=None,xPos=None,yPos=None):
		moves,sight = Settler.moves,Settler.sight
		super(Settler,self).__init__(team,moves,xPos,yPos,sight)

	def settle(self): #make a city!
		Unit.unitDict[(self.xPos,self.yPos)].remove(self)
		Unit.unitSet.remove(self)
		City(self.team,self.xPos,self.yPos)

	def battle(self,a,b):
		return 0,0,0,0,False

class Tile(object): #tiles that make up the board
	tileSet = set() #list of all tiles to iterate through

	tileDict = {}

	landDict = {}

	waterDict = {}

	terrainDict = {}

	def __init__(self,colPos,rowPos,r,adj60,left,top,adj30):#inits tiles
		cx = left + adj60 + colPos * adj60
		cy = top + r if rowPos%2 == 0 else top+2*r+adj30
		cy += rowPos/2*2*(r+adj30)
		self.cx,self.cy,self.r = cx,cy,r
		self.indexA,self.indexB = colPos,rowPos
		self.terrain = self.seedRandomTerrain(self.indexA,self.indexB)
		if self.terrain == "land":
			Tile.landDict[(self.indexA,self.indexB)] = self
		elif self.terrain == "water":
			Tile.waterDict[(self.indexA,self.indexB)] = self
		Tile.terrainDict[(self.indexA,self.indexB)] = self.terrain
		Tile.tileSet.add(self)
		Tile.tileDict[(self.indexA,self.indexB)] = self

	def seedRandomTerrain(self,indexA,indexB):
		randomSeed = random.randint(0,24)
		#if randomSeed<=0: return "water"
		if (indexA,indexB) in set([(1,1),(2,2),(58,28),(57,27)]): #HARDCODED
			return "land"
		if (indexA,indexB) == (1,7): #HARDCODED
			return "water"
		if 0<randomSeed<=1: return "land"
		else: return None
		#surroundingTiles = set([(indexA+2,indexB),(indexA-2,indexB),
		#(indexA+1,indexB+1),(indexA-1,indexB-1),
		#(indexA-1,indexB+1),(indexA+1,indexB-1)])
		#surroundingArea = []
		#for tileIndex in surroundingTiles:
		#	if tileIndex in Tile.terrainDict:
		#		surroundingArea.append(Tile.terrainDict[tileIndex])
		#weight = (.5+(surroundingArea.count("land")-
		#	surroundingArea.count("water")/float(len(surroundingArea)))*.97*.5 
		#	if len(surroundingArea)>0 else .4)
		#tileDistrNo = random.triangular(0,1,weight)
		#if tileDistrNo<.5: return "water"
		#else: return "land"

class City(Interactable): #Cities make units
	cityDict = {}

	citySet = set()

	productionOptions = set() #how to get production options...?
							  #--> will eventually be able to be informed by
							  #the science tree

	productionCost = {"Warrior"   : 7,
					  "Settler"   : 10,
					  "Archer"    : 8,
					  "Swordsman" : 12,
					  "Ship"      : 9} #create this before the game
						  #ex --> {"Warrior" : 2}

	def __init__(self,team,xPos,yPos,health=200):
		#population,area of influence,
		#attack, defense, health?
		City.citySet.add(self)
		try: City.cityDict[(xPos,yPos)].add(self)
		except: City.cityDict[(xPos,yPos)] = set([self])
		self.team = team
		self.xPos = xPos
		self.yPos = yPos
		self.currentProduction = 0
		self.selected = False
		self.health = health
		super(City,self).__init__()

	def determineProductionLevel(self):
		cityCount = 0
		for city in City.citySet:
			if city.team == self.team:
				cityCount += 1
		prodDict = {1 : 2,
					2 : 2.5,
					3 : 3,
					4 : 2.5,
					5 : 2}
		if cityCount in prodDict:
			return prodDict[cityCount]
		else:
			return 1.5

	def produceShields(self): #increase production ability. not on Tkinter yet
		productionLevel = self.determineProductionLevel()
		self.currentProduction += productionLevel if productionLevel > 0 else 0

	def createUnit(self,unitType): #creates any unit, right next to the city
		posAdj = [(+1,-1),(+2,+0),(+1,+1),(-1,+1),(-2,+0),(-1,-1)]
		unitCost = City.productionCost[unitType]
		if unitCost <= self.currentProduction:
			for adj in posAdj:
				xPos = self.xPos + adj[0]
				yPos = self.yPos + adj[1]
				try: city = City.cityDict[(xPos,yPos)]
				except: city = None
				try: unit = Unit.unitDict[(xPos,yPos)]
				except: unit = None
				if not(city or unit) and (xPos,yPos) in Tile.tileDict:
					marineString = ["Ship"]
					if not unitType in marineString:
						if Tile.terrainDict[(xPos,yPos)] == "land":
							createStr = "%s(\"%s\",%d,%d)" % (unitType,self.team,
								xPos,yPos)
							self.currentProduction -= unitCost
							eval(createStr)
							return
					else: #ships are currently spawning on land
						if Tile.terrainDict[(xPos,yPos)] == "water":
							createStr = "%s(\"%s\",%d,%d)" % (unitType,self.team,
								xPos,yPos)
							self.currentProduction -= unitCost
							eval(createStr)
							return

	def takeDamage(self,unit):
		luck = random.randint(0,9)#for pmf
		success = Unit.rankDict[unit.rank][luck]#gets qualified success
		successNumber = Unit.effectiveDict[success] #quantifies success
		cityDefense = 3.5
		cityLuck = 3
		damage = 3*successNumber*unit.atk-cityDefense*cityLuck
		self.health = self.health - int(damage) if damage>0 else self.health
		unit.moves = 0
		unit.battled = True
		self.checkLife()
		return int(damage) if damage > 0 else 0

	def checkLife(self):
		if self.health <= 0:
			City.cityDict[(self.xPos,self.yPos)].remove(self)
			City.citySet.remove(self)

	def reset(self):
		self.health = int(self.health*1.05) if self.health*1.05<200 else 200

class Civilization(Animation): #basis of the "board" and how things will move

	def mouseMotion(self,event):
		self.image = self.start
		ctrl  = ((event.state & 0x0004) != 0)
		shift = ((event.state & 0x0001) != 0)
		capsLock = ((event.state & 0x0002) != 0)
		command = ((event.state & 0x0008) != 0)
		alt = ((event.state & 0x0010) != 0)
		fn = ((event.state & 0x0040) != 0)
		if not(self.splashScreen) and not(self.help):
			self.lastA,self.lastB = self.motionIndexA,self.motionIndexB
			indexA,indexB = self.calcMousePosition(event)
			if self.lastA != indexA and self.lastB != indexB:
				self.baseTime = time.time()
			self.motionIndexA = indexA
			self.motionIndexB = indexB
		elif self.splashScreen and not(self.help):
			if self.mouseRelease and not self.mousePress:
				if 485<=event.x<=790: #HARDCODED
					if 255<= event.y<=340: #HARDCODED
						self.image = self.playHover
					elif 420<=event.y<=505: #HARDCODED
						self.image = self.helpHover
			elif not self.mouseRelease and self.mousePress:
				if 485<=event.x<=790: #HARDCODED
					if 255<= event.y<=340: #HARDCODED
						self.image = self.playClick
					elif 420<=event.y<=505: #HARDCODED
						self.image = self.helpClick
		self.mseX = event.x
		self.mseY = event.y

	def mouseReleased(self,event):
		self.mouseRelease = True
		self.mousePress = False
		if self.image == self.playClick:
			self.image = self.playHover
			self.splashScreen = False
		elif self.image == self.helpClick:
			self.image = self.helpHover
			self.help = True

	def mousePressed(self,event):
		if self.image == self.playHover: self.image = self.playClick
		elif self.image == self.helpHover: self.image = self.helpClick
		self.mousePress = True
		self.mouseRelease = False
		if not(self.splashScreen) and not(self.help):
			indexA,indexB = self.calcMousePosition(event)
			self.unitAction(indexA,indexB)
		#if not self.selected:
		#	if (self.indexA == indexA) and (self.indexB == indexB):
		#		self.selected = True
		#else:
		#	self.indexA = indexA
		#	self.indexB = indexB
		#	self.selected = False

	def calcMousePosition(self,event):
		adj60,adj30,r = self.adj60,self.adj30,self.r
		mBlue = ((1.0*r-adj30)/adj60) #slope for blue lines
		mRed = ((1.0*adj30-r)/adj60) #slope for red lines
		#see concept "Board With Lines.png" if unclear
		mseX,mseY = event.x,event.y
		if (mseX > self.right or mseX < self.left or mseY > self.bottom or 
			mseY < self.top): return None,None
		mseX -= self.adjX
		mseY -= self.adjY
		yIntBlue = mseY - self.top - (mseX-self.left)*mBlue
		yIntRed = mseY - self.top - (mseX-self.left)*mRed
		blueNum = (yIntBlue - adj30)/(2*adj30)
		redNum = (yIntRed - adj30)/(2*adj30)
		bFloor = int(math.floor(blueNum)) #changed from specialInt
		rFloor = int(math.floor(redNum))  #^this
		#print "b: " + str(blueNum) + "," + "r: " + str(redNum)
		if (bFloor+rFloor)%3 == 0:
			if blueNum % 1 > redNum % 1: pass
		#		print "left"
			else: pass
		#		print "right"
		indexA,indexB = -1,Fraction(1,3)
		indexA += rFloor
		indexB += Fraction(1,3)*rFloor
		indexA -= bFloor
		indexB += Fraction(1,3)*bFloor
		if (bFloor+rFloor)%3 == 0:
			if blueNum % 1 > redNum % 1: indexA -= 1
			else: indexA += 1
		indexA,indexB = int(math.floor(indexA)),int(math.floor(indexB))
		return indexA,indexB

	def unitAction(self,indexA,indexB): #extension of mousePressed for unit act
		unpackedTile = self.unpackTile(indexA,indexB)
		if self.selectedUnit:
			if isinstance(unpackedTile,Unit): 
				if (unpackedTile.team == self.player and
					unpackedTile != self.selectedUnit): #switch to other unit
					if not isinstance(unpackedTile,Marine): #on your team
						self.selectUnit(unpackedTile)
					else:
						targetX,targetY = unpackedTile.xPos,unpackedTile.yPos
						curX,curY = (self.selectedUnit.xPos,
							self.selectedUnit.yPos)
						posAdj = [(+1,-1),(+2,+0),(+1,+1),(-1,+1),
						(-2,+0),(-1,-1)]
						relPosAdj = []
						for ind in posAdj:
							relPosAdj.append((ind[0]+curX,ind[1]+curY))
						if (targetX,targetY) in relPosAdj:
							unpackedTile.load(self.selectedUnit)
							self.deselectCurrentlySelectedUnit()
						else:
							self.selectUnit(unpackedTile)
				elif unpackedTile == self.selectedUnit: #clicked on same unit
					self.deselectCurrentlySelectedUnit()
				elif unpackedTile.team != self.player: #interact with other
					if (not self.selectedUnit.battled and #unit
						self.selectedUnit.moves > 0 and
						not isinstance(unpackedTile,City)):
						(damageDealt,damageRetaliated,selfHealth,otherHealth,
							battled) = self.selectedUnit.battle(unpackedTile,
							self.moveDict)
						if battled:
							self.updateStatusListFromBattle(damageDealt,
								damageRetaliated,selfHealth,otherHealth,
								unpackedTile)
						else:
							otherColor = ("Blue" if unpackedTile.team == 
								"blue" else "Red")
							otherTypeStr = str(type(unpackedTile))
							otherUnitString = (otherTypeStr
								[otherTypeStr.find(".")+1:-2])
							addend = "You cannot attack that %s %s." % (
								otherColor,otherUnitString)
							self.statusTextList.append(addend)
						self.deselectCurrentlySelectedUnit()
			elif isinstance(unpackedTile,City):
				if (not self.selectedUnit.battled and #unit
					self.selectedUnit.moves > 0 and
					unpackedTile.team != self.selectedUnit.team):
					damage = unpackedTile.takeDamage(self.selectedUnit)
					self.constructCityString(damage)
					self.deselectCurrentlySelectedUnit()
				elif unpackedTile.team == self.player:
					self.selectUnit(unpackedTile)
			elif (indexA,indexB) in self.moveDict: #move unit
				self.selectedUnit.move(indexA,indexB,self.moveDict)
				self.deselectCurrentlySelectedUnit()
			else: #clicking elsewhere
				self.deselectCurrentlySelectedUnit()
		elif self.selectedCity: #deselect city
			self.deselectCurrentlySelectedUnit()
			if isinstance(unpackedTile,Interactable):
				if unpackedTile.team == self.player:
					self.selectUnit(unpackedTile) #select other unit
		else:
			if isinstance(unpackedTile,Interactable):
				if unpackedTile.team == self.player: #select
					self.selectUnit(unpackedTile)
				elif unpackedTile.team != self.player:
					pass #DISPLAY INFORMATION...or mouse hover?

	def unpackTile(self,indexA,indexB): #get thing from tile
		if (indexA,indexB) in City.cityDict:
			if City.cityDict[(indexA,indexB)]:
				clickedTileSet = City.cityDict[(indexA,indexB)]
				clickedTileUnitList = list(clickedTileSet)
				if len(clickedTileUnitList) == 1:
					unit = clickedTileUnitList[0]
					return unit
				elif len(clickedTileUnitList) == 0:
					return
				else:
					assert(False) #figure out whether/how to deal with multiple units
		if (indexA,indexB) in Unit.unitDict:
			clickedTileSet = Unit.unitDict[(indexA,indexB)]
			clickedTileUnitList = list(clickedTileSet)
			if len(clickedTileUnitList) == 1:
				unit = clickedTileUnitList[0]
				return unit
			elif len(clickedTileUnitList) == 0:
				return
			else:
				assert(False) #figure out whether/how to deal with multiple units

	def selectUnit(self,unit):
		self.deselectCurrentlySelectedUnit()
		unit.selected = True
		if isinstance(unit,Unit): self.selectedUnit = unit
		else: self.selectedCity = unit

	def deselectCurrentlySelectedUnit(self):
		if self.selectedUnit:
			self.selectedUnit.selected = False
			self.selectedUnit = None
		elif self.selectedCity:
			self.selectedCity.selected = False
			self.selectedCity = None

	def deselectAllUnits(self): #possibly never used
		for everyUnit in Unit.unitSet:
			everyUnit.selected = False
		self.selectedUnit = None

	def keyPressed(self,event): #mainly for testing; as moving uses the mouse in game
		#keyAdj = 20
		#if not(self.splashScreen) and not(self.help):
		#	if event.keysym == "Up":
		#		if not self.bottomEdge-keyAdj<=self.bottom:
		#			self.adjY -= keyAdj
		#		else:
		#			self.adjY += self.bottom-self.bottomEdge #stop
		#			#self.adjY = 0 #wrap around
		#	elif event.keysym == "Down":
		#		if not self.topEdge+keyAdj>=self.top:
		#			self.adjY += keyAdj
		#		else:
		#			self.adjY = 0 #stop
		#			#self.adjY += self.bottom-self.bottomEdge #wrap-around
		#	elif event.keysym == "Right":
		#		if not self.leftEdge+keyAdj>=self.left:
		#			self.adjX += keyAdj
		#		else:
		#			self.adjX = 0 #stop
		#			#self.adjX += self.right-self.rightEdge #wrap-around
		#	elif event.keysym == "Left":
		#		if not self.rightEdge-keyAdj<=self.right:
		#			self.adjX -= keyAdj
		#		else:
		#			self.adjX += self.right-self.rightEdge #stop
		#			#self.adjX = 0 #wrap around
		if event.keysym == "d": self.coords = not(self.coords) #superimpose
														   #numbers over tiles
		elif event.keysym == "u": self.showUnits = not(self.showUnits)
		elif event.keysym == "space":
			if self.splashScreen:pass
			#	self.splashScreen = not(self.splashScreen)
			elif self.outcome:
				self.showDisplayOutcome = False
			else:
				self.switchPlayer()
				selfColor = "Red" if self.player=="red" else "Blue"
				addend = "It is now the %s player's turn." % selfColor
				self.statusTextList.append(addend)
				self.deselectCurrentlySelectedUnit()
				self.reset() #happens at the beginning of the turn
		elif event.keysym == "h":
			self.help = not(self.help)
		elif event.keysym == "s":
			if self.selectedCity:
				self.selectedCity.createUnit("Settler")
				self.deselectCurrentlySelectedUnit()
		elif event.keysym == "w":
			if self.selectedCity:
				self.selectedCity.createUnit("Warrior")
				self.deselectCurrentlySelectedUnit()
		elif event.keysym == "c":
			if isinstance(self.selectedUnit,Settler):
				self.selectedUnit.settle()
				self.deselectCurrentlySelectedUnit()
		elif event.keysym == "Up":
			self.countAdj += 1
		elif event.keysym == "Down":
			self.countAdj -= 1
		elif event.keysym == "Right":
			if not self.help:
				self.countAdj = 0
			self.helpPage = self.helpPage + 1 if self.helpPage < 4 else 4
		elif event.keysym == "Left":
			if not self.help:
				self.countAdj = 0
			elif self.help:
				self.helpPage = self.helpPage - 1 if self.helpPage > 0 else 0
		elif event.keysym == "r":
			self.init()
		elif event.keysym == "a":
			if self.selectedCity:
				self.selectedCity.createUnit("Archer")
				self.deselectCurrentlySelectedUnit()
		elif event.keysym == "l":
			if isinstance(self.selectedUnit,Marine):
				self.selectedUnit.unload()
				self.deselectCurrentlySelectedUnit()
		elif event.keysym == "m":
			if self.selectedCity:
				self.selectedCity.createUnit("Swordsman")
				self.deselectCurrentlySelectedUnit()
		elif event.keysym == "p":
			if self.selectedCity:
				self.selectedCity.createUnit("Ship")
				self.deselectCurrentlySelectedUnit()
		elif event.keysym == "e":
			Unit.unitDict[(self.rWar.xPos,self.rWar.yPos)].remove(self.rWar)
			Unit.unitDict[(self.rSetl.xPos,self.rSetl.yPos)].remove(self.rSetl)
			self.rWar.xPos,self.rWar.yPos = 3,1
			self.rSetl.xPos,self.rSetl.yPos = 4,2
			try: Unit.unitDict[(self.rWar.xPos,self.rWar.yPos)].add(self.rWar)
			except: Unit.unitDict[(self.rWar.xPos,self.rWar.yPos)] = set([self.rWar])
			try: Unit.unitDict[(self.rSetl.xPos,self.rSetl.yPos)].add(self.rSetl)
			except: Unit.unitDict[(self.rSetl.xPos,self.rSetl.yPos)] = set([self.rSetl])
			#Unit.unitDict[(self.rWar.xPos,self.rWar.yPos)].add(self.rWar)
			#Unit.unitDict[(self.rSetl.xPos,self.rSetl.yPos)].add(self.rSetl)

		#print self.indexA,self.indexB

	def switchPlayer(self):
		if self.player == "blue": self.player = "red"
		else: self.player = "blue"

	def reset(self):
		for unit in Unit.unitSet:
			if unit.team == self.player:
				unit.reset()
		for city in City.citySet:
			if city.team == self.player:
				city.produceShields()
				city.reset()

	def drawBoard(self): #for each tile object, draws a hexagon
		adj60,adj30,left,top,r =self.adj60,self.adj30,self.left,self.top,self.r
		rows,cols = self.rows-1,self.cols-1
		self.leftEdge = left+self.adjX
		self.rightEdge = left+2*adj60+self.adjX+(self.cols-1)*adj60
		self.topEdge = top+self.adjY
		self.bottomEdge = top + r if rows%2 == 0 else top+2*r+adj30+self.adjY
		self.bottomEdge += rows/2*2*(r+adj30) + r
		self.canvas.create_rectangle(self.left-5,self.top-5,self.right+5,self.bottom+5,
			fill = "#b79e76",width=10,outline="#b79e76")
		for tile in Tile.tileSet:
			color = "#d2d2d2"
			color = "purple"
			cx,cy,r = tile.cx,tile.cy,tile.r
			cx += self.adjX
			cy += self.adjY
			if tile.terrain == "land":
				color = "#a27741"
			elif tile.terrain == "water":
				color = "#34a1d3"
			if ((self.right+2*self.adj60>cx>self.left-2*adj60) and
				(self.bottom+2*r>cy>self.top-2*r)):
				self.canvas.create_polygon(cx,          cy-r,
										   cx+adj60,    cy-adj30,
										   cx+adj60,    cy+adj30,
										   cx,          cy+r,
										   cx-adj60,    cy+adj30,
										   cx-adj60,    cy-adj30,
										   fill = color, outline = "black",
										   width = r/50)#line width heuristic
				#self.canvas.create_text(cx,cy,text=tile.terrain)
				if self.coords:self.canvas.create_text(cx,cy,text="%d,%d"%(
					tile.indexA,tile.indexB),font="Helvetica %d" % 
					(int(self.r/1.5))) #superimpose numbers
		#self.canvas.create_rectangle(self.left,self.top,self.right,self.bottom)
		#bounding rectangle to show what the board actually is

	def initBoard(self,cx=400,cy=250,width=700,height=400,r=22,random=True): #creates tiles
		cy = cy if cy != 250 else self.canvasHeight/2
		height = height if height != 400 else self.canvasHeight-(cx-width/2)*2
		left,right,top,bottom = cx-width/2,cx+width/2,cy-height/2,cy+height/2
		self.boardCX,self.boardCY = cx,cy
		self.left,self.top,self.right,self.bottom = left,top,right,bottom
		self.width,self.height = width,height #= abs(left-right),abs(top-bottom)
		if r < 0: r = min(width,height)/20 #radius heuristic
		adj60, adj30 = r*(3**.5)/2, r/2.0 #distances corresponding to the sides
			 #opposide the 30 and 60 degree angles of triangles in the hexagons
		self.adj60,self.adj30,self.top,self.left,self.r=adj60,adj30,top,left,r
		for colPos1 in xrange(0,self.cols,2):
			for rowPos1 in xrange(0,self.rows,2):
				Tile(colPos1,rowPos1,r,adj60,left,top,adj30)
		for colPos2 in xrange(1,self.cols,2): #easier to iterate every other row, separately
			for rowPos2 in xrange(1,self.rows,2):
				Tile(colPos2,rowPos2,r,adj60,left,top,adj30)
		if random:
			landSet = set()
			for tile in Tile.tileSet:
				if tile.terrain == "land":
					landSet.add(tile)
				#self.fillBoard(tile)
			#self.fillLand()
			self.growBoard(landSet)
			self.fillWater()
			#def growBoard(self,landSet): #weird broken code. rewrote it
			#	for landTile in landSet:
			#		indexA,indexB = landTile.indexA,landTile.indexB
			#		if (indexA,indexB) == (1,1):
			#			n = 5
			#			possibleLandDict = {}
			#			possibleLandSet = set()
			#			for n in xrange(n,0,-1):
			#				tempLandDict,tempLandSet = self.findPosLandNMovesAway(indexA,
			#					indexB,n)
			#				possibleLandSet = possibleLandSet.union(tempLandSet)
			#				for index in tempLandDict:
			#					possibleLandDict[index] = n
			#			for tileIndex in possibleLandSet:
			#				newTile = Tile.tileDict[tileIndex]
			#				weight = (1 - .25*(possibleLandDict[tileIndex]-1))
			#				probNo = random.uniform(0,1)
			#				if newTile.terrain == None:
			#					if probNo <= weight:
			#						newTile.terrain = "land"
			#						Tile.terrainDict[(indexA,indexB)] = newTile.terrain
			#						Tile.landDict[(indexA,indexB)] = newTile
			#					else:
			#						newTile.terrain = "water"
			#						Tile.terrainDict[(indexA,indexB)] = newTile.terrain
			#						Tile.waterDict[(indexA,indexB)] = newTile

	def growBoard(self,landSet):
		for landTile in landSet:
			indexA,indexB = landTile.indexA,landTile.indexB
			distanceAway = 2
			possibleTileSet = set()
			possibleTileDict = {}
			for n in xrange(distanceAway,0,-1):
				tempDict,tempSet = self.findPosLandNMovesAway(indexA,indexB,n)
				for key in tempDict:
					possibleTileDict[key] = tempDict[key]
				possibleTileSet = possibleTileSet.union(tempSet)
			for tileIndex in possibleTileSet:
				tile = Tile.tileDict[tileIndex]
				if tile.terrain == None:
					weight = (1 - .4*(possibleTileDict[tileIndex]-1))#Make the .4 (weight) closer to 1 for smaller land masses
					if random.uniform(0,1) <= weight:
						tile.terrain = "land"
						Tile.terrainDict[tileIndex] = "land"
						Tile.landDict[tileIndex] = tile

	def fillWater(self):
		for tile in Tile.tileSet:
			if tile.terrain == None:
				indexA,indexB = tile.indexA,tile.indexB
				tile.terrain = "water"
				Tile.terrainDict[(indexA,indexB)] = tile.terrain
				Tile.waterDict[(indexA,indexB)] = tile

	def findPosLandNMovesAway(self,indexA,indexB,n):
		boundingBoxTiles = self.findPossibleLandTilesBox(indexA,indexB,n)
		diamondTilesGivenSet = self.findDiamondMovesGivenSet(indexA,indexB,n,
			boundingBoxTiles)
		tilesNMovesAway = diamondTilesGivenSet
		landDict,landSet = {},set()
		for move in tilesNMovesAway:
			landDict[move] = n
			landSet.add(move)
		return landDict,landSet

	def findPossibleLandTilesBox(self,indexA,indexB,n):
		boundingBoxSet = set()
		for xPos in xrange(max(indexA-2*n,0),min(indexA+2*n,self.cols-1)+1):
			for yPos in xrange(max(indexB-n,0),min(indexB+n,self.rows-1)+1):
				if xPos%2 == yPos%2:
					boundingBoxSet.add((xPos,yPos))
		return boundingBoxSet

	def diamondPossibleLandTiles(self,indexA,indexB,n,boundingBoxSet):
		possibleLandSet = set()
		for indicie in boundingBoxSet:
			(moveX,moveY) = move
			deltaX = abs(moveX-indexA)
			deltaY = abs(moveY-indexB)
			deltaTotal = (deltaX+deltaY)/2
			deltaMax = n
			if deltaMax>=deltaTotal:
				possibleLandSet.add(move)
		return possibleLandSet
		#rectangle plus diamond makes hexagon

	def fillBoard(self,tile):
		indexA,indexB = tile.indexA,tile.indexB
		surroundingTiles = set([(indexA+2,indexB),(indexA-2,indexB),
		(indexA+1,indexB+1),(indexA-1,indexB-1),
		(indexA-1,indexB+1),(indexA+1,indexB-1)])
		surroundingArea = []
		for tileIndex in surroundingTiles:
			if tileIndex in Tile.terrainDict:
				surroundingArea.append(Tile.terrainDict[tileIndex])
		if surroundingArea.count(None) == 6:
			tile.terrain = "water"
			Tile.terrainDict[(indexA,indexB)] = tile.terrain
			Tile.waterDict[(indexA,indexB)] = tile
		elif surroundingArea.count("land") <= 1:
			probNo = random.uniform(0,1)
			if probNo >= 0.33:
				tile.terrain = "water"
				Tile.terrainDict[(indexA,indexB)] = tile.terrain
				Tile.waterDict[(indexA,indexB)] = tile
			else:
				tile.terrain = "land"
				Tile.terrainDict[(indexA,indexB)] = tile.terrain
				Tile.landDict[(indexA,indexB)] = tile

	def fillLand(self):
		for tile in Tile.tileSet:
			if tile.terrain == None:
				indexA,indexB = tile.indexA,tile.indexB
				tile.terrain = "land"
				Tile.terrainDict[(indexA,indexB)] = tile.terrain
				Tile.landDict[(indexA,indexB)] = tile
		#weight = (.5+(surroundingArea.count("land")-
		#	surroundingArea.count("water")/float(len(surroundingArea)))*.97*.5 
		#	if len(surroundingArea)>0 else .4)
		#tileDistrNo = random.triangular(0,1,weight)
		#if tileDistrNo<.5: return "water"
		#else: return "land"

	def drawPosition(self,indexA,indexB): #draws dot: hypothetical unit
		if (indexA%2 != indexB%2): indexA += 1 #NOT self.indexA
		adj60, adj30 = self.adj60, self.adj30
		left,top,r = self.left,self.top,self.r
		cx = left + adj60 + indexA*adj60
		cy = float(top + r) if indexB%2 == 0 else float(top+float(2*r+adj30))
		cy += indexB/2*float(2*(r+adj30))
		cx += self.adjX
		cy += self.adjY
		color = "black"
		if self.selected: color = "yellow"
		if (cx > self.right or cx < self.left or cy > self.bottom or 
			cy < self.top): return
		self.canvas.create_oval(cx-5,cy-5,cx+5,cy+5,fill = color)
		#the dot, which represents a unit, has an arbitrary radius of 5

	def initUnits(self): #arbitrary
		adj = 0 if self.cols%2 == 0 else 1
		self.rSetl = Settler("red",self.cols-2-adj,self.rows-2) #FIX, doesn't work for odd ones
		self.bSetl = Settler("blue",1,1) #HARDCODED
		self.rWar = Warrior("red",self.cols-3-adj,self.rows-3) #HARDCODED
		#Archer("red",self.cols-4,self.rows-4) #HARDCODED
		#Swordsman("blue",3,3)
		self.bWar = Warrior("blue",2,2) #HARDCODED
		#Ship("blue",1,7) #HARDCODED
		#Settler("red",3,1)

	def drawUnits(self):
		left,adj60,top,r,adj30=self.left,self.adj60,self.top,self.r,self.adj30
		self.indicateMovableTiles()
		for unit in Unit.unitSet:
			indexA,indexB = unit.xPos,unit.yPos
			cx = left + adj60 + indexA*adj60
			cy = float(top + r) if indexB%2 == 0 else float(top+float(2*r+adj30))
			cy += indexB/2*float(2*(r+adj30))
			cx += self.adjX
			cy += self.adjY
			typeStr = str(type(unit))
			if (cx > self.right or cx < self.left or cy > self.bottom or 
				cy < self.top): continue #don't draw if outside scope
			color = unit.team
			if unit.selected:
				color = "yellow"
				adj60,adj30,r = self.adj60,self.adj30,self.r
				self.canvas.create_polygon(cx,          cy-r,
										   cx+adj60,    cy-adj30,
										   cx+adj60,    cy+adj30,
										   cx,          cy+r,
										   cx-adj60,    cy+adj30,
										   cx-adj60,    cy-adj30,
										   fill = "", outline = "yellow",
										   width = r/50)
			if type(unit) == Warrior:
				if unit.team == "blue":
					self.canvas.create_image(cx,cy,image=self.bWarrior)
				else:
					self.canvas.create_image(cx,cy,image=self.rWarrior)
			elif type(unit) == Settler:
				if unit.team == "blue":
					self.canvas.create_image(cx,cy,image=self.bSettler)
				else:
					self.canvas.create_image(cx,cy,image=self.rSettler)
			elif type(unit) == Swordsman:
				if unit.team == "blue":
					self.canvas.create_image(cx,cy,image=self.bSwordsman)
				else:
					self.canvas.create_image(cx,cy,image=self.rSwordsman)
			elif type(unit) == Archer:
				if unit.team == "blue":
					self.canvas.create_image(cx,cy,image=self.bArcher)
				else:
					self.canvas.create_image(cx,cy,image=self.rArcher)
			elif type(unit) == Ship:
				if unit.team == "blue":
					self.canvas.create_image(cx,cy,image=self.bShip)
				else:
					self.canvas.create_image(cx,cy,image=self.rShip)
			else:
				self.canvas.create_text(cx,cy,text = typeStr[typeStr.find(".")+1:
					typeStr.find(".")+3],
					anchor = CENTER,fill = color) #teams are colors for now.
												  	#maybe have unit.color later

	def drawCities(self):
		left,adj60,top,r,adj30=self.left,self.adj60,self.top,self.r,self.adj30
		for city in City.citySet:
			indexA,indexB = city.xPos,city.yPos
			cx = left + adj60 + indexA*adj60
			cy = float(top + r) if indexB%2 == 0 else float(top+float(2*r+adj30))
			cy += indexB/2*float(2*(r+adj30))
			cx += self.adjX
			cy += self.adjY
			typeStr = str(type(city))
			if (cx > self.right or cx < self.left or cy > self.bottom or 
				cy < self.top): continue #don't draw if outside scope
			color = city.team
			if city.selected:
				color = "yellow"
				adj60,adj30,r = self.adj60,self.adj30,self.r
				self.canvas.create_polygon(cx,          cy-r,
										   cx+adj60,    cy-adj30,
										   cx+adj60,    cy+adj30,
										   cx,          cy+r,
										   cx-adj60,    cy+adj30,
										   cx-adj60,    cy-adj30,
										   fill = "", outline = "yellow",
										   width = r/50)
			self.canvas.create_image(cx+1,cy,image=self.city)
			#self.canvas.create_text(cx,cy,text = typeStr[typeStr.find(".")+1:
			#	typeStr.find(".")+3],
			#	anchor = CENTER,fill = color) #teams are colors for now.
											  	#maybe have unit.color later

	def indicateMovableTiles(self):
		if self.selectedUnit:
			self.findMovableTiles()
			for move in self.moveSet:
				adj60, adj30 = self.adj60, self.adj30
				left,top,r = self.left,self.top,self.r
				indexA,indexB = move
				cx = left + adj60 + indexA*adj60
				cy = (float(top + r) if indexB%2 == 0 else 
					float(top+float(2*r+adj30)))
				cy += indexB/2*float(2*(r+adj30))
				cx += self.adjX
				cy += self.adjY
				color = "pink"
				if (cx > self.right or cx < self.left or cy > self.bottom or 
					cy < self.top): continue
				r = self.r
				if Tile.terrainDict[(indexA,indexB)] == "water":
					color = "#9ab7d4"
				else:
					color = "#d1a28b"
				self.canvas.create_polygon(cx,          cy-r,
										   cx+adj60,    cy-adj30,
										   cx+adj60,    cy+adj30,
										   cx,          cy+r,
										   cx-adj60,    cy+adj30,
										   cx-adj60,    cy-adj30,
										   fill = color, outline = "black",
										   width = r/50)#line width heuristic
		else:
			self.moveSet = self.moveDict = None

	def findMovableTiles(self):
		indexA = self.selectedUnit.xPos
		indexB = self.selectedUnit.yPos
		moves = self.selectedUnit.moves
		self.moveDict = {}
		self.moveSet = set()
		for move in xrange(moves,0,-1):
			self.findNMovesAway(indexA,indexB,move)

	def findNMovesAway(self,indexA,indexB,n):
		boundingBoxMoves = self.findBoundingBoxMoves(indexA,indexB,n)
		diamondMovesGivenSet = self.findDiamondMovesGivenSet(indexA,indexB,n,
			boundingBoxMoves)
		legalMovesForN = diamondMovesGivenSet
		for move in legalMovesForN:
			if not isinstance(self.selectedUnit,Marine):
				if Tile.terrainDict[move] == "land":
					self.moveDict[move] = n
					self.moveSet.add(move)
			else:
				if Tile.terrainDict[move] == "water":
					self.moveDict[move] = n
					self.moveSet.add(move)

	def findBoundingBoxMoves(self,indexA,indexB,n):
		boundingBoxSet = set()
		for xPos in xrange(max(indexA-2*n,0),min(indexA+2*n,self.cols-1)+1):
			for yPos in xrange(max(indexB-n,0),min(indexB+n,self.rows-1)+1):
				if xPos%2 == yPos%2:
					boundingBoxSet.add((xPos,yPos))
		return boundingBoxSet

	def findDiamondMovesGivenSet(self,indexA,indexB,n,boundingBoxSet):
		legalMoveSet = set()
		for move in boundingBoxSet:
			(moveX,moveY) = move
			deltaX = abs(moveX-indexA)
			deltaY = abs(moveY-indexB)
			deltaTotal = (deltaX+deltaY)/2
			deltaMax = n
			if deltaMax>=deltaTotal:
				legalMoveSet.add(move)
		return legalMoveSet
		#rectangle plus diamond makes hexagon

	def turnIndicator(self): #colored rectangle
		self.canvas.create_rectangle(10,10,self.left-10,self.top-10,
			fill="%s" % self.player,width=2)

	def drawAroundBoard(self): #the beige around the board
		color="#fff7d2"
		outline = color
		width = 2
		self.canvas.create_rectangle(0,0,self.left,self.canvasHeight,
			fill=color,width=width,outline=outline)
		self.canvas.create_rectangle(self.left,0,self.right,self.top,
			fill=color,width=width,outline=outline)
		self.canvas.create_rectangle(self.left,self.bottom,self.right,
			self.canvasHeight,fill=color,width=width,outline=outline)
		self.canvas.create_rectangle(self.right,0,self.canvasWidth,
			self.canvasHeight,fill=color,width=width,outline=outline)
		left,top,right,bottom = self.left,self.top,self.right,self.bottom
		self.canvas.create_line(left,top,right,top,width=width)
		self.canvas.create_line(right,top,right,bottom,width=width)
		self.canvas.create_line(right,bottom,left,bottom,width=width)
		self.canvas.create_line(left,bottom,left,top,width=width)

	def parchmentBackground(self):
		#HARDCODED
		self.canvas.create_image(0,0,image = self.background,anchor = NW)

	def constructCityString(self,damage):
		selfColor = "Red" if self.selectedUnit.team == "red" else "Blue"
		otherColor = "Blue" if selfColor == "Red" else "Red"
		selfTypeStr = str(type(self.selectedUnit))
		selfUnitString = selfTypeStr[selfTypeStr.find(".")+1:-2]
		addend = "Your %s %s did %d damage to the %s City." % (selfColor,
			 selfUnitString,damage,otherColor)
		self.statusTextList.append(addend)

	def drawStatusBox(self):
		self.canvas.create_rectangle(self.right+50,self.canvasHeight/2,
			self.canvasWidth-50,self.canvasHeight-50,fill="#d6d1c4",
			outline = "#632017", width = 1)
		self.statusText = ""
		count = -1 + self.countAdj
		for event in reversed(self.statusTextList):
			count += 1
			if (self.canvasHeight-50>self.canvasHeight-70-count*35>
				(self.canvasHeight/2)+10):
				self.canvas.create_text(self.right+52,
					self.canvasHeight-80-count*35,
					text = event, anchor = W,
					font = "CenturyGothic 14",
					fill = "#632017",
					width=self.canvasWidth-50-self.right-50)

	def drawPromptBox(self):
		self.canvas.create_rectangle(self.right+50,self.canvasHeight/3+40,
			self.canvasWidth-50,self.canvasHeight/2-10,fill="#d6d1c4",
			outline = "#632017", width = 1)
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			(self.canvasHeight/2+self.canvasHeight/3)/2+15,
			text = "Status Box", fill = "#632017",font = "CenturyGothic 20")

	def drawInteractionBox(self):
		self.canvas.create_rectangle(self.right+50,self.top,
			self.canvasWidth-50,self.canvasHeight/3,fill="#d6d1c4",
			outline = "#632017", width = 1)
		if self.selectedUnit:
			unit = self.selectedUnit
			if isinstance(unit,Warrior):
				self.doWarriorInt()
			elif isinstance(unit,Swordsman):
				self.doSwordsManInt()
			elif isinstance(unit,Settler):
				self.doSettlerInt()
			elif isinstance(unit,Ship):
				self.doShipInt()
			elif isinstance(unit,Archer):
				self.doArcherInt()
		elif self.selectedCity:
			city = self.selectedCity
			self.doCityInt()
		else:
			self.noneSelected()

	def noneSelected(self):
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			self.top+(self.top+self.canvasHeight/3)/2/3,
			text = "Click on one of your units or cities to interact.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 15")
		#self.canvas.create_text((self.right+self.canvasWidth)/2,
		#	self.top+2*(self.top+self.canvasHeight/3)/2/3,
		#	text = "Press Enter/Return to have the computer play a move.",
		#	anchor = CENTER,
		#	fill ="#632017",
		#	font = "CenturyGothic 15")
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			self.top+3*(self.top+self.canvasHeight/3)/2/3,
			text = "Press Space to advance to the next turn.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 15")

	def doWarriorInt(self):
		#self.canvas.create_image(800,50,image = self.warriorInt,anchor = NE)
		selfColor = "Red" if self.selectedUnit.team == "red" else "Blue"
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.8,
			text = "%s Warrior" % selfColor,
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 17")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.5,
			text = "Health: %d\tMoves Remaining: %d" % (
				self.selectedUnit.health,self.selectedUnit.moves),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")	
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.3,
			text = "Attack: %d\t\tDefense: %d" % (self.selectedUnit.atk,
				self.selectedUnit.df),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		#self.canvas.create_text(self.right+55,
		#	(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
		#		)/2-self.top)*-.2,
		#	text = "Defense: %d" % self.selectedUnit.df,
		#	anchor = W,
		#	fill ="#632017",
		#	font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.3,
			text = "Click a highlighted tile to move there.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.5,
			text = "If you are next to an enemy, click on it to attack.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.7,
			text = "If you are next to friendly ship, click on it to board.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")

	def doSwordsManInt(self):
		#self.canvas.create_image(800,50,image = self.warriorInt,anchor = NE)
		selfColor = "Red" if self.selectedUnit.team == "red" else "Blue"
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.8,
			text = "%s Swordsman" % selfColor,
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 17")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.5,
			text = "Health: %d\tMoves Remaining: %d" % (
				self.selectedUnit.health,self.selectedUnit.moves),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")	
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.3,
			text = "Attack: %d\t\tDefense: %d" % (self.selectedUnit.atk,
				self.selectedUnit.df),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		#self.canvas.create_text(self.right+55,
		#	(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
		#		)/2-self.top)*-.2,
		#	text = "Defense: %d" % self.selectedUnit.df,
		#	anchor = W,
		#	fill ="#632017",
		#	font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.3,
			text = "Click a highlighted tile to move there.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.5,
			text = "If you are next to an enemy, click on it to attack.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.7,
			text = "If you are next to friendly ship, click on it to board.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")

	def doSettlerInt(self):
		#self.canvas.create_image(800,50,image = self.warriorInt,anchor = NE)
		selfColor = "Red" if self.selectedUnit.team == "red" else "Blue"
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.8,
			text = "%s Settler" % selfColor,
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 17")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.5,
			text = "Moves Remaining: %d" % (self.selectedUnit.moves),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.4,
			text = "Click a highlighted tile to move there.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.6,
			text = "If you are next to friendly ship, click on it to board.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")

	def doShipInt(self):
		#self.canvas.create_image(800,50,image = self.warriorInt,anchor = NE)
		selfColor = "Red" if self.selectedUnit.team == "red" else "Blue"
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.8,
			text = "%s Ship" % selfColor,
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 17")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.3,
			text = "On Board: %d\tMax Capacity: %d" % (
				self.selectedUnit.currentCapacity,self.selectedUnit.capacity),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")	
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.5,
			text = "Moves: %d" % (self.selectedUnit.moves),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.3,
			text = "Click a highlighted tile to move there.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.5,
			text = "If next to land, press 'l' to unload all boarded units.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.7,
			text = "To board units: select the unit then click the ship when close.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")

	def doArcherInt(self):
		#self.canvas.create_image(800,50,image = self.warriorInt,anchor = NE)
		selfColor = "Red" if self.selectedUnit.team == "red" else "Blue"
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.8,
			text = "%s Archer" % selfColor,
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 17")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.5,
			text = "Health: %d\tMoves Remaining: %d" % (
				self.selectedUnit.health,self.selectedUnit.moves),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")	
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.3,
			text = "Attack: %d\t\tDefense: %d\tRange: %d" % (
				self.selectedUnit.atk,self.selectedUnit.df,
				self.selectedUnit.range),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		#self.canvas.create_text(self.right+55,
		#	(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
		#		)/2-self.top)*-.2,
		#	text = "Defense: %d" % self.selectedUnit.df,
		#	anchor = W,
		#	fill ="#632017",
		#	font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.3,
			text = "Click a highlighted tile to move there.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.5,
			text = "If you are in range of an enemy, click on it to attack.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.7,
			text = "If you are next to friendly ship, click on it to board.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")

	def doCityInt(self):
		#self.canvas.create_image(800,50,image = self.warriorInt,anchor = NE)
		selfColor = "Red" if self.selectedCity.team == "red" else "Blue"
		self.canvas.create_text((self.right+self.canvasWidth)/2,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.8,
			text = "%s City" % selfColor,
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 17")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.5,
			text = "Health: %d" % (self.selectedCity.health),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")	
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*-.3,
			text = "Production Shields: %d\tProduction Per Turn: %.1f" % (
				self.selectedCity.currentProduction,
				self.selectedCity.determineProductionLevel()),
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")
		self.canvas.create_text(self.right+55,
			(self.top+self.canvasHeight/3)/2+((self.top+self.canvasHeight/3
				)/2-self.top)*.5,
			text = "To create units, press the corresponding key, with this city\nselected. For reference, see the help screen.",
			anchor = W,
			fill ="#632017",
			font = "CenturyGothic 14")

	def updateStatusListFromBattle(self,damageDealt,damageRetaliated,
		selfHealth,otherHealth,unpackedTile):
		supportActions = ["besiged","attacked","came across",
		"made convincing arguments to","dispensed wisdom upon"]
		supportTransitions = ["In the search for a more timely demise,",
		"To avoid a rather nasty confrontation,",
		"Due to a spontaneous change of heart,","Responding to reason,",
		"Being enlightened,"]
		supportReactions = ["hastily became a","made the transition to",
		"switched colors to become a",
		"realized they would look better in a different color:",
		"made a superior decision, becoming a"]
		selfColor = "Red" if self.selectedUnit.team == "red" else "Blue"
		otherColor = "Blue" if selfColor == "Red" else "Red"
		selfTypeStr = str(type(self.selectedUnit))
		selfUnitString = selfTypeStr[selfTypeStr.find(".")+1:-2]
		otherTypeStr = str(type(unpackedTile))
		otherUnitString = otherTypeStr[otherTypeStr.find(".")+1:-2]
		if isinstance(unpackedTile,Support):
			actionNo = random.randint(0,4)
			actionString = supportActions[actionNo]
			transisionString = supportTransitions[actionNo]
			reactionString = supportReactions[actionNo]
			actionAddend = "Your %s %s %s a %s %s." % (selfColor,selfUnitString,
				actionString,otherColor,otherUnitString)
			self.statusTextList.append(actionAddend)
			reactionAddend = "%s the %s %s %s %s %s." % (transisionString,
				otherColor,otherUnitString,reactionString,selfColor,
				otherUnitString)
			self.statusTextList.append(reactionAddend)
		elif isinstance(unpackedTile,Military):
			actionString = "Your %s %s dealt %d damage to the %s %s." % (
				selfColor,selfUnitString,damageDealt,otherColor,
				otherUnitString)
			self.statusTextList.append(actionString)
			reactionString = "In retaliation, the %s %s dealt %d" % (
				otherColor,otherUnitString,damageRetaliated)
			reactionString += " damage to your %s %s." % (selfColor,
				selfUnitString)
			self.statusTextList.append(reactionString)
			#if isinstance(self.selectedUnit,Range):
			#	if isinstance(unpackedTile,Range):
			#		actionString = "Your %s %s %s the opposing %s %s." % (
			#			selfColor,selfUnitString,"rained arrows upon", #temp
			#			otherColor,otherUnitString)
			#		self.statusTextList.append(actionString)
			#		reactionString = "Defending itself, the %s %s %s on your"
			#	elif isinstance(unpackedTile,Military):
			#		pass
			#elif isinstance(self.selectedUnit,Land):
			#	if isinstance(unpackedTile,Range):
			#		pass
			#	elif isinstance(unpackedTile,Military):
			#		pass

	def drawHoverMenus(self):
		indexA,indexB = self.motionIndexA,self.motionIndexB
		if (time.time()-.75>self.baseTime):
			if ((indexA,indexB) in Unit.unitDict or
				(indexA,indexB) in City.cityDict):
				if Unit.unitDict[(indexA,indexB)]:
					unit = list(Unit.unitDict[(indexA,indexB)])[0]
					self.canvas.create_rectangle(self.mseX,self.mseY,
						self.mseX+100,self.mseY-67,
						fill="white",outline="black",width=2)
					typeStr = str(type(unit))
					color = "Red" if unit.team == "red" else "Blue"
					unitString = (color + " " + typeStr[typeStr.find(".")+1:
						-2])
					if isinstance(unit,Land):
						rank = chr(ord(str(unit.rank)[0])-32)+str(unit.rank)[1:]
						unitString += ("\nHealth: " + str(unit.health) +"\nAttack: "
							+ str(unit.atk) + "\nDefense: " + str(unit.df) + "\n" +
							"Moves Left: " + str(unit.moves))
						self.canvas.create_text(self.mseX+1,self.mseY-66,
							text = unitString, fill = "black", anchor = NW,
							font = "CenturyGothic 10")
					elif isinstance(unit,Range):
						unitString += ("\nHealth: " + str(unit.health) +"\nAttack: "
							+ str(unit.atk) + "\nDefense: " + str(unit.df) + "\n" +
							"Moves Left: " + str(unit.moves) + "\nRange: " + 
							str(unit.range))
						self.canvas.create_text(self.mseX+1,self.mseY-66,
							text = unitString, fill = "black", anchor = NW,
							font = "CenturyGothic 9")
					elif isinstance(unit,Marine):
						unitString += ("\nOn Board: " + 
							str(unit.currentCapacity) +"\nMax Capacity: "
							+ str(unit.capacity) + "\nMoves Left: " + 
							str(unit.moves))
						self.canvas.create_text(self.mseX+1,self.mseY-66,
							text = unitString, fill = "black", anchor = NW,
							font = "CenturyGothic 10")
					elif isinstance(unit,Settler):
						unitString += ("\nMoves Left: " + str(unit.moves))
						self.canvas.create_text(self.mseX+1,self.mseY-66,
							text = unitString, fill = "black", anchor = NW,
							font = "CenturyGothic 10")
				elif ((indexA,indexB) in City.cityDict and
					City.cityDict[(indexA,indexB)]):
					city = list(City.cityDict[(indexA,indexB)])[0]
					self.canvas.create_rectangle(self.mseX,self.mseY,
						self.mseX+100,self.mseY-67,
						fill="white",outline="black",width=2)
					color = "Red" if city.team == "red" else "Blue"
					cityString = (color + " City" + "\nCurrent Production\n" + 
						"   Shields: " + str(city.currentProduction) + 
						"\nHealth: " + str(city.health))
					self.canvas.create_text(self.mseX+1,self.mseY-66,
						text = cityString, fill = "black", anchor = NW,
						font = "CenturyGothic 10")

	def scrollBoard(self):
		xRan = self.width/5
		yRan = self.height/5
		xAdj = xRan/20
		yAdj = yRan/20
		if self.left<self.mseX<self.left+xRan: #LEFT
			if (not(self.leftEdge+(self.left+xRan-self.mseX)/xAdj/2>self.left)
				and self.top<=self.mseY<=self.bottom):
				self.adjX += int((self.left+xRan-self.mseX)/xAdj/1.5)
			elif self.top<=self.mseY<=self.bottom:
				#self.adjX += self.right-self.rightEdge #wrap-around
				self.adjX = 0 #stop
		elif self.right>self.mseX>self.right-xRan: #RIGHT
			if (not(self.rightEdge-(self.mseX-self.right+xRan)
				/xAdj/2<=self.right) and self.top<=self.mseY<=self.bottom):
				self.adjX -= int((self.mseX-self.right+xRan)/xAdj/1.5)
			elif self.top<=self.mseY<=self.bottom:
			#	self.adjX = 0 #wrap-around
				self.adjX += self.right-self.rightEdge #stop
		if self.top<self.mseY<self.top+yRan: #UP
			if (not(self.topEdge+(self.top+yRan-self.mseY)/yAdj/2>self.top)
				and self.left<=self.mseX<=self.right):
				self.adjY += int((self.top+yRan-self.mseY)/yAdj/1.5)
			elif self.left<=self.mseX<=self.right:
			#	self.adjY += self.bottom-self.bottomEdge #wrap-around
				self.adjY = 0 #stop
		elif self.bottom>self.mseY>self.bottom-yRan: #DOWN
			if (not(self.bottomEdge-(self.mseY-self.bottom+yRan)
				/yAdj/2<self.bottom) and self.left<=self.mseX<=self.right):
				self.adjY -= int((self.mseY-self.bottom+yRan)/yAdj/1.5)
			elif self.left<=self.mseX<=self.right:
			#	self.adjY = 0 #wrap-around
				self.adjY += self.bottom-self.bottomEdge #stop

	def drawSplashScreen(self): #starting screen
		image = self.image
		self.canvas.create_image(0,0,image=image,anchor=NW)

	def drawHelp(self): #help screen
		self.canvas.create_image(0,0,image=self.fullBackground,anchor=NW)
		createStr = "self.drawHelpPg%d()" % self.helpPage
		eval(createStr)

	def drawHelpPg0(self):
		xPos = self.canvasWidth/2
		self.canvas.create_text(xPos,35,
			text = "Help",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 48")
		self.canvas.create_text(xPos,self.canvasHeight-35,
			text = "Use the left/right arrow keys to scroll through the help section.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 28")
		self.canvas.create_text(self.canvasWidth-5,self.canvasHeight-5,
			text = "Page 0",
			anchor = SE,
			fill ="#632017",
			font = "CenturyGothic 16")
		self.canvas.create_text(xPos,135,
			text = "Table of Contents:",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 26")
		self.canvas.create_text(xPos,205,
			text = "Table of Contents : Page 0",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,240,
			text = "General Gameplay : Page 1",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,275,
			text = "Units : Page 2",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,310,
			text = "Cities : Page 3",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,345,
			text = "Objective : Page 4",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")

	def drawHelpPg1(self):
		xPos = self.canvasWidth/2
		self.canvas.create_text(xPos,35,
			text = "Help",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 48")
		self.canvas.create_text(xPos,self.canvasHeight-35,
			text = "Use the left/right arrow keys to scroll through the help section.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 28")
		self.canvas.create_text(self.canvasWidth-5,self.canvasHeight-5,
			text = "Page 1",
			anchor = SE,
			fill ="#632017",
			font = "CenturyGothic 16")
		self.canvas.create_text(xPos,135,
			text = "General Gameplay:",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 26")
		self.canvas.create_text(xPos,205,
			text = "Click on a unit/city to select it.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,240,
			text = "Then, click on a highlighted tile to interact with it.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,275,
			text = "You can move to land tiles, battle enemy military units, and load onto friendly marine units.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,310,
			text = "You may not move onto a city or stack units (have more than one unit per tile).",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,345,
			text = "The square in the upper left corner indicates whose turn it is.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,380,
			text = "Press space to advance to the next player's turn.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,415,
			text = "Press 'h' to toggle help.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,450,
			text = "Press 'r' to reset the game.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,485,
			text = "Hover over a unit to see quick information. Click it to get more detailed infromation.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,510,
			text = "Scroll over by moveing your mouse to a corner of the board.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")

	def drawHelpPg2(self):
		xPos = self.canvasWidth/2
		self.canvas.create_text(xPos,35,
			text = "Help",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 48")
		self.canvas.create_text(xPos,self.canvasHeight-35,
			text = "Use the left/right arrow keys to scroll through the help section.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 28")
		self.canvas.create_text(self.canvasWidth-5,self.canvasHeight-5,
			text = "Page 2",
			anchor = SE,
			fill ="#632017",
			font = "CenturyGothic 16")
		self.canvas.create_text(xPos,135,
			text = "Units:",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 26")
		self.canvas.create_text(xPos,240,
			text = "Click on a unit to select it.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,205,
			text = "Unit Types: Warrior, Archer, Swordsman, Settler, and Ship.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,275,
			text = "If a marine unit is next to land, press 'l' to unload any loaded land units.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,310,
			text = "You may not move onto a city or stack units (have more than one unit per tile).",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,345,
			text = "After selecting a unit, click a highlighted tile (or marine unit) to interact.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,380,
			text = "If you have a Settler selected, press 'c' to found a city at that location.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,415,
			text = "Land units may only attack units next to them. Range units may attack anyone in their range.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,450,
			text = "Land units may only stand on land, but may traverse water. The opposite is true for marine units",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")

	def drawHelpPg3(self):
		xPos = self.canvasWidth/2
		self.canvas.create_text(xPos,35,
			text = "Help",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 48")
		self.canvas.create_text(xPos,self.canvasHeight-35,
			text = "Use the left/right arrow keys to scroll through the help section.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 28")
		self.canvas.create_text(self.canvasWidth-5,self.canvasHeight-5,
			text = "Page 3",
			anchor = SE,
			fill ="#632017",
			font = "CenturyGothic 16")
		self.canvas.create_text(xPos,135,
			text = "Cities:",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 26")
		self.canvas.create_text(xPos,205,
			text = "Cities have production shields, which you use to make units. Hover or click to view how many you have.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,240,
			text = "Cities have health that can be reduced by enemy units. Don't let it get to 0!",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,310,
			text = "Create units by selecting a city and pressing the corresping production macro (key).",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,345,
			text = "Unit Type : Production Shield Cost : Production Macro",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,380,
			text = "Warrior : 7 Shields : 'w'",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,275,
			text = "Cities gain variable amounts (from 1.5 to 3) of Production Shields, per turn.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,415,
			text = "Archer : 8 Shields : 'a'",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,450,
			text = "Ship : 9 Shields : 'p'",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,485,
			text = "Settler : 10 Shields : 's'",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,520,
			text = "Swordsman : 12 Shields : 'm'",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,555,
			text = "Cities produce units on a tile next to them. If all such tiles are filled, cities cannot prouce until otherwise.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")

	def drawHelpPg4(self):
		xPos = self.canvasWidth/2
		self.canvas.create_text(xPos,35,
			text = "Help",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 48")
		self.canvas.create_text(xPos,self.canvasHeight-35,
			text = "Use the left/right arrow keys to scroll through the help section.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 28")
		self.canvas.create_text(self.canvasWidth-5,self.canvasHeight-5,
			text = "Page 4",
			anchor = SE,
			fill ="#632017",
			font = "CenturyGothic 16")
		self.canvas.create_text(xPos,135,
			text = "Objective:",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 26")
		self.canvas.create_text(xPos,205,
			text = "Eliminate all enemy Military Units, Settlers, and Cities to win.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,240,
			text = "Note: Ships are not military units, so you needn't eliminate them.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,275,
			text = "Note: Any units loaded onto ships do not exist in regard to the win condition.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,310,
			text = "Note: Once unloaded, however, units that were once on a ship count towards the win condition.",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,345,
			text = "",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,410,
			text = "",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,415,
			text = "",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,450,
			text = "",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,485,
			text = "",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,520,
			text = "",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")
		self.canvas.create_text(xPos,555,
			text = "",
			anchor = CENTER,
			fill ="#632017",
			font = "CenturyGothic 24")

	def calcUnitList(self):
		self.blueUnits = []
		self.redUnits = []
		for city in City.citySet:
			if city.team == "blue":
				self.blueUnits.append(city)
			elif city.team == "red":
				self.redUnits.append(city)
		for unit in Unit.unitSet:
			if not isinstance(unit,Marine):
				if unit.team == "blue":
					self.blueUnits.append(unit)
				elif unit.team == "red":
					self.redUnits.append(unit)

	def detectOutcome(self):
		if len(self.blueUnits) <= 0:
			self.victoriousTeam = ("red","Red")
			self.outcome = True
		elif len(self.redUnits) <= 0:
			self.victoriousTeam = ("blue","Blue")
			self.outcome = True

	def secureWin(self):
		unitsToRemove = []
		for unit in Unit.unitSet:
			if unit.team != self.victoriousTeam[0]:
				unitsToRemove.append(unit)
		for unit in unitsToRemove:
			Unit.unitSet.remove(unit)
			Unit.unitDict[(unit.xPos,unit.yPos)].remove(unit)

	def displayOutcome(self):
		self.canvas.create_oval(self.canvasWidth/4,self.canvasHeight/4,
			3*self.canvasWidth/4,3*self.canvasHeight/4,fill="#d6d1c4",
			outline = "#632017", width = 1)
		self.canvas.create_text(self.canvasWidth/2,
			self.canvasHeight/2-self.canvasHeight/8,
			fill="#632017",
			text = "The %s Team Won!" % self.victoriousTeam[1],
			font = "CenturyGothic 24")
		self.canvas.create_text(self.canvasWidth/2,
			self.canvasHeight/2,
			fill="#632017",
			text = "Press Space to continue building your empire.",
			font = "CenturyGothic 16")
		self.canvas.create_text(self.canvasWidth/2,
			self.canvasHeight/2+self.canvasHeight/16,
			fill="#632017",
			text = "Press 'r' to restart the game.",
			font = "CenturyGothic 16")

	def init(self): #initializes the animation
		Tile.tileSet = set()
		Unit.unitDict = {}
		Unit.unitSet = set()
		Tile.tileSet = set()
		Tile.tileDict = {}
		Tile.landDict = {}
		Tile.waterDict = {}
		Tile.terrainDict = {}
		City.cityDict = {}
		City.citySet = set()
		#add inital production options in init
		#add consequent production options in science engine
		self.initBoard()
		self.initUnits()
		#"in-shifted" by 25 to show that program works even if the boundaries
		#are not the edges
		self.motionIndexA = 0
		self.motionIndexB = 0
		#self.selected = False
		self.coords = False
		self.adjX = 0
		self.adjY = 0
		self.showUnits = True
		self.selectedUnit = None
		self.player = "blue"
		self.splashScreen = True
		self.help = False
		self.selectedCity = None
		#self.initAroundBoard
		self.mseX = 0
		self.mseY = 0
		self.motionIndexA = -1
		self.motionIndexB = -1
		self.baseTime = time.time()**2
		self.lastA = 0
		self.lastB = 0
		#self.statusText = ""
		self.statusTextList = []
		self.countAdj = 0
		self.start = PhotoImage(file="start.gif")
		self.helpHover = PhotoImage(file="help-hover.gif")
		self.playHover = PhotoImage(file="play-hover.gif")
		self.helpClick = PhotoImage(file="help-click.gif")
		self.playClick = PhotoImage(file="play-click.gif")
		self.image = self.start
		self.mousePress = False
		self.mouseRelease = True
		self.background = PhotoImage(file="background.gif")
		#self.warriorInt = PhotoImage(file="warrior-int.gif")
		self.bWarrior = PhotoImage(file="blue-warrior.gif")
		self.rWarrior = PhotoImage(file="red-warrior.gif")
		self.rSettler = PhotoImage(file="red-settler.gif")
		self.bSettler = PhotoImage(file="blue-settler.gif")
		self.bSwordsman = PhotoImage(file="blue-swordsman.gif")
		self.rSwordsman = PhotoImage(file="red-swordsman.gif")
		self.rArcher = PhotoImage(file="red-archer.gif")
		self.bArcher = PhotoImage(file="blue-archer.gif")
		self.bShip = PhotoImage(file="blue-ship.gif")
		self.rShip = PhotoImage(file="red-ship.gif")
		self.city = PhotoImage(file="city.gif")
		self.outcome = False
		self.showDisplayOutcome = True
		self.helpPage = 0
		self.fullBackground = PhotoImage(file="full-background.gif")

	def redrawAll(self): #redraws all
		if not self.outcome:
			self.calcUnitList()
			self.detectOutcome()
		elif self.outcome:
			self.displayOutcome()
		if self.splashScreen:
			if self.help: self.drawHelp()
			else: self.drawSplashScreen()
		else: 
			if self.help: self.drawHelp()
			else:
				self.drawBoard()
				if self.showUnits:
					self.drawUnits()
					self.drawCities()
				self.drawAroundBoard()
				self.parchmentBackground()
				if self.showUnits:
					self.drawHoverMenus()
				self.turnIndicator()
				self.scrollBoard()
				self.drawStatusBox()
				self.drawPromptBox()
				self.drawInteractionBox()
		if not self.outcome:
			self.calcUnitList()
			self.detectOutcome()
		elif self.outcome:
			self.secureWin()
			if self.showDisplayOutcome:
				self.displayOutcome()
		#self.drawPosition(self.indexA,self.indexB)

Civilization().run(30,60)

def testAll():
	pass