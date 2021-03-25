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
def calcClosestTarget(token, lowers):
    minimum = 9999
    distance = 0
    for lowerToken in lowers:
        if (token.type == 's'):
            if (lowerToken.type == 'p'):
                distance = calcDistance((token.x,token.y),(lowerToken.x,lowerToken.y))
        if (token.type == 'p'):
            if (lowerToken.type == 'r'):
                distance = calcDistance((token.x,token.y),(lowerToken.x,lowerToken.y))
        if (token.type == 'r'):
            if (lowerToken.type == 's'):
                distance = calcDistance((token.x,token.y),(lowerToken.x,lowerToken.y))
        if(distance<minimum):
            minimum = distance
    return distance
        
# Calculates all possible movements of a cell and returns a list of new positions
def calcStates(token, uppers, lowers, blocks):
    positions = []
    for i in range(-1,2):
        blocked = False
        if (i==0):
            continue
        if(abs(token.x+i) > MAX_X):
            continue
        for block in blocks:
            if ((token.x + i, token.y) == (block.x,block.y)):
                blocked = True
                break
        if(blocked == False):
            positions.append((token.x+i,token.y))   
    for i in range(-1,2):
        blocked = False
        if(abs(token.y+i) > MAX_X):
            continue
        if (i==0):
            continue
        for block in blocks:
            if ((token.x, token.y + i) == (block.x,block.y)):
                blocked = True
                break
        if(blocked == False):
            positions.append((token.x,token.y+i))
    for i in range(-1,2):
        blocked = False
        if((abs(token.x-i) > MAX_X) or (abs(token.y + i)>MAX_X)):
            continue
        if (i==0):
            continue
        for block in blocks:
            if ((token.x - i, token.y + i) == (block.x,block.y)):
                blocked = True
                break
        if(blocked == False):
            positions.append((token.x-i,token.y+i))
    return positions
        

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
# and returns that path as an array
def findPath(token, uppers, lowers, blocks):
    # Keep track of open and closed cells
    # Open = search the cell for children
    # Closed = don't search that cell anymore
    openList = []
    closedList = []

    # Make cell for the first position
    start = Cell((token.x,token.y),None)
    openList.append(start)

    while len(openList) > 0:
        current = openList[0]
        
        # Remove from open and add to closed
        openList.pop(0)
        closedList.append(current)

        # If closest target has position 0 then path has been found
        closestDistance = calcClosestTarget(Token(current.pos[0],current.pos[1],token.type),lowers)
        if closestDistance == 0:
            # Iterate through parent nodes and add to list
            path = []
            while current != None:
                path.append(current.pos)
                current = current.parent
            print("Path found!")
            return path[::-1]
        
        # Get children 
        childrenPositions = calcStates(Token(current.pos[0],current.pos[1],token.type),uppers,lowers,blocks)
        children = []
        for pos in childrenPositions:
            children.append(Cell(pos, current))
        
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
    print("Couldn't find path")
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

    # find a path for each upper token
    paths = []
    for token in upperTokens:
        paths.append(findPath(token, upperTokens, lowerTokens, blockTokens))
    for path in paths:
        print(path)