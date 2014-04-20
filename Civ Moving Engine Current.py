#more effective search function --> use mouse position as location heruistic
#"dot" "shifts" to the right for larger numbers --> (floating point errors?)
#determine indecies in initBoard! Do not wait to extrapolate in __init__ --> Done!
#Do gross math for efficient mouse click search....

from Tkinter import *
import random

class Animation(object): #From Kosbie email;expanded sligtly from stock code
	def mousePressed(self, event): pass
	def keyPressed(self, event): pass
	def timerFired(self): pass
	def init(self): pass
	def redrawAll(self): pass
	def mouseReleased(self,event): pass #added mouseReleased
	#removed many of the comments
	def run(self, width=500,height=500):
		root = Tk()
		self.width,self.height = width,height
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

class Tile(object): #tiles that make up the board
	tileList = [] #list of all tiles to iterate through
	def __init__(self,cx,cy,r,adj60,left,top,adj30,indexA,indexB,
		typee="Normal", terrain="Normal"): #initializes each tile
		self.cx,self.cy,self.r,self.type,self.terrain = cx,cy,r,typee,terrain
		self.indexA,self.indexB=indexA,indexB #assigns indicies to tiles
		Tile.tileList.append(self)

class MoveEngine(Animation): #basis of the "board" and how things will move
	def mousePressed(self,event):
		if not(self.selected): #select a "unit"
			for tile in Tile.tileList:
				if ((((event.x-tile.cx)**2+(event.y-tile.cy)**2)**.5 <= 
					self.adj60) and 							#.5 for sqrt
					(self.indexA == tile.indexA) and (self.indexB == 
						tile.indexB)):
					self.selected = True
		elif self.selected: #move a "unit"
			for tile in Tile.tileList:
				if (((event.x-tile.cx)**2+(event.y-tile.cy)**2)**.5 <= 
					self.adj60):
					self.indexA = tile.indexA
					self.indexB = tile.indexB
					self.selected = False
		#print self.selected

	def mousePressed(self,event):
		adj60,adj30,r = self.adj60,self.adj30,self.r
		mBlue = ((1.0*r-adj30)/int(adj60)) #slope for blue lines
		mRed = ((1.0*adj30-r)/int(adj60)) #slope for red lines
		#print mBlue
		#see concept "Board With Lines.png" if unclear
		mseX,mseY = event.x,event.y
		yIntBlue = 1

	def keyPressed(self,event): #mainly for testing; moving uses the mouse
		if event.keysym == "Left": self.indexA -= 2 #move the "dot"
		elif event.keysym == "Up": self.indexB -= 1
		elif event.keysym == "Down": self.indexB += 1
		elif event.keysym == "Right": self.indexA += 2
		elif event.keysym == "d": self.coords = not(self.coords) #superimpose
														   #numbers over tiles
		#print self.indexA,self.indexB

	def drawBoard(self): #for each tile object, draws a hexagon
		for tile in Tile.tileList:
			cx,cy,r = tile.cx,tile.cy,tile.r
			adj60, adj30 = r*(3**.5)/2, r/2.0 #30,60,90 triangles have sides of
			#a, a*(3**.5), and 2a. In this case a = r/2.
			self.canvas.create_polygon(cx,          cy-r,
									   cx+adj60,    cy-adj30,
									   #m = (int(adj60)/(r-adj30))
									   cx+adj60,    cy+adj30,
									   cx,          cy+r,
									   #m = (int(adj60)/(adj30-r))
									   cx-adj60,    cy+adj30,
									   cx-adj60,    cy-adj30,
									   fill = "white", outline = "black",
									   width = r/50)#line width heuristic
			if self.coords:self.canvas.create_text(cx,cy,text="%d,%d"%(
				tile.indexA,tile.indexB)) #superimpose numbers
		self.canvas.create_rectangle(self.left,self.top,self.right,self.bottom)
		#bounding rectangle to show what the board actually is

	def initBoard(self,left,top,right,bottom,r=-1): #creates tiles for board
		self.left,self.top,self.right,self.bottom = left,top,right,bottom
		self.width,self.height = width,height = abs(left-right),abs(top-bottom)
		if r < 0: r = min(width,height)/20 #radius heuristic
		adj60, adj30 = int(r*(3**.5)/2), int(r/2.0) #distances corresponding to the sides
			 #opposide the 30 and 60 degree angles of triangles in the hexagons
		print r,adj60,adj30
		self.adj60,self.adj30,self.top,self.left,self.r=adj60,adj30,top,left,r
		indexA = -2
		for colPos1 in xrange(left+int(adj60),right-int(adj60),int(adj60)*2):
			indexB = -2
			indexA += 2
			for rowPos1 in xrange(top+r,bottom-r,int(2*(r+adj30))):
				indexB += 2
				Tile(colPos1,rowPos1,r,adj60,left,top,adj30,indexA,indexB)
		indexA = -1
		for colPos2 in xrange(left+int(adj60)*2,right-int(adj60),
			int(adj60)*2): #easier to iterate every other row, separately
			indexB = -1
			indexA += 2
			for rowPos2 in xrange(top+int(2*r+adj30),bottom-r,
				int(2*(r+adj30))):
				indexB += 2
				Tile(colPos2,rowPos2,r,adj60,left,top,adj30,indexA,indexB)

	def drawPosition(self,indexA,indexB): #draws dot: hypothetical unit
		if (indexA%2 != indexB%2): indexA += 1 #NOT self.indexA
		adj60, adj30 = self.adj60, self.adj30
		left,top,r = self.left,self.top,self.r
		cx = left + int(adj60)
		cx += int(adj60)*indexA #LOCAL indexA
								  #--> this is why it moves "straight down"
								  #(breaks mousePressed, in some cases)
		cy = float(top + r) if indexB%2 == 0 else float(top+float(2*r+adj30))
		cy += indexB/2*float(2*(r+adj30))
		color = "black"
		if self.selected: color = "yellow"
		self.canvas.create_oval(cx-5,cy-5,cx+5,cy+5,fill = color)
		#the dot, which represents a unit, has an arbitrary radius of 5

	def init(self): #initializes the animation
		self.initBoard(25,25,self.width-25,self.height-25,25)
		#"in-shifted" by 25 to show that program works even if the boundaries
		#are not the edges
		self.indexA = 0
		self.indexB = 0
		self.selected = False
		self.coords = False

	def redrawAll(self): #redraws all
		self.drawBoard()
		self.drawPosition(self.indexA,self.indexB)

MoveEngine().run()