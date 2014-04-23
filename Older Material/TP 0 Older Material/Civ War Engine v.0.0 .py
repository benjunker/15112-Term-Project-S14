#magic numbers? --> allowed to use some arbitrary numbers, but comment!!
#find a good way to "normalize" the damage for larger attack/defense values

from Tkinter import *
import random

class Animation(object): #From Kosbie email;expanded slightly from stock code
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

class Unit(object): #generic unit class
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

	def __init__(self,atk,df,typee,team,mode,moves,xPos,yPos,
		state="neutral",health=100,rank="normal"): #initializes units
		self.atk = atk #attacking power
		self.df = df #defending ability
		self.type = typee #purpose of unit (ie-attack,build,settle,etc)
		self.team = team #which player/team controls the unit
		self.mode = mode #mode of attack (if at all) (ie - ground,range,etc)
		self.moves = moves #number of moves per turn
		self.xPos = xPos #current x position
		self.yPos = yPos # current y position
		self.state = state #game state (ie-neutral,fortitified,etc)
		self.health = health #health remaining
		self.rank = rank #current ability/prowess (normal, elite, or master)
		self.exp = 0 #current amount of experience
		self.defaultMoves = moves #no of moves per turn --> to reset

	def battleSuccess(self):#determines effectiveness in battle
		luck = random.randint(0,9)#for pmf
		success = Unit.rankDict[self.rank][luck]#gets qualified success
		successNumber = Unit.effectiveDict[success] #quantifies success
		return successNumber

	def reset(self):
		#to reset moves each turn
		self.moves = self.defaultMoves

class Warrior(Unit): #type of unit: warrior
	atk = 2 #arbitrary
	df = 2 #arbitrary
	typee = "attack"
	mode = "ground"
	moves = 2 #arbitrary

	def __init__(self, team = None, xPos = None, yPos = None):
		atk = Warrior.atk
		df = Warrior.df
		typee = Warrior.typee
		mode = Warrior.mode
		moves = Warrior.moves
		super(Warrior,self).__init__(atk,df,typee,team,mode,moves,xPos,yPos)

class BattleDialogue(Animation): #shows the progression of a series of battles
	def keyPressed(self,event): #advances by keypresses
		if event.keysym == "b": #simulates a battle
			self.battle()
			self.fought = True
		elif event.keysym == "r": #resets
			self.init()

	def init(self): #initilizes dialogue
		self.fought = False
		self.a = Warrior()
		self.b = Warrior()
		self.aPrevious = 100 #previous health --> 100 to start
		self.bPrevious = 100

	def redrawAll(self): #draws dialogue on canvas; coordinates are arbitrary
		self.canvas.create_text(10,0, #dialogue
			text = "press \"b\" to advance or \"r\" to reset",anchor = NW)
		if self.fought:
			self.canvas.create_text(10,25,
				text = "a.health = %d & b.health = %d" % (self.aPrevious,
					self.bPrevious),anchor = NW)#starting health
			self.canvas.create_text(10,50,text = "a just attacked b!",
				anchor = NW)#information
			self.canvas.create_text(10,75,
				text ="a had %d success & b had %d success" % (self.aSuccess,
					self.bSuccess),anchor=NW)#quantified success
			self.canvas.create_text(10,100,
				text ="That is: a was %s & b was %s" % (
					self.reverse[self.aSuccess],self.reverse[self.bSuccess]),
				anchor = NW)#qualified success
			self.canvas.create_text(10,125,
				text ="a dealt %d damage & b retaliated %d damage" % (
					self.damage,self.retaliateDamage),anchor = NW)#damage dealt
			self.canvas.create_text(10,150,
				text ="a now has %d health & b now has %d health" % (
					self.a.health,self.b.health),anchor = NW)#remaining health


	def battle(self):#simulates battle
		self.aPrevious = self.a.health #stores previous health
		self.bPrevious = self.b.health
		self.aSuccess = self.a.battleSuccess() #calculates level of success
		self.bSuccess = self.b.battleSuccess()
		self.reverse = Unit.reverseEffectiveDict
		self.damage = 3*self.a.atk*self.aSuccess - self.b.df*self.bSuccess
		self.retaliateDamage = (3*self.b.atk*self.bSuccess - 
			self.a.df*self.aSuccess)/2 #scalar *3 and /2 are (potentially)
			#temporary, arbitrary heuristics
		self.b.health = self.b.health - self.damage if (
			self.damage > 0) else self.b.health
		self.a.health = self.a.health - self.retaliateDamage if (
			self.retaliateDamage>0) else self.a.health

BattleDialogue().run(350,200)#for correct sized canvas

###############################################################################
###              Older code is below; it resets evey iteration              ###
###                         ignore if you so desire                         ###
###############################################################################

a = Warrior() #older iteration of class warriors
b = Warrior()

def battle(a,b): #older iteration of the class battle funciton
	#a.rank = "master"
	print "To start:",
	print "a.health = %d & b.health = %d" % (a.health,b.health)
	print
	aSuccess = a.battleSuccess()
	bSuccess = b.battleSuccess()
	reverse = Unit.reverseEffectiveDict
	print "a had %d success & b had %d success" % (aSuccess,bSuccess)
	print "That is: a was %s & b was %s" % (reverse[aSuccess],
		reverse[bSuccess])
	print
	damage = 3*a.atk*aSuccess - b.df*bSuccess
	retaliateDamage = (3*b.atk*bSuccess - a.df*aSuccess)/2
	print "a dealt %d damage & b retaliated %d damage" % (damage,
		retaliateDamage)
	print
	b.health = b.health - damage if (damage > 0) else b.health
	a.health = a.health - retaliateDamage if (retaliateDamage>0) else a.health
	print "a now has %d health & b now has %d health" % (a.health,b.health)

#battle(a,b)