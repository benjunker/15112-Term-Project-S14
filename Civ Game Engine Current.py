#more effective search function --> use mouse position as location heruistic
#"dot" "shifts" to the right for larger numbers --> (floating point errors?)
#determine indecies in initBoard! Do not wait to extrapolate in __init__ --> Done!
#Do gross math for efficient mouse click search.... --> Yay!

from Tkinter import *
import random
import math
from fractions import Fraction

class Animation(object): #From Kosbie email;expanded sligtly from stock code
	def mousePressed(self, event): pass
	def keyPressed(self, event): pass
	def timerFired(self): pass
	def init(self): pass
	def redrawAll(self): pass
	def mouseReleased(self,event): pass #added mouseReleased
	#removed many of the comments
	def run(self,rows=10,cols=20,width=500,height=500):#new args
		root = Tk()
		self.width,self.height = width,height
		self.rows,self.cols = rows,cols
		self.canvas = Canvas(root, width=width, height=height)
		self.canvas.configure(bd = 0, highlightthickness = 0) #added
		self.canvas.pack()
		def redrawAllWrapper():
			self.canvas.delete(ALL)
			self.redrawAll()
		def mousePressedWrapper(event):
			self.mousePressed(event)
			redrawAllWrapper()
		def mouseReleasedWrapper(event):
			self.mouseReleased(event)
			redrawAllWrapper()
		def keyPressedWrapper(event):
			self.keyPressed(event)
			redrawAllWrapper()
		root.bind("<Button-1>", mousePressedWrapper)
		root.bind("<Key>", keyPressedWrapper)
		root.bind("<B1-ButtonRelease>",mouseReleasedWrapper)
		self.timerFiredDelay = 200 # milliseconds
		def timerFiredWrapper():
			self.timerFired()
			redrawAllWrapper()
			self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
		self.init()
		timerFiredWrapper()
		root.mainloop()

class Unit(object): #generic unit class
	unitDict = {}

	unitSet = set()

	effectiveDict = {"very ineffective" : 1,
					 "ineffective"      : 2,
					 "neutral"          : 3,
					 "effective"        : 4,
					 "very effective"   : 5}
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
				#dictionary

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

	def move(self,indexA,indexB):
		deltaX = abs(self.xPos-indexA)
		deltaY = abs(self.yPos-indexB)
		deltaTotal = (deltaX+deltaY)/2
		print self.moves
		if self.moves>=deltaTotal:
			Unit.unitDict[(self.xPos,self.yPos)].remove(self)
			self.moves-=deltaTotal
			self.xPos,self.yPos = indexA,indexB
			try: Unit.unitDict[(self.xPos,self.yPos)].add(self)
			except: Unit.unitDict[(self.xPos,self.yPos)] = set([self])
		print self.moves

	def reset(self):
		#to reset moves each turn
		self.moves = self.defaultMoves

	def battleSuccess(self): pass
	def battle(self): pass
	def attack(self): pass
	def retaliate(self): pass

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

	def battle(self,other): #battle enginge, for military units
		if isinstance(other,Military):		
			selfSuccess = self.battleSuccess()
			otherSuccess = other.battleSuccess()
			self.attack(other,selfSuccess,otherSuccess)
			other.retaliate(self,selfSuccess,otherSuccess)
		elif isinstance(other,Support):
			other.lose(self)

	def attack(self,other,selfSuccess,otherSuccess): #dealing damage
		otherBefore = other.health
		damage = 3*selfSuccess*self.atk-otherSuccess*other.df
		other.health = other.health - damage if damage>0 else other.health
		otherAfter = other.health

	def retaliate(self,other,selfSuccess,otherSuccess): #retaliating after atk
		otherBefore = other.health
		damage = (3*selfSuccess*self.atk-otherSuccess*other.df)/2
		other.health = other.health - damage if damage>0 else other.health
		otherAfter = other.health

class Land(Military):
	def battle(self,other):
		if not (isinstance(other,Land) or isinstance(other,Support)):
			assert (False)
		super(Land,self).battle(other)

	def retaliate(self,other,selfSuccess,otherSuccess):
		if isinstance(other,Land):
			super(Land,self).retaliate(other,selfSuccess,otherSuccess)

