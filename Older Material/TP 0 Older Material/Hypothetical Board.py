from Tkinter import *

root = Tk()
canvas = Canvas(root, width=500, height=500)

#def drawHexagon(left, top, right, bottom):
#    height,width = abs(top-bottom),abs(right-left)
#    halfWay,quarterWay,threeFourthsWay = .5,.25,.75
#    lineThickness = ((width+height)/2.0)/((width+height)/float(width)*10) #Change!
#    canvas.create_polygon(left, top+height*halfWay, left+width*quarterWay, 
#        top, left+width*threeFourthsWay, top, right, top+height*halfWay,left+width*threeFourthsWay, 
#        bottom, left+width*quarterWay, bottom, fill = "white", outline = "black", width = lineThickness)

def drawHexagon2(cx,cy,r):
    height = width = r*2
    adj60, adj30 = r*(3**.5)/2, r/2
    canvas.create_polygon(cx,          cy-r,
                          cx+adj60,    cy-adj30,
                          cx+adj60,    cy+adj30,
                          cx,          cy+r,
                          cx-adj60,    cy+adj30,
                          cx-adj60,    cy-adj30,
                          fill = "white", outline = "black",width = r/50)#TODO


def drawBoard(canvas,left,top,right,bottom,r=-1):
    width,height = abs(left-right),abs(top-bottom)
    if r < 0: r = (width+height)/2/(10**(len(str(left))-2)) #radius heuristic
    adj60, adj30 = r*(3**.5)/2, r/2 #distances corresponding to the 30 and 60
                                   #degree sides of the triangle sin the hexagon
    canvas.adj60 = adj60
    canvas.adj30 = adj30
    canvas.top = top
    canvas.left = left
    canvas.r = r
    for colPos1 in xrange(left+int(adj60),right-int(adj60),int(2*adj60)):
        for rowPos1 in xrange(top+r,bottom-r,int(2*(r+adj30))):
            drawHexagon2(colPos1,rowPos1,r)
    for colPos2 in xrange(left+int(adj60)*2,right-int(adj60)*2,int(2*adj60)):
        for rowPos2 in xrange(top+int(2*r+adj30),bottom-int(2*r+adj30), int(2*(r+adj30))):
            drawHexagon2(colPos2,rowPos2,r)
    #canvas.create_rectangle(left,top,right,bottom)


#def drawBoard2(canvas,left,top,right,bottom,radius=-1):
#    width,height = abs(right-left),abs(top-bottom)
#    if radius < 0: radius = ((width+height)/2)/10

def drawPosition(indexA,indexB):
    assert indexA%2 == indexB%2
    adj60, adj30 = canvas.adj60, canvas.adj30
    left,top,r = canvas.left,canvas.top,canvas.r
    cx = left + int(adj60)
    cx += int(adj60)*indexA
    cy = top + r if indexB%2 == 0 else top+int(2*r+adj30)
    cy += indexB/2*int(2*(r+adj30))
    canvas.create_oval(cx-5,cy-5,cx+5,cy+5,fill = "black")

drawBoard(canvas,100,100,400,400)
drawPosition(2 ,0)

canvas.pack()
root.mainloop()