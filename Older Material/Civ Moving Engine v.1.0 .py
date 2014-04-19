from Tkinter import *
import random

class Animation(object): #From Kosbie email;expanded sligtly from stock code
    def mousePressed(self, event): pass
    def keyPressed(self, event): pass
    def timerFired(self): pass
    def init(self): pass
    def redrawAll(self): pass
    def mouseReleased(self,event): pass

    def run(self, width=500,height=500):
        root = Tk()
        self.width,self.height = width,height
        self.canvas = Canvas(root, width=width, height=height)
        self.canvas.configure(bd = 0, highlightthickness = 0)
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

class Tile(object):
	tileList = []
	def __init__(self,cx,cy,r,adj60,left,top,adj30,typee="Normal",terrain="Normal"):
		self.cx,self.cy,self.r,self.type,self.terrain = cx,cy,r,typee,terrain
		indexA = int(round((float(cx)-left-adj60)/adj60))
		if indexA%2 == 0:
			indexB = 2*int(round((float(cy)-top-float(top + r))/float(2*(r+adj30))))
		else:
			indexB = (2*int(round((float(cy)-top-float(top+float(2*r+adj30)))/float(2*(r+adj30)))))+1
		self.indexA,self.indexB=indexA,indexB
		Tile.tileList.append(self)

class MoveEngine(Animation):
	def mousePressed(self,event):
		if not(self.selected):
			for tile in Tile.tileList:
				if ((((event.x-tile.cx)**2+(event.y-tile.cy)**2)**.5 <= self.adj60) and
					(self.indexA == tile.indexA) and (self.indexB == tile.indexB)):
					self.selected = True
		elif self.selected:
			for tile in Tile.tileList:
				if (((event.x-tile.cx)**2+(event.y-tile.cy)**2)**.5 <= tile.r):
					self.indexA = tile.indexA
					self.indexB = tile.indexB
					self.selected = False
		#print self.selected

	def keyPressed(self,event):
		if event.keysym == "Left": self.indexA -= 2
		elif event.keysym == "Up": self.indexB -= 1
		elif event.keysym == "Down": self.indexB += 1
		elif event.keysym == "Right": self.indexA += 2
		#print self.indexA,self.indexB

	def drawBoard(self):
	    for tile in Tile.tileList:
	    	cx,cy,r = tile.cx,tile.cy,tile.r
	    	adj60, adj30 = r*(3**.5)/2, r/2
	    	self.canvas.create_polygon(cx,          cy-r,
	                        	   	   cx+adj60,    cy-adj30,
	                          		   cx+adj60,    cy+adj30,
	                          		   cx,          cy+r,
	                          		   cx-adj60,    cy+adj30,
	                          		   cx-adj60,    cy-adj30,
	                         		   fill = "white", outline = "black",
	                          		   width = r/50)#TODO
	    	#self.canvas.create_text(cx,cy,text="%d,%d"%(tile.indexA,tile.indexB))
	    self.canvas.create_rectangle(self.left,self.top,self.right,self.bottom)


	def initBoard(self,left,top,right,bottom,r=-1):
		self.left,self.top,self.right,self.bottom = left,top,right,bottom
	   	self.width,self.height = width,height = abs(left-right),abs(top-bottom)
	   	if r < 0: r = min(width,height)/20
	   	adj60, adj30 = r*(3**.5)/2, r/2.0 #distances corresponding to the 30 and 60
	   	                               #degree sides of the triangle sin the hexagon
	   	self.adj60,self.adj30,self.top,self.left,self.r=adj60,adj30,top,left,r
	   	for colPos1 in xrange(left+int(adj60),right-int(adj60),int(2*adj60)):
	   	    for rowPos1 in xrange(top+r,bottom-r,int(2*(r+adj30))):
	   	        Tile(colPos1,rowPos1,r,adj60,left,top,adj30)
	   	for colPos2 in xrange(left+int(adj60)*2,right-int(adj60)*2,int(2*adj60)):
	   	    for rowPos2 in xrange(top+int(2*r+adj30),bottom-int(2*r+adj30), int(2*(r+adj30))):
	   	        Tile(colPos2,rowPos2,r,adj60,left,top,adj30)

	def drawPosition(self,indexA,indexB):
	    if (indexA%2 != indexB%2): indexA += 1 #NOT self.indexA
	    adj60, adj30 = self.adj60, self.adj30
	    left,top,r = self.left,self.top,self.r
	    cx = float(left + float(adj60))
	    cx += float(adj60)*indexA #LOCAL indexA --> this is why it moves "straight down"
	    cy = float(top + r) if indexB%2 == 0 else float(top+float(2*r+adj30))
	    cy += indexB/2*float(2*(r+adj30))
	    color = "black"
	    if self.selected: color = "yellow"
	    self.canvas.create_oval(cx-5,cy-5,cx+5,cy+5,fill = color)

	def init(self):
		self.initBoard(25,25,self.width-25,self.height-25)
		self.indexA = 0
		self.indexB = 0
		self.selected = False

	def redrawAll(self):
		self.drawBoard()
		self.drawPosition(self.indexA,self.indexB)

MoveEngine().run()