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

def calcDistance(xOne,xTwo,yOne,yTwo):
    return (abs(xTwo-xOne) + abs(yTwo-yOne))

def calcClosestTarget(token, lowers):
    minimum = 9999
    distance = 0
    for lowerToken in lowers:
        if (token.type == 's'):
            if (lowerToken.type == 'p'):
                distance = calcDistance(lowerToken.x,token.x,lowerToken.y,token.y)
        if (token.type == 'p'):
            if (lowerToken.type == 'r'):
                distance = calcDistance(lowerToken.x,token.x,lowerToken.y,token.y)
        if (token.type == 'r'):
            if (lowerToken.type == 's'):
                distance = calcDistance(lowerToken.x,token.x,lowerToken.y,token.y)
        if(distance<minimum):
            minimum = distance
    print(distance)
    return distance
        
            


def calcState(current, uppers, lowers, blocks):
    positions = []
    for i in range(-1,2):
        blocked = False
        if (i==0):
            continue
        if(abs(uppers[current].x+i) > MAX_X):
            continue
        for token in blocks:
            if ((uppers[current].x + i, uppers[current].y) == (token.x,token.y)):
                blocked = True
                break
        if(blocked == False):
            positions.append((uppers[current].x+i,uppers[current].y))
                

    for i in range(-1,2):
        blocked = False
        if(abs(uppers[current].y+i) > MAX_X):
            continue
        if (i==0):
            continue
        for token in blocks:
            if ((uppers[current].x, uppers[current].y + i) == (token.x,token.y)):
                blocked = False
                break
        if(blocked == False):
            positions.append((uppers[current].x,uppers[current].y+i))

    for i in range(-1,2):
        blocked = False
        if((abs(uppers[current].x-i) > MAX_X) or (abs(uppers[current].y + i)>MAX_X)):
            continue
        if (i==0):
            continue
        for token in blocks:
            if ((uppers[current].x - i, uppers[current].y + i) == (token.x,token.y)):
                blocked = False
        if(blocked == False):
            positions.append((uppers[current].x-i,uppers[current].y+i))
    print(positions)
        
    





                


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

                


    
    """for token in dict:
        if(currentToken = token):
            continue
        else if(dict[token].x + dict[token].y + currentToken.x + currentToken.y is in [-1,0,1]):
            if(dict[token].type != 'block'):
                dict[currentToken] = token
                return"""


def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    # TODO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).
    
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


    # Print board to show off function
    board = generate_board_dict(upperTokens,lowerTokens,blockTokens)
    print_board(board)
    print(upperTokens[0].type)
    calcClosestTarget(upperTokens[1],lowerTokens)
    for i in range(len(upperTokens)):
        calcState(i,upperTokens,lowerTokens,blockTokens)
