"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json
import math

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_slide, print_swing
from search.token import Token
from search.cell import Cell

# Max x value for the grid
MAX_X = 4

# Generates a board dictionary in the format of the board printing
# function
def generate_board_dict(uppers,lowers,blocks):
    board_dict = {}
    for upper in uppers:
        board_dict[(upper.x,upper.y)] = f"{upper.type}, u"
    for lower in lowers:
        board_dict[(lower.x,lower.y)] = f"{lower.type}, l"
    for block in blocks:
        board_dict[(block.x,block.y)] = "block"
    return board_dict

# Calculate the manhattan distance between two points
def calcDistance(p1,p2):
    return (abs(p2[0]-p1[0]) + abs(p2[1]-p1[1]))

# Calculates distance to the closest target for a token
# as a 2-tuple (distance, target)
def calcClosestTarget(token, lowers):
    minimum = 9999
    target = None
    for lowerToken in lowers:
        if(whoWins(token.type, lowerToken.type)==1):
            distance = calcDistance((token.x,token.y),(lowerToken.x,lowerToken.y))
            if(distance<minimum):
                minimum = distance
                target = lowerToken
    return (minimum,target)

# Takes two token types, and returns the winner
def whoWins(type1, type2):
    if type1 == 'r':
        if type2 == 's':
            return 1
        if type2 == 'p':
            return -1
    if type1 == 's':
        if type2 == 'p':
            return 1
        if type2 == 'r':
            return -1
    if type1 == 'p':
        if type2 == 'r':
            return 1
        if type2 == 's':
            return -1
    return 0

def calcStates(token, uppers, lowers, blocks, isSwing):
    # States holds an array of (x, y, moveType)
    states = []
    for i in [(-1,1),(0,1),(-1,0),(1,0),(0,-1),(1,-1)]:
        blocked = False
        swing = False
        defeat = 0
        if abs(token.x+i[0]) > MAX_X or abs(token.y+i[1]) > MAX_X:
            continue
        for block in blocks:
            if ((token.x + i[0], token.y + i[1]) == (block.x,block.y)):
                blocked = True
                break
        for lowToken in lowers:
            if ((token.x + i[0], token.y + i[1]) == (lowToken.x,lowToken.y)):
                if (whoWins(token.type,lowToken.type) == -1):
                    defeat = 1
                    break
        if(isSwing == 0):
            for swingToken in uppers:
                if (token.x + i[0], token.y + i[1]) == (swingToken.x, swingToken.y):
                    swing = True
                    savedSwing = swingToken
                    break
        if(defeat == 1):
            continue
        if(blocked == True):
            continue  
        if(swing == True):
            for element in calcStates(savedSwing,uppers,lowers,blocks,1):
                if((element[0],element[1]) == (token.x,token.y)):
                    continue
                states.append((element[0],element[1],"SWING"))
        else:
            states.append((token.x+i[0],token.y+i[1],"SLIDE"))  
    states = list(dict.fromkeys(states))
    return states

# Checks if a certain path will intersect with another path on a specific turn
def isIntersecting(currentTokenPath, allPaths):
    for i in range(len(currentTokenPath)):
        for path in allPaths:
            if (currentTokenPath[i]==path[i]):
                return True
    return False

def fight(uppers, lowers):
    for first in uppers:
        i=0
        for second in range(len(lowers)):
            if (uppers[first].x,uppers[first].y) == (lowers[second].x,lowers[second].y):
                if (uppers[first].type == 'r'):
                    if(lowers[second].type == 's'):
                        lowers[second].kill()
                        lowers.pop(i)
                elif (uppers[first].type == 's'):
                    if(lowers[second].type == 'p'):
                        lowers[second].kill()
                        lowers.pop(i)
                elif (uppers[first].type == 'p'):
                    if(lowers[second].type == 'r'):
                        lowers[second].kill()
                        lowers.pop(second)
        for third in range(len(uppers)):
            if(first==third):
                continue
            if (uppers[first].x,uppers[first].y) == (uppers[third].x,uppers[third].y):
                if (uppers[first].type == 'r'):
                    if(uppers[third].type == 's'):
                        uppers[third].kill()
                        lowers.pop(i)
                elif (uppers[first].type == 's'):
                    if(uppers[third].type == 'p'):
                        uppers[third].kill()
                        lowers.pop(i)
                elif (uppers[first].type == 'p'):
                    if(uppers[third].type == 'r'):
                        uppers[third].kill()
                        lowers.pop(third)