class Warrior(Land):
	atk = df = moves = sight = 2 #arbitrary

	def __init__(self,team=None,xPos=None,yPos=None,health=100):
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

class Support(Unit):
	def lose(self,other):
		assert isinstance(other,Military)
		if self.state == "neutral":
			self.team = other.team

class Settler(Support):
	moves = sight = 2

	def  __init__(self,team=None,xPos=None,yPos=None):
		moves,sight = Settler.moves,Settler.sight
		super(Settler,self).__init__(team,moves,xPos,yPos,sight)

	def settle(self):
		Unit.unitDict[(self.xPos,self.yPos)].remove(self)

class Tile(object): #tiles that make up the board
	tileSet = set() #list of all tiles to iterate through
	def __init__(self,colPos,rowPos,r,adj60,left,top,adj30): #initializes each tile
		cx = left + adj60 + colPos * adj60
		cy = top + r if rowPos%2 == 0 else top+2*r+adj30
		cy += rowPos/2*2*(r+adj30)
		self.cx,self.cy,self.r = cx,cy,r
		self.indexA,self.indexB = colPos,rowPos
		Tile.tileSet.add(self)

class PartialGame(Animation): #basis of the "board" and how things will move

	def mousePressed(self,event):
		adj60,adj30,r = self.adj60,self.adj30,self.r
		mBlue = ((1.0*r-adj30)/adj60) #slope for blue lines
		mRed = ((1.0*adj30-r)/adj60) #slope for red lines
		#see concept "Board With Lines.png" if unclear
		mseX,mseY = event.x,event.y
		if (mseX > self.right or mseX < self.left or mseY > self.bottom or 
			mseY < self.top): return
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
		self.unitAction(indexA,indexB)
		#if not self.selected:
		#	if (self.indexA == indexA) and (self.indexB == indexB):
		#		self.selected = True
		#else:
		#	self.indexA = indexA
		#	self.indexB = indexB
		#	self.selected = False

	def unitAction(self,indexA,indexB):
		if self.selectedUnit == None:
			try:
				unit = self.unpackTile(indexA,indexB)
				if unit.team == self.player:
					self.selectUnit(unit)
				print "not selected: try"
			except:
				print "not selected: except"
				return
		else:
			try:
				unit = self.unpackTile(indexA,indexB)
				if unit.team == self.selectedUnit.team == self.player:
					self.selectUnit(unit)
				print "selected: try"
			except:
				self.selectedUnit.move(indexA,indexB)
				self.deselectCurrentlySelectedUnit()
				print "selected: except"

	def unpackTile(self,indexA,indexB):
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
		self.selectedUnit = unit

	def deselectCurrentlySelectedUnit(self):
		if self.selectedUnit:
			self.selectedUnit.selected = False
			self.selectedUnit = None

	def deselectAllUnits(self): #possibly never used
		for everyUnit in Unit.unitSet:
			everyUnit.selected = False
		self.selectedUnit = None

	def keyPressed(self,event): #mainly for testing; as moving uses the mouse in game
		keyAdj = 20
		#if event.keysym == "z": self.indexA -= 2 #move the "dot" #left
		#elif event.keysym == "s": self.indexB -= 1 #up
		#elif event.keysym == "x": self.indexB += 1 #down
		#elif event.keysym == "c": self.indexA += 2 #right
		if event.keysym == "d": self.coords = not(self.coords) #superimpose
														   #numbers over tiles
		elif event.keysym == "Up":
			if not self.bottomEdge-keyAdj<=self.bottom:
				self.adjY -= keyAdj
			else:
				self.adjY += self.bottom-self.bottomEdge #stop
				#self.ajdY = 0 #wrap around
		elif event.keysym == "Down":
			if not self.topEdge+keyAdj>=self.top:
				self.adjY += keyAdj
			else:
				self.adjY = 0 #stop
				#self.adjY += self.bottom-self.bottomEdge #wrap-around
		elif event.keysym == "Right":
			if not self.leftEdge+keyAdj>=self.left:
				self.adjX += keyAdj
			else:
				self.adjX = 0 #stop
				#self.adjX += self.right-self.rightEdge #wrap-around
		elif event.keysym == "Left":
			if not self.rightEdge-keyAdj<=self.right:
				self.adjX -= keyAdj
			else:
				self.adjX += self.right-self.rightEdge #stop
				#self.adjX = 0 #wrap around
		elif event.keysym == "u": self.showUnits = not(self.showUnits)
		elif event.keysym == "space":
			self.switchPlayer()
			self.deselectCurrentlySelectedUnit()
			self.resetUnits() #happens at the beginning of the turn
			print self.player
		#print self.indexA,self.indexB

	def switchPlayer(self):
		if self.player == "blue": self.player = "red"
		else: self.player = "blue"

	def resetUnits(self):
		for unit in Unit.unitSet:
			if unit.team == self.player:
				unit.reset()

	def drawBoard(self): #for each tile object, draws a hexagon
		adj60,adj30,left,top,r = self.adj60,self.adj30,self.left,self.top,self.r
		rows,cols = self.rows-1,self.cols-1
		self.leftEdge = left+self.adjX
		self.rightEdge = left+2*adj60+self.adjX+(self.cols-1)*adj60
		self.topEdge = top+self.adjY
		self.bottomEdge = top + r if rows%2 == 0 else top+2*r+adj30+self.adjY
		self.bottomEdge += rows/2*2*(r+adj30) + r
		for tile in Tile.tileSet:
			cx,cy,r = tile.cx,tile.cy,tile.r
			cx += self.adjX
			cy += self.adjY
			if ((self.right+2*self.adj60>cx>self.left-2*adj60) and
				(self.bottom+2*r>cy>self.top-2*r)):
				self.canvas.create_polygon(cx,          cy-r,
										   cx+adj60,    cy-adj30,
										   cx+adj60,    cy+adj30,
										   cx,          cy+r,
										   cx-adj60,    cy+adj30,
										   cx-adj60,    cy-adj30,
										   fill = "white", outline = "black",
										   width = r/50)#line width heuristic
				if self.coords:self.canvas.create_text(cx,cy,text="%d,%d"%(
					tile.indexA,tile.indexB),font="Helvetica %d" % 
					(int(self.r/1.5))) #superimpose numbers
		self.canvas.create_rectangle(self.left,self.top,self.right,self.bottom)
		#bounding rectangle to show what the board actually is

	def initBoard(self,left,top,right,bottom,r=-1): #creates tiles for board
		self.left,self.top,self.right,self.bottom = left,top,right,bottom
		self.width,self.height = width,height = abs(left-right),abs(top-bottom)
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

	def initUnits(self):
		Settler("red",0,0)
		Settler("blue",6,6)
		Warrior("red",1,1)
		Warrior("blue",5,5)

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
			self.canvas.create_text(cx,cy,text = typeStr[typeStr.find(".")+1:
				typeStr.find(".")+3],
				anchor = CENTER,fill = color) #teams are colors for now.
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
				self.canvas.create_oval(cx-5,cy-5,cx+5,cy+5,fill = color)
		else: pass

	def findMovableTiles(self):
		indexA = self.selectedUnit.xPos
		indexB = self.selectedUnit.yPos
		moves = self.selectedUnit.moves
		self.moveDict = {}
		self.moveSet = set()
		for move in xrange(moves,0,-1):
			self.findNMovesAway(indexA,indexB,move)

	def findNMovesAway(self,indexA,indexB,n):
		self.count += 1
		boundingBoxMoves = self.findBoundingBoxMoves(indexA,indexB,n)
		diamondMovesGivenSet = self.findDiamondMovesGivenSet(indexA,indexB,n,
			boundingBoxMoves)
		legalMovesForN = diamondMovesGivenSet
		if self.count < 2:
			print boundingBoxMoves
			print legalMovesForN
		for move in legalMovesForN:
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

	def init(self): #initializes the animation
		self.initBoard(25,25,self.width-25,self.height-25)
		self.initUnits()
		#"in-shifted" by 25 to show that program works even if the boundaries
		#are not the edges
		#self.indexA = 0
		#self.indexB = 0
		#self.selected = False
		self.coords = False
		self.adjX = 0
		self.adjY = 0
		self.showUnits = True
		self.selectedUnit = None
		self.player = "blue"
		self.count = 0

	def redrawAll(self): #redraws all
		self.drawBoard()
		if self.showUnits: self.drawUnits()
		#self.drawPosition(self.indexA,self.indexB)

PartialGame().run(30,60)

def testAll():
	pass