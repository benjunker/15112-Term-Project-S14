#multiple inheritance from team?
#slightly variable expecience to rank up?

import random

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

	def __init__(self,atk,df,team,moves,xPos,yPos,sight,health,
		state="neutral"): #initializes units
		self.atk = atk #attacking power
		self.df = df #defending ability
		#self.type = typee #purpose of unit (ie-attack,build,settle,etc)
		self.team = team #which player/team controls the unit
		#self.mode = mode #mode of attack (if at all) (ie - ground,range,etc)
		self.moves = moves #number of moves per turn
		self.xPos = xPos #current x position --> an index?
		self.yPos = yPos # current y position --> and index?
		self.sight = sight #amount of tiles away, that a unit can "s    ee"
		self.health = health #health remaining
		self.state = state #game state (ie-neutral,fortitified,etc)
		self.defaultMoves = moves #num of moves per turn --> to reset

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
		super(Military,self).__init__(atk,df,team,moves,xPos,yPos,sight,health)
		self.rank = rank #current ability/prowess (normal, elite, or master)
		self.exp = 0 #current amount of experience

	def battleSuccess(self):#determines effectiveness in battle
		luck = random.randint(0,9)#for pmf
		success = Unit.rankDict[self.rank][luck]#gets qualified success
		successNumber = Unit.effectiveDict[success] #quantifies success
		return successNumber

	def battle(self,other): #battle enginge, for military units
		selfSuccess = self.battleSuccess()
		otherSuccess = other.battleSuccess()
		self.attack(other,selfSuccess,otherSuccess)
		other.retaliate(self,selfSuccess,otherSuccess)

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
		if not isinstance(other,Land): assert (False)
		super(Land,self).battle(other)

	def retaliate(self,other,selfSuccess,otherSuccess):
		if isinstance(other,Land):
			super(Land,self).retaliate(other,selfSuccess,otherSuccess)

class Warrior(Land):
	atk = df = moves = sight = 2 #arbitrary

	def __init__(self,team=None,xPos=None,yPos=None,health=100):
		atk,df,moves,sight = Warrior.atk,Warrior.df,Warrior.moves,Warrior.sight
		super(Warrior,self).__init__(atk,df,team,moves,xPos,yPos,sight,health)

	def __str__(self):
		print "atk: " + str(self.atk)
		print "df: " + str(self.df)
		print "moves: " + str(self.moves)
		print "sight: " + str(self.sight)
		print "health: " + str(self.health)
		print "rank: " + str(self.rank)
		print "exp: " + str(self.exp)
		print type(self)
		print "Land: " +  str(isinstance(self,Land))
		print "Military: " + str(isinstance(self,Military))
		print "Unit: " + str(isinstance(self,Unit))
		return ""