# Uses the A* pathfinding algorithm to find the shortest path
# and returns that path as an array of 3-tuples (x, y, moveType)
def findPath(token, uppers, lowers, blocks):
    # Keep track of open and closed cells
    # Open = search the cell for children
    # Closed = don't search that cell anymore
    openList = []
    closedList = []

    # Make cell for the first position
    start = Cell((token.x,token.y),None,"")
    openList.append(start)

    while len(openList) > 0:
        current = openList[0]
        
        # Remove from open and add to closed
        openList.pop(0)
        closedList.append(current)

        # If closest target has position 0 then path has been found
        closestDistance = calcClosestTarget(Token(current.pos[0],current.pos[1],token.type),lowers)[0]
        if closestDistance == 0:
            # Iterate through parent nodes and add to list
            path = []
            while current != None:
                path.append((current.pos[0],current.pos[1],current.moveType))
                current = current.parent
            return path[::-1]
        
        # Get children from calcStates
        childrenPositions = calcStates(Token(current.pos[0],current.pos[1],token.type),uppers,lowers,blocks,0)
        children = []
        for (x,y,moveType) in childrenPositions:
            children.append(Cell((x,y), current, moveType))
        
        for child in children:
            # If child position is in closed positions, continue
            cont = False
            for closed in closedList:
                if child.pos == closed.pos:
                    cont = True
            if cont:
                continue
            
            # Calculate path costs and heuristics for cell
            child.pathCost = current.pathCost + 1
            child.totalCost = child.pathCost + closestDistance

            # If this pathcost is more expensive than the same positions prev pathcost
            # then continue
            for op in openList:
                if op.pos == child.pos and child.pathCost > op.pathCost:
                    cont=True
            if cont:
                continue
            
            # Add child to list and sort the list
            openList.append(child)
        
        # Sort the open cells list by total cost
        sorted(openList, key=lambda op: op.totalCost)
    # Return empty path if no path found
    return []

# Entrypoint
def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)
    
    # Load in upper, lower and block tokens as seperate arrays (There
    # may be a more compact way to do this)
    upperTokens = []
    lowerTokens = []
    blockTokens = []
    for upperRaw in data['upper']:
        upper = Token(upperRaw[1], upperRaw[2], upperRaw[0])
        upperTokens.append(upper)
    for lowerRaw in data['lower']:
        lower = Token(lowerRaw[1], lowerRaw[2], lowerRaw[0])
        lowerTokens.append(lower)
    for blockRaw in data['block']:
        block = Token(blockRaw[1], blockRaw[2], "b")
        blockTokens.append(block)

    # While targets still exist, move tokens closer and closer
    activeTargets = [x for x in lowerTokens]
    roundCount = 1
    while(len(activeTargets) > 0):
        # Find a path for each upper token
        paths = []
        for token in upperTokens:
            paths.append((token, findPath(token, upperTokens, activeTargets, blockTokens)))
        
        # Move token by one move from the path
        for (token,path) in paths:
            # If no path could be calculated, move token by random direction
            if(len(path) == 0):
                states = calcStates(token, upperTokens, activeTargets, blockTokens, 0)
                print(f"Turn {roundCount}: {states[0][2]} from {(token.x,token.y)} to {(states[0][0],states[0][1])}")
                (token.x,token.y) = (states[0][0],states[0][1])
                continue
            
            # Move token along path
            (token.x,token.y) = (path[1][0],path[1][1])
            print(f"Turn {roundCount}: {path[1][2]} from {(path[0][0],path[0][1])} to {(path[1][0],path[1][1])}")
            if(len(path) == 2):
                target = calcClosestTarget(token,activeTargets)[1]
                activeTargets.remove(target)
        roundCount += 1