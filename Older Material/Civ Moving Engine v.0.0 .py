from Tkinter import *
import random

class Animation(object):
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

class MoveEngine(Animation):
	def mousePressed(self,event):
		print event.x,event.y

	def keyPressed(self,event):
		if event.keysym == "Left": self.indexA -= 2
		elif event.keysym == "Up": self.indexB -= 1
		elif event.keysym == "Down": self.indexB += 1
		elif event.keysym == "Right": self.indexA += 2
		print self.indexA,self.indexB

	def drawHexagon(self,cx,cy,r):
	    height = width = r*2
	    adj60, adj30 = r*(3**.5)/2, r/2
	    self.canvas.create_polygon(cx,          cy-r,
	                        	   cx+adj60,    cy-adj30,
	                          	   cx+adj60,    cy+adj30,
	                          	   cx,          cy+r,
	                          	   cx-adj60,    cy+adj30,
	                          	   cx-adj60,    cy-adj30,
	                         	   fill = "white", outline = "black",
	                          	   width = r/50)#TODO

	def drawBoard(self,left,top,right,bottom,r=-1):
	    width,height = abs(left-right),abs(top-bottom)
	    if r < 0: r = min(width,height)/20
	    adj60, adj30 = r*(3**.5)/2, r/2 #distances corresponding to the 30 and 60
	                                   #degree sides of the triangle sin the hexagon
	    self.adj60,self.adj30,self.top,self.left,self.r=adj60,adj30,top,left,r
	    for colPos1 in xrange(left+int(adj60),right-int(adj60),int(2*adj60)):
	        for rowPos1 in xrange(top+r,bottom-r,int(2*(r+adj30))):
	            self.drawHexagon(colPos1,rowPos1,r)
	    for colPos2 in xrange(left+int(adj60)*2,right-int(adj60)*2,int(2*adj60)):
	        for rowPos2 in xrange(top+int(2*r+adj30),bottom-int(2*r+adj30), int(2*(r+adj30))):
	            self.drawHexagon(colPos2,rowPos2,r)
	    #canvas.create_rectangle(left,top,right,bottom)

	def drawPosition(self,indexA,indexB):
	    if (indexA%2 != indexB%2): indexA += 1 #NOT self.indexA
	    adj60, adj30 = self.adj60, self.adj30
	    left,top,r = self.left,self.top,self.r
	    cx = float(left + float(adj60))
	    cx += float(adj60)*indexA #LOCAL indexA --> this is why it moves "straight down"
	    cy = float(top + r) if indexB%2 == 0 else float(top+float(2*r+adj30))
	    cy += float(indexB/2*float(2*(r+adj30)))
	    self.canvas.create_oval(cx-5,cy-5,cx+5,cy+5,fill = "black")

	def init(self):
	#	self.drawBoard(0,0,self.width,self.height)
	#	self.drawPosition(1,1)
		self.indexA = 0
		self.indexB = 0

	def redrawAll(self):
		self.drawBoard(25,25,self.width-25,self.height-25)
		self.drawPosition(self.indexA,self.indexB)

MoveEngine().run()